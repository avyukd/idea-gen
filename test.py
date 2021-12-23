import configparser
from screeners import InsiderScreener, RedditScreener
from core import UserType, Idea, Screener
from utils import extract_tickers
from datetime import datetime
import praw 
import nltk
import twitter 
import configparser

def insider_screener_test():
    #iscreener = InsiderScreener(initial_screen=True)
    #insider_ideas = iscreener.getIdeas()
    #for idea in insider_ideas:
    #    print(idea)
    #print("-------------------------------------------------------")
    iscreener2 = InsiderScreener(initial_screen=False)
    insider_ideas2 = iscreener2.getIdeas()
    for idea in insider_ideas2:
        print(idea)

def test_extract_tickers():
    text = "The $AAPL stock is $1.00 and the $MSFT stock is $2.00"
    tickers = extract_tickers(text)
    print(tickers)
    text = "The AAPL stock is $1.00 and the MSFT stock is $2.00"
    tickers = extract_tickers(text)
    print(tickers)
    text = "Apple (AAPL) is $1.00 and Microsoft (MSFT) is $2.00"
    tickers = extract_tickers(text)
    print(tickers)

def test_reddit_screener():
    reddit_screener = RedditScreener()
    reddit_ideas = reddit_screener.getIdeas()
    for idea in reddit_ideas:
        print(idea)

def twitterApiTest():
    #get twitter posts that I have liked, extract tickers from them, and then add ideas of those
    config = configparser.ConfigParser()
    config.read('config.ini')
    consumer_key = config["twitterApi"]["apiKey"]
    consumer_secret = config["twitterApi"]["apiKeySecret"]
    access_token = config["twitterApi"]["accessToken"]
    access_token_secret = config["twitterApi"]["accessTokenSecret"]
    api = twitter.Api(consumer_key=consumer_key,
                  consumer_secret=consumer_secret,
                  access_token_key=access_token,
                  access_token_secret=access_token_secret)
    test = twitter.Api.getUserStream(screen_name="@WallStreetBets")
    print(test)

if __name__ == "__main__":
    twitterApiTest()
    #nltk.download('words')
    #insider_screener_test()
    #test_extract_tickers()
    #test_reddit_screener()
    #reddit = praw.Reddit(client_id="8IWdjzbaAvn14TucQHakqw", client_secret="fsBuNhMQNaaUEYqCWvWMrFqXXeuCGA", user_agent='Idea Screener')
    #new_dd_posts = reddit.subreddit("wallstreetbets").search('flair:DD',limit=500, params={'sort':'new'})
    #get all new posts
    #new_posts = reddit.subreddit("wallstreetbets").new(limit=500)    
    #print days passed since post
    #for post in new_posts:
    #    print((datetime.now() - datetime.fromtimestamp(post.created_utc)).days)
    #    print(post.link_flair_text == "DD")
