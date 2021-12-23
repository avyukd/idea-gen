from core import UserType, Idea, Screener
from typing import List
import requests 
import bs4
import yfinance as yf

BASE_URL = "http://openinsider.com/latest-cluster-buys"
FORBIDDEN_KEYWORDS = ["pharma", "bio", "hold", "fund", "acq"]
class InsiderScreener():
    def __init__(self, cluster_threshold = 3, minimum_buy = 1000000) -> None:
        self.cluster_threshold = cluster_threshold
        self.minimum_buy = minimum_buy
    
    def getIdeas(self) -> List[Idea]:
        r = requests.get(BASE_URL)
        soup = bs4.BeautifulSoup(r.text, "html.parser")
        table = soup.find("table", {"class": "tinytable"})
        rows = table.find_all("tr")
        insider_buys = []
        for row in rows:
            cols = row.find_all("td")
            cols = [ele.text.strip() for ele in cols]
            if len(cols) > 0:
                company_and_industry = cols[4] + cols[5]
                if not any([x in company_and_industry for x in FORBIDDEN_KEYWORDS]):
                    
                    filing_timestamp = cols[1]
                    trade_date = cols[2]
                    ticker = cols[3]
                    num_buyers = int(cols[6])
                    purchase_price = float(cols[8][1:])
                    total_buy = float(cols[12][2:].replace(",", ""))
                    market_cap = yf.Ticker(ticker).info["marketCap"]
                    price = yf.Ticker(ticker).info["regularMarketPrice"]
                    
                    """1. Small cap stocks with cluster buy"""
                    """2. Major insider buy. Cluster of more than 5 people or purchase of more than $100 million"""
                    if market_cap < 1000000000 and num_buyers >= self.cluster_threshold and total_buy >= self.minimum_buy:
                        thesis = "Small cap stock with cluster of %d insiders buying. Total buy of %s.\n" % (num_buyers, cols[12])
                        if price < purchase_price:
                            thesis += "Current price of %s is below insider purchase price of %s.\n" % (price, purchase_price)
                        insider_buys.append(Idea(user="insiders", userType=UserType.INSIDER, ticker=ticker, dateAdded=filing_timestamp, \
                            thesis=thesis, comments="", tags=[]))
                    elif num_buyers >= 5 or total_buy >= 100000000:
                        thesis = "Large buy of %s by %d insiders.\n" % (cols[12], num_buyers)
                        if price < purchase_price:
                            thesis += "Current price of %s is below insider purchase price of %s.\n" % (price, purchase_price)
                        insider_buys.append(Idea(user="insiders", userType=UserType.INSIDER, ticker=ticker, dateAdded=filing_timestamp, \
                            thesis=thesis, comments="", tags=[]))
        return insider_buys