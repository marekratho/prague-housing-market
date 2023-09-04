from scraper_engine.bezrealitky_scraper import BezrealitkyScraper
from scraper_engine.sreality_scraper import SrealityScraper
from scraper_engine.ceskereality_scraper import CeskerealityScraper
import json
import datetime
from utils import print_data_report, save_list, load_config


if __name__ == "__main__":
    bezrealitky_config = load_config('./config/bezrealitky_config.json')
    bezrealitkyScraper = BezrealitkyScraper(config=bezrealitky_config)
    bezrealitkyScraper.scrape(total_attemps=10)
    save_list(bezrealitkyScraper.listings, f"../raw_data/bezrealitky_raw_{datetime.today().strftime('%Y-%m-%d')}.pkl")
    print_data_report(bezrealitkyScraper.listings, 'Cena', 'DISPOZICE')

    sreality_config = load_config('./config/sreality_config.json')
    srealityScraper = SrealityScraper(config=sreality_config)
    srealityScraper.scrape()
    save_list(srealityScraper.listings, f"../raw_data/sreality_raw_{datetime.today().strftime('%Y-%m-%d')}.pkl")
    srealityScraper.parse_listing_name()
    print_data_report(srealityScraper.listings, 'Cena', 'Disposition')

    ceskereality_config = load_config('./config/ceskereality_config.json')
    ceskerealityScraper = CeskerealityScraper(config=ceskereality_config)
    ceskerealityScraper.scrape()
    save_list(ceskerealityScraper.listings, f"../raw_data/ceskereality_raw_{datetime.today().strftime('%Y-%m-%d')}.pkl")
