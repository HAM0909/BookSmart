from bs4 import BeautifulSoup
import requests
from selenium import webdriver.selenium.

url = 'https://books.toscrape.com/catalogue/page-1.html'

response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')

books_data= []




