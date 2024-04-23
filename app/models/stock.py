from .db import db, environment, SCHEMA, add_prefix_for_prod
# Import libraries
import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from urllib.request import urlopen, Request
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import date
from timedelta import Timedelta 
from datetime import datetime


class Stock(db.Model):
    __tablename__ = 'stocks'

    if environment == "production":
        __table_args__ = {'schema': SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False, unique=True)

    watchlist_stocks = db.relationship('WatchlistStock', back_populates='stock', cascade='all, delete-orphan')



    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
        }
    
    def to_dict_watchlist(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
        }
