from datetime import datetime, timedelta

import torch
from transformers import BertTokenizer, BertForSequenceClassification, pipeline

from .alpaca_client import AlpacaClient, DATE_FORMAT
from ..news import News
from ..stock import Stock
from ..db import db


class NewsSentimentAnalyzer:
    """
    Fetches recent news for a stock, scores each article with FinBERT, and
    stores new articles + their sentiment in the DB (emitting a socket event
    per new article). The FinBERT model is loaded lazily on first use rather
    than at import time, since most requests never touch sentiment analysis
    and importing this module happens on every app boot/worker start.
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
        """Fetch + score + store news for `stock` (a Stock model instance). Returns the list of {content, sentiment, probability} dicts scored."""
        news = self._fetch_news(stock)
        if not news:
            return []
        news_and_sentiment = self._score_news(news)
        self._store_news(news_and_sentiment)
        return news_and_sentiment

    def _fetch_news(self, stock):
        today = datetime.now().date()
        week_prior = today - timedelta(days=self.NEWS_LOOKBACK_DAYS)
        return self.alpaca_client.get_news(stock.symbol, start=week_prior.strftime(DATE_FORMAT), end=today.strftime(DATE_FORMAT))

    def _score_news(self, news):
        pipeline_ = self._get_pipeline()
        news_and_sentiment = []
        for text in news:
            content = text.summary if text.summary else text.headline
            result = pipeline_(content)
            news_and_sentiment.append({
                'content': text,
                'probability': result[0]['score'],
                'sentiment': result[0]['label'],
            })
        return news_and_sentiment

    def _store_news(self, news_and_sentiment):
        from app.sockets.news import news_namespace
        for news_obj in news_and_sentiment:
            for symbol in news_obj['content'].symbols:
                stock = Stock.query.filter_by(symbol=symbol).first()
                if stock is None:
                    continue
                existing_news = News.query.filter_by(news_id=news_obj['content'].id, stock_id=stock.id).first()
                if existing_news is None:
                    news_instance = self._build_news(news_obj, stock)
                    db.session.add(news_instance)
                    news_namespace.emit('news', news_instance.to_dict_stock_news(), namespace='/news')
        db.session.commit()

    @staticmethod
    def _build_news(news_obj, stock):
        content = news_obj['content']
        return News(
            news_id=content.id,
            stock_id=stock.id,
            author=content.author,
            headline=content.headline,
            created_at=str(content.created_at),
            sentiment=news_obj['sentiment'],
            probability=news_obj['probability'],
            url=content.url,
            images=content.images,
            source=content.source,
            summary=content.summary,
            symbols=content.symbols,
        )
