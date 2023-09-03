from abc import ABC, abstractmethod
from typing import Union

class Scraper(ABC):
    '''Abstract class for property listing website scraper.'''
    
    @abstractmethod
    def scrape(self, **kwargs) -> Union[list, None]:
        '''Return a list containing information about listings found during scraping,
        return None if an error occurs during the scraping process.'''