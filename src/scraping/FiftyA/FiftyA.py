import re
import logging
import time

from bs4 import BeautifulSoup
from scraping.Scraper import ScraperMixin
from scraping.Parser import ParserMixin

from scraping.FiftyA.FiftyAOfficerParser import FiftyAOfficerParser
from scraping.FiftyA.FiftyAIncidentParser import FiftyAIncidentParser


class FiftyA(ScraperMixin, ParserMixin):
    SEED = "https://www.50-a.org"
    RATE_LIMIT = 3
    COMPLAINT_PATTERN = re.compile(r'^\/complaint\/\w+$')
    OFFICER_PATTERN = re.compile(r'^\/officer\/\w+$')
    PRECINT_PATTERN = re.compile(r'^\/command\/\w+$')

    def __init__(self, logger: logging.Logger | None = None):
        super().__init__(logger=logger)
        self.rate_limit = self.RATE_LIMIT

    def _find_officers(self, precinct: str) -> list[str]:
        """Find all officers in a precinct"""
        precinct_url = f"{self.SEED}{precinct}"
        officers = self.find_urls(precinct_url,  self.OFFICER_PATTERN)
        self.logger.info(f"Found {len(officers)} officers in precinct {precinct}")
        return officers

    def extract_data(self, debug=False) -> tuple[list[dict], list[dict]]:
        """Extract the officer profiles from 50a"""
        precincts = self.find_urls(f"{self.SEED}/commands", self.PRECINT_PATTERN)
        self.logger.info(f"Found {len(precincts)} precincts")
        officers = []


        if debug:
            precincts = precincts[:5]

        for index, precinct in enumerate(precincts):
            if index % 10 == 0 and index != 0:
                self.logger.info(f"Scrapped {index} precincts and have found {len(officers)} officers")
            time.sleep(self.RATE_LIMIT)
            officers += self._find_officers(precinct)
            
        self.logger.info(f"Found {len(officers)} officers")


        officer_profiles = []
        complaints = []
        if debug:
            officers = officers[:5]
        officer_parser = FiftyAOfficerParser(self.logger)
        for index, officer in enumerate(officers):
            if index % 10 == 0 and index != 0:
                self.logger.info(f"Scrapped {index} officers and have found {len(officer_profiles)} officer profiles")
            response = self.fetch(f"{self.SEED}{officer}")
            if not response: 
                continue
            officer_profiles.append(officer_parser.parse_officer(soup=BeautifulSoup(response, 'html.parser')))
            if officer_profiles[-1] and officer_profiles[-1].get("complaints"):
                complaints += officer_profiles[-1].pop("complaints")

        self.logger.info(f"Found {len(complaints)} complaints")

        if debug:
            complaints = complaints[:5]

        incidents = []
        incident_parser = FiftyAIncidentParser(self.logger)
        for index, complaint in enumerate(complaints):
            if index % 10 == 0 and index != 0:
                self.logger.info(f"Scrapped {index} complaints")
            response = self.fetch(f"{self.SEED}{complaint}")
            if not response: 
                continue
            incidents.append(incident_parser.parse_complaint(response, complaint))
        return officer_profiles, incidents
    
    
    
