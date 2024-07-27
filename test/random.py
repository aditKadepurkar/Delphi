import requests
from bs4 import BeautifulSoup

# Send a GET request to the website you want to scrape
url = "https://example.com"
response = requests.get(url)

# Create a BeautifulSoup object to parse the HTML content
soup = BeautifulSoup(response.content, "html.parser")

# Find and extract the desired data from the HTML
# For example, let's extract all the links on the page
links = soup.find_all("a")
for link in links:
    print(link.get("href"))