from .db import db, environment, SCHEMA

_unique_pattern = db.UniqueConstraint(
    'stock_id', 'pattern_name', 'sentiment', 'timeframe', 'milliseconds',
    name='uq_patterns_stock_pattern_sentiment_timeframe_ms'
)

class Pattern(db.Model):
    __tablename__ = 'patterns'

    if environment == "production":
        __table_args__ = (_unique_pattern, {'schema': SCHEMA})
    else:
        __table_args__ = (_unique_pattern,)

    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False, index=True)
    date = db.Column(db.DateTime, nullable=False)
    milliseconds = db.Column(db.BigInteger, nullable=False)
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
            'date': self.date.strftime('%Y-%m-%d'),
            'milliseconds': self.milliseconds,
            'pattern_name': self.pattern_name,
            'sentiment': self.sentiment,
            'value': self.value,
            'timeframe': self.timeframe,
            'latest_price': self.latest_price,
        }

    def to_dict_stock(self):
        # Uses the `stock` relationship instead of a fresh query - when
        # called from a route that already loaded that Stock (as every
        # caller today does), this is a session identity-map hit, not a
        # new SELECT per pattern.
        return {
            'id': self.id,
            'stock_id': self.stock_id,
            'date': self.date.strftime('%Y-%m-%d'),
            'milliseconds': self.milliseconds,
            'pattern_name': self.pattern_name,
            'sentiment': self.sentiment,
            'value': self.value,
            'timeframe': self.timeframe,
            'latest_price': self.latest_price,
            'stock': self.stock.to_dict_symbol(),
        }
