from abc import abstractclassmethod
from datetime import datetime
from enum import Enum
from typing import List
from dateutil import parser
import yfinance as yf 
import configparser
import uuid 
import json 
from abc import ABC, abstractmethod

"""Possible sources of idea"""
class UserType(Enum):
    USERINPUT = 1
    INSIDER = 2
    INSTITUTION = 3
    PODCAST = 4
    NEWSLETTER = 5
    BLOG = 6
    REDDIT = 7
    TWITTER = 8
    FUNDAMENTAL_SCREENER = 9


class Idea():
    
    def __init__(self, user: str, userType: UserType, ticker: str, \
                dateAdded = None, thesis = None, comments = None, tags = None, id = None) -> None:
        if id is None:
            """ADD constructor -- for new idea to be added to database"""
            self.id = str(uuid.uuid4())
            self.user = user
            self.userType = userType
            self.ticker = ticker
            #may need to replace if too slow
            if dateAdded is None:
                #get current date
                self.dateAdded = datetime.now()
            else:
                self.dateAdded = datetime.strptime(dateAdded, "%Y-%m-%d")
                #self.dateAdded = parser.parse(dateAdded)
            #use close price of date
            #if datetime is not today
            if self.dateAdded.date() != datetime.now().date():
                hist = yf.Ticker(ticker).history(period=self.dateAdded.strftime("%Y-%m-%d"))
                self.priceOnAddDate = hist["Close"].values[0]
            else:
                self.priceOnAddDate = yf.Ticker(ticker).info["regularMarketPrice"]
            if thesis is None:
                self.thesis = ""
            else:
                self.thesis = thesis
            if comments is None:
                self.comments = ""
            else:
                self.comments = comments
            if tags is None:
                self.tags = []
            else:
                self.tags = tags
        else:
            """READ constructor -- for existing ideas in database, acts as wrapper"""
            if dateAdded is None or thesis is None or comments is None or tags is None or id is None:
                raise ValueError("Must provide all fields for read constructor.")
            self.id = id
            self.user = user
            self.userType = UserType(userType)
            self.ticker = ticker
            self.dateAdded = parser.parse(dateAdded)
            self.thesis = thesis
            self.comments = comments
            self.tags = json.loads(tags)

    def __str__(self) -> str:
        retStr = "ID: " + self.id + "\n"
        retStr += "User: " + self.user + " (" + self.userType.name + ") "+ "\n"
        retStr += "Ticker: " + self.ticker + "\n"
        retStr += "Date Added: " + self.dateAdded.strftime("%Y-%m-%d") + "\n"
        retStr += "Thesis: " + self.thesis + "\n"
        retStr += "Comments: " + self.comments + "\n"
        retStr += "Tags: " + str(self.tags) + "\n"
        return retStr

    def getPerformance(self) -> float:
        marketPrice = yf.Ticker(self.ticker).info["regularMarketPrice"]
        performance = (marketPrice - self.priceOnAddDate) / self.priceOnAddDate
        return performance

"""Abstract class for idea generators"""
class Screener(ABC):

    @abstractmethod
    def getIdeas() -> List[Idea]:
        pass

