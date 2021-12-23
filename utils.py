from typing import List
import re
from nltk.corpus import words

COMMON_WORDS = set(["US", "EV", "DCF", "EPS", "IV", "PE", "CEO", "SARS", "TLDR", "DD", "BS", "GAAP"])
def extract_tickers(text: str) -> List[str]:
    """1. Parse using regex for $[2-4 uppercase characters]"""
    tickers = re.findall(r"\$[A-Z]{2,4}", text)
    if tickers != []:
        tickers = [ticker[1:] for ticker in tickers]
        return tickers
    """2. Parse using regex for string followed by ([2-4 uppercase characters])"""
    tickers = re.findall(r"\([A-Z]{2,4}\)", text)
    if tickers != []:
        #strip parnethesis
        tickers = [ticker[1:-1] for ticker in tickers]
        return tickers
    """3. Parse using regex for [2-4 uppercase characters]"""
    #d = enchant.Dict("en_US")
    tickers = re.findall(r"[A-Z]{2,4}\s", text)
    if tickers != []:
        filtered_tickers = []
        all_words = set(words.words())
        for ticker in tickers:
            ticker = ticker.strip()
            if ticker.lower() not in all_words and ticker not in COMMON_WORDS:
                filtered_tickers.append(ticker)
        return filtered_tickers
    return []