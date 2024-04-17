from app.models import db, Stock, environment, SCHEMA
from sqlalchemy.sql import text
import csv

def seed_stocks():
    with open('app/seeds/Stocks.csv', 'r') as file:
        csvreader = csv.reader(file)
        for stock in csvreader:
            new_stock = Stock(
                symbol = (stock[0])
            )
            db.session.add(new_stock)
            db.session.commit()

def undo_stocks():
    if environment == "production":
        db.session.execute(f"TRUNCATE table {SCHEMA}.stocks RESTART IDENTITY CASCADE;")
    else:
        db.session.execute(text("DELETE FROM stocks"))
    db.session.commit()
