from newsapi import NewsApiClient

newsapi = NewsApiClient(api_key='2258fbb914d84a90a4047fb59c2c84d8')

def get_headlines(ticker):
    query = f"{ticker} stock"
    res = newsapi.get_everything(q=query, language='en', sort_by='publishedAt', page_size=5)
    return [article['title'] for article in res['articles']]
