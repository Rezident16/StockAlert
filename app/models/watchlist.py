from .db import db, environment, SCHEMA, add_prefix_for_prod

watchlist_stocks = db.Table('watchlist_stocks',
    db.Column('watchlist_id', db.Integer, db.ForeignKey('watchlists.id'), primary_key=True),
    db.Column('stock_id', db.Integer, db.ForeignKey('stocks.id'), primary_key=True)
)

class WatchList(db.Model):
    __tablename__ = 'watchlists'

    if environment == "production":
        __table_args__ = {'schema': SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('users.id')), nullable=False)
    stocks = db.relationship('Stock', secondary=watchlist_stocks, backref=db.backref('watchlists', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
        }
    
    def to_dict_stocks(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'stocks': [stock.to_dict() for stock in self.stocks]
        }
