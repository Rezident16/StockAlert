from .db import db, environment, SCHEMA
from .stock import Stock

class Pattern(db.Model):
    __tablename__ = 'patterns'

    if environment == "production":
        __table_args__ = {'schema': SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    date = db.Column(db.String, nullable=False)
    milliseconds = db.Column(db.String, nullable=False)
    pattern_name = db.Column(db.String(150), nullable=False)
    sentiment = db.Column(db.String(150), nullable=False)
    value = db.Column(db.Integer, nullable=False)
    timeframe = db.Column(db.String(150), nullable=False)
    latest_price = db.Column(db.Float, nullable=False)

    stock = db.relationship('Stock', back_populates='patterns')

    def to_dict_self(self):
        return {
            'id': self.id,
            'stock_id': self.stock_id,
            'date': self.date,
            'milliseconds': self.milliseconds,
            'pattern_name': self.pattern_name,
            'sentiment': self.sentiment,
            'value': self.value,
            'timeframe': self.timeframe,
            'latest_price': self.latest_price,
        }
    
    def to_dict_stock(self):
        stock = Stock.query.get(self.stock_id)
        return {
            'id': self.id,
            'stock_id': self.stock_id,
            'date': self.date,
            'milliseconds': self.milliseconds,
            'pattern_name': self.pattern_name,
            'sentiment': self.sentiment,
            'value': self.value,
            'timeframe': self.timeframe,
            'latest_price': self.latest_price,
            'stock': stock.to_dict_symbol(),
        }
