from .db import db, environment, SCHEMA

_unique_news = db.UniqueConstraint('news_id', 'stock_id', name='uq_news_news_id_stock_id')

class News(db.Model):
    __tablename__ = 'news'

    if environment == "production":
        __table_args__ = (_unique_news, {'schema': SCHEMA})
    else:
        __table_args__ = (_unique_news,)

    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.BigInteger, nullable=False, index=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False, index=True)
    author = db.Column(db.String, nullable=False)
    headline = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    sentiment = db.Column(db.String, nullable=False)
    probability = db.Column(db.Float, nullable=False)
    url = db.Column(db.String, nullable=False)
    images = db.Column(db.JSON, nullable=True)
    source = db.Column(db.String, nullable=False)
    summary = db.Column(db.String, nullable=False)
    symbols = db.Column(db.JSON, nullable=True)

    stock_news = db.relationship('StockNews', back_populates='news', cascade='all, delete-orphan')

    def to_dict_self(self):
        return {
            'id': self.id,
            'news_id': self.news_id,
            'stock_id': self.stock_id,
            'author': self.author,
            'headline': self.headline,
            'created_at': self.created_at.isoformat(),
            'sentiment': self.sentiment,
            'probability': self.probability,
            'url': self.url,
            'images': self.images,
            'source': self.source,
            'summary': self.summary,
            'symbols': self.symbols
        }

    def to_dict_stock_news(self):
        return {
            'id': self.id,
            'news_id': self.news_id,
            'stock_id': self.stock_id,
            'author': self.author,
            'headline': self.headline,
            'created_at': self.created_at.isoformat(),
            'sentiment': self.sentiment,
            'probability': self.probability,
            'url': self.url,
            'images': self.images,
            'source': self.source,
            'summary': self.summary,
            'stock_news': [stock_news.to_dict_stock() for stock_news in self.stock_news],
        }
