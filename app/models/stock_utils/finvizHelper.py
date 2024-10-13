import requests
from bs4 import BeautifulSoup

def get_finviz_data(ticker):
    # ticker = "AAPL"
    url = f'https://finviz.com/quote.ashx?t={ticker}'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    
    soup = BeautifulSoup(response.text, 'html.parser')

    data = {}
    for row in soup.find_all('tr', class_='table-dark-row'):
        cells = row.find_all('td')
        # print(cells[0].text)
        # print(cells[1].text)
        # Finviz splits their data into two columns - one for the key and one for the value
        # For that reason we would need to iterate over the cells with two steps
        for i in range(0, len(cells), 2):
            key = cells[i].text.strip()
            value = cells[i + 1].text.strip()
            data[key] = value

    return data


# get_finviz_data("AAPL")
