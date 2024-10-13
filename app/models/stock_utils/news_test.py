# import torch
# from transformers import BertTokenizer, BertForSequenceClassification, pipeline

# # Load pre-trained FinBERT model and tokenizer
# finbert = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone', num_labels=3)
# tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-tone')

# # Check if GPU is available and set the device accordingly
# device = 0 if torch.cuda.is_available() else -1

# # Create a pipeline for sentiment analysis with the specified device
# nlp = pipeline("sentiment-analysis", model=finbert, tokenizer=tokenizer, device=device)

# # List of sentences to analyze
# sentences = "there is a shortage of capital, and we need extra financing growth is strong and we have plenty of liquidity there are doubts about our finances, profits are flat"


# # Perform sentiment analysis
# results = nlp(sentences)
# print(results[0]["label"])
# print(results[0]["score"])




from datetime import datetime, timedelta
from torch import device
from transformers import BertTokenizer, BertForSequenceClassification, pipeline
from dateutil.relativedelta import relativedelta
import torch
from alpaca_trade_api import REST, TimeFrame, TimeFrameUnit
from dotenv import load_dotenv
import os
from flask import current_app
from bs4 import BeautifulSoup

### Use for sentiment analysis on a news article ###
# Set the device to "cuda:0" if CUDA is available, otherwise use the CPU
device = "cuda:0" if torch.cuda.is_available() else "cpu"

# Using Transformers to analize news sentiment
# https://huggingface.co/yiyanghkust/finbert-tone
finbert = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone', num_labels=3)
tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-tone')
nlp = pipeline("sentiment-analysis", model=finbert, tokenizer=tokenizer, device=device)


load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BASE_URL = os.getenv("BASE_URL")

ALPACA_CREDS = {
    "API_KEY":API_KEY, 
    "API_SECRET": API_SECRET, 
}

api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)


# NEWS FUNCTIONS

DATE_FORMAT = '%Y-%m-%d'

# Main function to fetch the news and estimate the sentiment


# Fetch news from the Alpaca API
def fetch_news():
    today = datetime.now().date()
    week_prior = today - timedelta(days=14)
    return api.get_news("AAPL", end=today.strftime(DATE_FORMAT), start=week_prior.strftime(DATE_FORMAT), include_content=True)




news = fetch_news()
for news_item in news:
    soup = BeautifulSoup(news_item.content, 'html.parser')
    paragraphs = soup.find_all('p')
    
    relevant_content = ""
    for paragraph in paragraphs:
        text = paragraph.get_text()
        if "AAPL" in text or "Apple" in text:
            relevant_content += text + "\n"
    
    print(relevant_content)
    result = nlp(relevant_content.strip())
    print(result)
    break
# print(news)



"""
for news_item in news:
    content = news_item.content
    content_list = content.split("<p><strong>")
    return_content = ""
    for item in content_list:
        # Add back the <strong> tag to the first item if it was split
        item = "<p><strong>" + item

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(item, 'html.parser')
        
        # Extract and print the text content, removing all HTML tags
        text_content = soup.get_text()
        
        # Check if "TSLA" or "Tesla" is in the text content
        if "TSLA" in text_content or "Tesla" in text_content:
            return_content += text_content + "\n"
    
    print(return_content)
    break
"""

device = "mps" if torch.backends.mps.is_available() else ("cuda:0" if torch.cuda.is_available() else "cpu")
print(device)
