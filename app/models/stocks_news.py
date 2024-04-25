from .db import db, environment, SCHEMA

class StockNews(db.Model):
    __tablename__ = 'stock_news'

    if environment == "production":
        __table_args__ = {'schema': SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'), nullable=False)

    stock = db.relationship('Stock', back_populates='stock_news')
    news = db.relationship('News', back_populates='stock_news')

    def to_dict_self(self):
        return {
            'id': self.id,
            'stock_id': self.stock_id,
            'news_id': self.news_id,
        }
    
    def to_dict_stock(self):
        return {
            'id': self.id,
            'stock_id': self.stock_id,
            'news_id': self.news_id,
            'stock': self.stock.to_dict(),
        }
    
    def to_dict_news(self):
        return {
            'id': self.id,
            'stock_id': self.stock_id,
            'news_id': self.news_id,
            'news': self.news.to_dict(),
        }
    
    def to_dict_stock_news(self):
        return {
            'id': self.id,
            'stock_id': self.stock_id,
            'news_id': self.news_id,
            'stock': self.stock.to_dict(),
            'news': self.news.to_dict(),
        }
