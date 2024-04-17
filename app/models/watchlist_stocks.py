from .db import db, environment, SCHEMA, add_prefix_for_prod

class WatchlistStock(db.Model):
    __tablename__ = 'watchlist_stocks'

    if environment == "production":
        __table_args__ = {'schema': SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('stocks.id')), nullable=False)
    watchlist_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('watchlists.id')), nullable=False)

    watchlist = db.relationship('WatchList', back_populates='watchlist_stocks')
    stock = db.relationship('Stock', back_populates='watchlist_stocks')
    
    def to_dict(self):
        return {
            'id': self.id,
            'stock_id': self.stock_id,
            'watchlist_id': self.watchlist_id,
        }
