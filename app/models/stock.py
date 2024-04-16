from .db import db, environment, SCHEMA, add_prefix_for_prod
from .watchlist import watchlist_stocks

class Stock(db.Model):
    __tablename__ = 'stocks'

    if environment == "production":
        __table_args__ = {'schema': SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False, unique=True)

    watchlists = db.relationship('WatchList', secondary=watchlist_stocks, backref=db.backref('stocks', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
        }
    
    def to_dict_watchlist(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'watchlists': [watchlist.to_dict() for watchlist in self.watchlists]
        }
