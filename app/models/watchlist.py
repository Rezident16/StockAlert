from .db import db, environment, SCHEMA, add_prefix_for_prod

class WatchList(db.Model):
    __tablename__ = 'watchlists'

    if environment == "production":
        __table_args__ = {'schema': SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('users.id')), nullable=False)

    watchlist_stocks = db.relationship('WatchlistStock', back_populates='watchlist', cascade='all, delete-orphan')
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
        }
    
    def to_dict_stocks(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
        }
