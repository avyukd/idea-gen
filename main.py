import argparse

parser = argparse.ArgumentParser(description="Idea generation and research terminal for investors.")
parser.add_argument("--run", help="Run all screeners to update ideas. Recommend watchlist adds.")
parser.add_argument("--add", help="Add an idea to the watchlist.")
parser.add_argument("--remove", help="Remove an idea from the watchlist.")