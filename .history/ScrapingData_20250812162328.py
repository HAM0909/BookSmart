from bs4 import BeautifulSoup
import requests

url = 'https://books.toscrape.com/catalogue/page-1.html'

response = requests.get(url)

soup = BeautifulSoup(response.text, 'html')


