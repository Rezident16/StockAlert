import requests
from bs4 import BeautifulSoup


class FinvizClient:
    """Scrapes the key/value fundamentals table off a Finviz quote page."""

    BASE_URL = 'https://finviz.com/quote.ashx'
    HEADERS = {'User-Agent': 'Mozilla/5.0'}

    def get_stock_data(self, ticker):
        response = requests.get(self.BASE_URL, headers=self.HEADERS, params={'t': ticker}, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        data = {}
        for row in soup.find_all('tr', class_='table-dark-row'):
            cells = row.find_all('td')
            # Finviz splits its data into two columns per pair - one for the
            # key and one for the value - so step through two cells at a time.
            for i in range(0, len(cells), 2):
                key = cells[i].text.strip()
                value = cells[i + 1].text.strip()
                data[key] = value

        return data
