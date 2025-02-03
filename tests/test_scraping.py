import pytest
from main import scrape_price
from bs4 import BeautifulSoup

def test_scrape_price():
    # Mock HTML response
    html = """
    <html>
        <body>
            <span id="lblPrice">100.00</span>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, 'html.parser')
    price_span = soup.find('span', id='lblPrice')
    assert price_span is not None
    assert price_span.text.strip() == "100.00"
