from datetime import datetime
from core import UserType, Idea, Screener
from typing import List
import requests 
import bs4
from utils import extract_tickers
import yfinance as yf
import json
import configparser
import praw 
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from summarizer import summarize

BASE_URL = "http://openinsider.com/latest-cluster-buys"
FORBIDDEN_KEYWORDS = ["pharma", "bio", "hold", "fund", "acq"]
class InsiderScreener(Screener):
    #add date so that it only screens before then or something
    #need to load last screened date and use that to filter out irrelevant cluster buys that have been seen
    def __init__(self, cluster_threshold = None, minimum_buy = None, small_mcap = None, initial_screen = None) -> None:
        if cluster_threshold is not None:
            self.cluster_threshold = cluster_threshold
        else: 
            self.cluster_threshold = 3
        if minimum_buy is not None:
            self.minimum_buy = minimum_buy
        else:
            self.minimum_buy = 1000000
        if small_mcap is not None:
            self.small_mcap = small_mcap
        else:
            self.small_mcap = 1000000000
        if initial_screen is not None:
            self.initial_screen = initial_screen
        else:
            self.initial_screen = False
        if not initial_screen:
            with open('cache.json', 'r') as f:
                try:
                    cache = json.load(f)
                    lastScreenedDate = cache['insiderLastScreenDate']
                    self.lastScreenedDate = datetime.strptime(lastScreenedDate, "%Y-%m-%d")
                except Exception as e:
                    raise Exception("Please run initial screen first.")

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
                company_and_industry = company_and_industry.lower()
                filing_timestamp = cols[1]
                filing_timestamp = filing_timestamp.split(" ")[0]
                filing_date = datetime.strptime(filing_timestamp, "%Y-%m-%d")
                if self.initial_screen or filing_date >= self.lastScreenedDate:
                    if not any([x in company_and_industry for x in FORBIDDEN_KEYWORDS]):
                        trade_date = cols[2]
                        ticker = cols[3]
                        #print(ticker)
                        num_buyers = int(cols[6])
                        purchase_price = float(cols[8][1:])
                        total_buy = float(cols[12][2:].replace(",", ""))
                        
                        """1. Small cap stocks with cluster buy"""
                        """2. Major insider buy. Cluster of more than 5 people or purchase of more than $100 million"""
                        if num_buyers >= self.cluster_threshold and total_buy >= self.minimum_buy:
                            yf_t = yf.Ticker(ticker)
                            market_cap = yf_t.info["marketCap"]
                            price = yf_t.info["regularMarketPrice"]
                            if market_cap is not None and market_cap < self.small_mcap:
                                thesis = "Small cap stock with cluster of %d insiders buying. Total buy of %s.\n" % (num_buyers, cols[12])
                                if price is not None and price < purchase_price:
                                    thesis += "Current price of %s is below insider purchase price of %s.\n" % (price, purchase_price)
                                insider_buys.append(Idea(user="insiders", userType=UserType.INSIDER, ticker=ticker, dateAdded=filing_timestamp, \
                                    thesis=thesis, comments="", tags=[]))
                        elif num_buyers >= 5 or total_buy >= 100000000:
                            thesis = "Large buy of %s by %d insiders.\n" % (cols[12], num_buyers)
                            yf_t = yf.Ticker(ticker)
                            price = yf_t.info["regularMarketPrice"]
                            if price is not None and price < purchase_price:
                                thesis += "Current price of %s is below insider purchase price of %s.\n" % (price, purchase_price)
                            insider_buys.append(Idea(user="insiders", userType=UserType.INSIDER, ticker=ticker, dateAdded=filing_timestamp, \
                                thesis=thesis, comments="", tags=[]))
        
        lastScreenedDate = datetime.strftime(datetime.now().date(), "%Y-%m-%d")
        with open('cache.json', 'r') as f:
            cache = json.load(f)
            cache['insiderLastScreenDate'] = lastScreenedDate
        with open('cache.json', 'w') as f:
            f.write(json.dumps(cache))
        
        return insider_buys

GOOD_KEYWORDS = ["value", "contrarian", "financials", "earnings", "supply", "demand", \
    "debt", "cash", "fundamental", "model", "dcf", "book", "insider", "gross", "operating", "margin"]
BAD_KEYWORDS = ["squeeze", "short", "rocket", "stonk", "moon", "tendies", "retard", "monkey", "boyfriend", "wife"]
class RedditScreener(Screener):
    def __init__(self, min_score=None, max_days=None):
        if min_score is None:
            self.min_score = 5
        else:
            self.min_score = min_score
        if max_days is None:
            self.max_days = 7
        else:
            self.max_days = max_days
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.client_id = config["redditApi"]["clientId"]
        self.client_secret = config["redditApi"]["clientSecret"]
        lemmatizer = WordNetLemmatizer()
        self.good_keywords = set([lemmatizer.lemmatize(keyword.lower()) for keyword in GOOD_KEYWORDS])
        self.bad_keywords = set([lemmatizer.lemmatize(keyword.lower()) for keyword in BAD_KEYWORDS])

    def score(self, text):
        tokens = word_tokenize(text)
        lemmatizer = WordNetLemmatizer()
        tokens = [lemmatizer.lemmatize(token.lower()) for token in tokens]
        score = 0
        for token in tokens:
            if token in self.good_keywords:
                score += 1
            if token in self.bad_keywords:
                score -= 1
        return score

    def getIdeas(self) -> List[Idea]:
        reddit = praw.Reddit(client_id=self.client_id, client_secret=self.client_secret, user_agent='Idea Screener')
        new_posts = reddit.subreddit("wallstreetbets").new(limit=250)  
        new_dd_posts = []
        for post in new_posts:
            if post.link_flair_text == "DD":
                new_dd_posts.append(post)
        #print("Secured DD posts")
        ideas = []
        for post in new_dd_posts:
            title = post.title.encode('ascii', 'ignore').decode()
            body = post.selftext.encode('ascii', 'ignore').decode()
            body = ' '.join(word for word in body.split() 
                    if not (word.startswith('[') or word.startswith('http') or 'http' in word))
            sc = self.score(title+body)
            tickers = extract_tickers(title)
            if tickers == []:
                tickers = extract_tickers(body)
            #print(tickers)
            days_since_post = (datetime.now() - datetime.fromtimestamp(post.created_utc)).days
            if sc >= self.min_score and tickers != [] and days_since_post <= self.max_days:
                #print("Found post with tickers %s" % tickers)
                for ticker in tickers:
                    thesis = "Score %d. Title: %s.\n" % (sc, title)
                    thesis += "Summary: "
                    thesis += " ".join(summarize(title, body, count=5))
                    comments = post.url
                    ideas.append(Idea(user=post.author.name, userType=UserType.REDDIT, ticker=ticker, \
                        thesis=thesis, comments=comments, tags=[]))
        return ideas