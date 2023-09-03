from bezrealitky_scraper import BezrealitkyScraper
import json
from utils import print_data_report


if __name__ == "__main__":
    with open('./config/bezrealitky_config.json', mode='r') as f:
        config = json.load(f)
    bezrealitkyScraper = BezrealitkyScraper(config=config)
    bezrealitkyScraper.scrape(total_attemps=10)

    print_data_report(bezrealitkyScraper.listings, 'Cena', 'DISPOZICE')
