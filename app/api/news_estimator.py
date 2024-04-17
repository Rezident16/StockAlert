# from transformers import AutoTokenizer, AutoModelForSequenceClassification
# import torch
# from typing import Tuple
# from alpaca_trade_api import REST
# from dotenv import load_dotenv

# import os
# device = "cuda:0" if torch.cuda.is_available() else "cpu"

# tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
# model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert").to(device)
# labels = ["positive", "negative", "neutral"]


# load_dotenv()
# API_KEY = os.getenv("API_KEY")
# API_SECRET = os.getenv("API_SECRET")
# BASE_URL = os.getenv("BASE_URL")

# ALPACA_CREDS = {
#     "API_KEY":API_KEY, 
#     "API_SECRET": API_SECRET, 
#     "PAPER": True
# }

# def estimate_sentiment(stocks):
#     api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)


#     if news:
#         tokens = tokenizer(news, return_tensors="pt", padding=True).to(device)

#         result = model(tokens["input_ids"], attention_mask=tokens["attention_mask"])[
#             "logits"
#         ]
#         result = torch.nn.functional.softmax(torch.sum(result, 0), dim=-1)
#         probability = result[torch.argmax(result)]
#         sentiment = labels[torch.argmax(result)]
#         return probability, sentiment
#     else:
#         return 0, labels[-1]


# if __name__ == "__main__":
#     tensor, sentiment = estimate_sentiment(['markets responded negatively to the news!','traders were displeased!'])
#     print(tensor, sentiment)
#     print(torch.cuda.is_available())


# Import libraries
import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from urllib.request import urlopen, Request
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import date
import time
import urllib.request



# Parameters 
def get_response(url):
    while True:
        try:
            response = urllib.request.urlopen(url)
            return response
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(5) 
            else:
                raise 

def get_sentiment(ticker):

    finwiz_url = 'https://finviz.com/quote.ashx?t='
    news_tables = {}

    url = finwiz_url + ticker
    req = Request(url=url, headers={'user-agent': 'Mozilla/5.0'})
    resp = get_response(req)    
    html = BeautifulSoup(resp, features="lxml")
    news_table = html.find(id='news-table')
    news_tables[ticker] = news_table

    parsed_news = []
    for file_name, news_table in news_tables.items():
        for x in news_table.findAll('tr'):
            if x and x.a:
                text = x.a.get_text() 
                date_scrape = x.td.text.split()
                if len(date_scrape) == 1:
                    time_scrape = date_scrape[0]
            
                else:
                    date = date_scrape[0]
                    time_scrape = date_scrape[1]
                
                ticker = file_name.split('_')[0]
            
                parsed_news.append([ticker, date, time_scrape, text])
    analyzer = SentimentIntensityAnalyzer()

    columns = ['Ticker', 'Date', 'Time', 'Headline']
    news = pd.DataFrame(parsed_news, columns=columns)

    scores = news['Headline'].apply(analyzer.polarity_scores).tolist()

    df_scores = pd.DataFrame(scores)
    news = news.join(df_scores, rsuffix='_right')





    unique_ticker = news['Ticker'].unique().tolist()
    news_dict = {name: news.loc[news['Ticker'] == name] for name in unique_ticker}

    values = []
    
    if ticker in news_dict:
        dataframe = news_dict[ticker]
        dataframe = dataframe.set_index('Ticker')
        dataframe = dataframe.drop(columns = ['Headline'])
        
        mean = round(dataframe['compound'].mean(), 2)
        values.append(mean)
        
        df = pd.DataFrame(list(zip(ticker, values)), columns =['Ticker', 'Mean Sentiment']) 
        df = df.set_index('Ticker')
        df = df.sort_values('Mean Sentiment', ascending=False)
        return mean
    else:
        print(f"No news found for {ticker}")
        return None
