import re
from datetime import datetime, timedelta

import torch
from bs4 import BeautifulSoup
from transformers import BertTokenizer, BertForSequenceClassification, pipeline

from .alpaca_client import AlpacaClient, DATE_FORMAT
from ..news import News
from ..stock import Stock
from ..db import db


class NewsSentimentAnalyzer:
    """
    Fetches recent news for a stock, scores it with FinBERT, and stores new
    articles + their sentiment in the DB (emitting a socket event per new
    article). The FinBERT model is loaded lazily on first use rather than
    at import time, since most requests never touch sentiment analysis and
    importing this module happens on every app boot/worker start.

    A single article often covers multiple tickers with different (even
    opposite) sentiment per ticker - scoring the whole headline/summary
    once and stamping that one result on every mentioned symbol would get
    that wrong. When an article covers more than one symbol, this looks
    for paragraphs in the full article body that actually mention a given
    stock - by ticker or by its Stock.name, since articles often refer to
    a company by name rather than symbol - and scores just those; if
    neither matches anywhere, it falls back to whole-article sentiment,
    same as a single-symbol article always gets.
    """

    MODEL_NAME = 'yiyanghkust/finbert-tone'
    NEWS_LOOKBACK_DAYS = 7

    _nlp_pipeline = None

    def __init__(self, alpaca_client=None):
        self.alpaca_client = alpaca_client or AlpacaClient()

    @classmethod
    def _get_pipeline(cls):
        if cls._nlp_pipeline is None:
            device = "mps" if torch.backends.mps.is_available() else ("cuda:0" if torch.cuda.is_available() else "cpu")
            finbert = BertForSequenceClassification.from_pretrained(cls.MODEL_NAME, num_labels=3)
            tokenizer = BertTokenizer.from_pretrained(cls.MODEL_NAME)
            cls._nlp_pipeline = pipeline("sentiment-analysis", model=finbert, tokenizer=tokenizer, device=device)
        return cls._nlp_pipeline

    def analyze(self, stock):
        """Fetch + score + store news for `stock` (a Stock model instance). Returns [{content, sentiment, probability}] scored specifically for `stock`."""
        news = self._fetch_news(stock)
        if not news:
            return []
        scores = self._store_news(news)
        return [
            {'content': article, 'sentiment': scores[key][0], 'probability': scores[key][1]}
            for article in news
            if (key := (article.id, stock.symbol)) in scores
        ]

    def _fetch_news(self, stock):
        today = datetime.now().date()
        week_prior = today - timedelta(days=self.NEWS_LOOKBACK_DAYS)
        return self.alpaca_client.get_news(stock.symbol, start=week_prior.strftime(DATE_FORMAT), end=today.strftime(DATE_FORMAT))

    def _store_news(self, news_list):
        """
        Batches the Stock/News lookups instead of querying per symbol per
        article - with K articles averaging M symbols each, a naive
        approach does K*M*2 individual queries; this does 2 total,
        regardless of size. Returns {(news_id, symbol): (sentiment,
        probability)} for every symbol across every article, whether newly
        scored just now or already stored from an earlier run.
        """
        from app.sockets.news import news_namespace
        from sqlalchemy.exc import IntegrityError

        all_symbols = {symbol for article in news_list for symbol in article.symbols}
        all_news_ids = {article.id for article in news_list}

        stocks_by_symbol = {s.symbol: s for s in Stock.query.filter(Stock.symbol.in_(all_symbols))}
        existing_rows = {
            (n.news_id, n.stock_id): (n.sentiment, n.probability)
            for n in News.query.filter(News.news_id.in_(all_news_ids))
        }

        scores = {}
        # The whole-article fallback score, computed lazily at most once
        # per article regardless of how many symbols end up needing it.
        fallback_cache = {}

        for article in news_list:
            for symbol in article.symbols:
                stock = stocks_by_symbol.get(symbol)
                if stock is None:
                    continue

                existing = existing_rows.get((article.id, stock.id))
                if existing is not None:
                    scores[(article.id, symbol)] = existing
                    continue

                sentiment, probability = self._score_for_symbol(article, stock, fallback_cache)
                scores[(article.id, symbol)] = (sentiment, probability)
                existing_rows[(article.id, stock.id)] = (sentiment, probability)

                news_instance = self._build_news(article, stock, sentiment, probability)
                db.session.add(news_instance)
                try:
                    # Commit per row (not batched): the in-memory dedup
                    # above only catches duplicates within this one fetch.
                    # Real-world API pagination can still return the same
                    # article twice across separate fetches at a page
                    # boundary - the DB's unique constraint is the actual
                    # source of truth, so a conflict here just means
                    # someone else already stored it; skip and move on
                    # instead of failing the whole batch.
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                    continue
                news_namespace.emit('news', news_instance.to_dict_stock_news(), namespace='/news')

        return scores

    def _score_for_symbol(self, article, stock, fallback_cache):
        segment = self._stock_segment(article, stock)
        if segment:
            return self._run_finbert(segment)
        if article.id not in fallback_cache:
            fallback_cache[article.id] = self._run_finbert(article.summary or article.headline)
        return fallback_cache[article.id]

    # BERT's hard limit; the tokenizer's own model_max_length isn't
    # reliably set for this checkpoint, so truncation=True alone doesn't
    # actually cap it here - pass max_length explicitly too.
    MAX_TOKENS = 512

    def _run_finbert(self, text):
        result = self._get_pipeline()(text, truncation=True, max_length=self.MAX_TOKENS)
        return result[0]['label'], result[0]['score']

    def _stock_segment(self, article, stock):
        """Paragraphs from the full article body that mention `stock` by ticker or by name, or None if there's nothing worth isolating."""
        if not article.content or len(article.symbols) <= 1:
            # Single-symbol article - whole-article sentiment is already
            # correct, no need for the more expensive per-paragraph pass.
            return None
        pattern = self._stock_pattern(stock)
        matches = [p for p in self._paragraphs(article.content) if pattern.search(p)]
        return ' '.join(matches) if matches else None

    @staticmethod
    def _stock_pattern(stock):
        terms = [stock.symbol] + ([stock.name] if stock.name else [])
        alternation = '|'.join(re.escape(term) for term in terms)
        return re.compile(rf'(?<![A-Za-z0-9])(?:{alternation})(?![A-Za-z0-9])', re.IGNORECASE)

    @staticmethod
    def _paragraphs(html):
        soup = BeautifulSoup(html, 'html.parser')
        return [text for tag in soup.find_all(['p', 'li']) if (text := tag.get_text(strip=True))]

    @staticmethod
    def _build_news(article, stock, sentiment, probability):
        return News(
            news_id=article.id,
            stock_id=stock.id,
            author=article.author,
            headline=article.headline,
            created_at=article.created_at,
            sentiment=sentiment,
            probability=probability,
            url=article.url,
            images=article.images,
            source=article.source,
            summary=article.summary,
            symbols=article.symbols,
        )
