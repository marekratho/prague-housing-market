from scraper_engine.bezrealitky_scraper import BezrealitkyScraper
from scraper_engine.sreality_scraper import SrealityScraper
from scraper_engine.ceskereality_scraper import CeskerealityScraper
import json
from utils import print_data_report


if __name__ == "__main__":
    # with open('./config/bezrealitky_config.json', mode='r') as f:
    #     config = json.load(f)
    # bezrealitkyScraper = BezrealitkyScraper(config=config)
    # bezrealitkyScraper.scrape(total_attemps=10)
    # print_data_report(bezrealitkyScraper.listings, 'Cena', 'DISPOZICE')

    # with open('./config/sreality_config.json', mode='r') as f:
    #     sreality_config = json.load(f)
    # srealityScraper = SrealityScraper(config=sreality_config)
    # srealityScraper.scrape()
    # srealityScraper.parse_listing_name()
    # print_data_report(srealityScraper.listings, 'Cena', 'Disposition')

    with open('./config/ceskereality_config.json', mode='r') as f:
        ceskereality_config = json.load(f)
    ceskerealityScraper = CeskerealityScraper(config=ceskereality_config)
    ceskerealityScraper.scrape()
