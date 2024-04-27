from .db import db, environment, SCHEMA, add_prefix_for_prod
# Import libraries


class Stock(db.Model):
    __tablename__ = 'stocks'

    if environment == "production":
        __table_args__ = {'schema': SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False, unique=True)

    watchlist_stocks = db.relationship('WatchlistStock', back_populates='stock', cascade='all, delete-orphan')

    patterns = db.relationship('Pattern', back_populates='stock', cascade='all, delete-orphan')

    stock_news = db.relationship('StockNews', back_populates='stock', cascade='all, delete-orphan')


    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
        }
    
    def to_dict_watchlist(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'watchlist_stocks': [watchlist_stock.to_dict() for watchlist_stock in self.watchlist_stocks],
        }
    
    def to_dict_pattern(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'patterns': [pattern.to_dict_self() for pattern in self.patterns],
        }
    
    def to_dict_stock_news(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'stock_news': [stock_news.to_dict_news() for stock_news in self.stock_news],
        }
    
    def to_dict_symbol(self):
        return {
            'symbol': self.symbol,
        }
