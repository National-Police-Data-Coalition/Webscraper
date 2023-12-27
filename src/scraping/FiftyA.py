import re
from bs4 import BeautifulSoup, Tag
from scraping.Scraper import Scraper
import logging
import time

class FiftyA(Scraper):
    SEED = "https://www.50-a.org"
    PRECINT_PATTERN = re.compile(r'^\/command\/\w+$')
    OFFICER_PATTERN = re.compile(r'^\/officer\/\w+$')
    RATE_LIMIT = 3

    def __init__(self, logger: logging.Logger | None = None):
        super().__init__(logger=logger)
        self.rate_limit = self.RATE_LIMIT

    def __find_officers__(self, precinct: str) -> list[str]:
        """Find all officers in a precinct"""
        precinct_url = f"{self.SEED}{precinct}"
        officers = self.find_urls(precinct_url, self.OFFICER_PATTERN)
        self.logger.info(f"Found {len(officers)} officers in precinct {precinct}")
        return officers
    
    def __parse_officer_profile__(self, officer_html: str) -> dict | None:
        """Parse an officer's profile"""
        soup = BeautifulSoup(officer_html, 'html.parser')
        link_pattern = re.compile(r'^\/complaint\/\w+$')
        complaints = list(set([complaint['href'] for complaint in soup.find_all('a', href=link_pattern)]))
 
        soup: Tag |  None  = soup.find("div", class_="identity") # type: ignore
        if not soup:
            self.logger.error("Could not find identity div")
            return None
        
        tax_id = soup.find("span", class_="taxid") 
        if not tax_id:
            self.logger.error("No tax id found for officer")
            return None
        tax_id = tax_id.text.replace("Tax #", "")
        

        title = soup.find('h1', class_="title name")        
        if not title:
            self.logger.error("No title found for officer")
            return None
        title = title.text
        first_name, last_name = title.split(" ") if len(title.split(" ")) < 3  else (title.split(" ")[0], title.split(" ")[2])
        self.logger.info(f"Found officer {first_name} {last_name}")


        description = soup.find("span", class_="desc")
        if not description:
            self.logger.error("No title found for officer")
            return None
        description = description.text

        officer_descriptions = description.replace(",", "").split(" ")
        race, gender, age = None, None, None
        if len(officer_descriptions) == 3:
            race, gender, age = officer_descriptions
        else:
            self.logger.warning(f"Could not parse officer description: {description}")


        rank = soup.find("span", class_="rank")
        if not rank:
            self.logger.warning(f"No rank found for officer {first_name} {last_name}")
        else:
            rank = rank.text
            
        department = soup.find("a", class_="command", href=re.compile(r"^/command/(\w+)$"))
        department = None if not department else department.text
        work_history = [precinct.text for precinct in soup.find_all("a", href=re.compile(r"^/command/(\w+)$")) if precinct.text and precinct.text != department]

        badge = soup.find("span", class_="badge")
        # badge = None if not badge else badge.text.replace("Badge #", "")
        if not badge:
            self.logger.warning(f"No badge found for officer {first_name} {last_name}")
            return None
        badge = badge.text.replace("Badge #", "")

        return {
            "complaints": complaints,
            "first_name": first_name,
            "last_name": last_name,
            "department": department,
            "rank": rank,
            "badge": badge, 
            "race": race,
            "gender": gender,
            "work_history": work_history,
            "age": age,
            "taxId": tax_id
        }

    def extract_data(self) -> list[dict]:
        """Extract the officer profiles from 50a"""
        precincts = self.find_urls(f"{self.SEED}/commands", self.PRECINT_PATTERN)
        self.logger.info(f"Found {len(precincts)} precincts")
        officers = []
        for index, precinct in enumerate(precincts):
            if index % 10 == 0 and index != 0:
                self.logger.info(f"Scrapped {index} precincts and have found {len(officers)} officers")
            time.sleep(self.RATE_LIMIT)
            officers += self.__find_officers__(precinct)
            
        self.logger.info(f"Found {len(officers)} officers")
        officer_profiles = []
        for index, officer in enumerate(officers):
            if index % 10 == 0 and index != 0:
                self.logger.info(f"Scrapped {index} officers and have found {len(officer_profiles)} officer profiles")
            response = self.fetch(f"{self.SEED}{officer}")
            if not response: continue
            officer_profiles.append(self.__parse_officer_profile__(response))
        return officer_profiles
    
    
    
