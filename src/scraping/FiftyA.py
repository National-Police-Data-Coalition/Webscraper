import re
import logging
import time

from datetime import datetime
from bs4 import BeautifulSoup, Tag
from scraping.Scraper import ScraperMixin
from scraping.Parser import ParserMixin


class FiftyA(ScraperMixin, ParserMixin):
    SEED = "https://www.50-a.org"
    RATE_LIMIT = 3
    LOCATION_REGEX = r'Location:\s*(.+)'
    PRECINCT_REGEX = r'In NYPD\s+(\S+)\s*Precinct\s*(.+)'
    INCIDENT_REGEX = r"Incident: "
    REASON_FOR_CONTACT = "Reason for contact: "
    OUTCOME_REGEX = r'Outcome:.*\barrest\b'
    LINK_PATTERN = re.compile(r'^https://.*$')
    COMPLAINT_PATTERN = re.compile(r'^\/complaint\/\w+$')
    OFFICER_PATTERN = re.compile(r'^\/officer\/\w+$')

    def __init__(self, logger: logging.Logger | None = None):
        super().__init__(logger=logger)
        self.rate_limit = self.RATE_LIMIT

    def __find_officers__(self, precinct: str) -> list[str]:
        """Find all officers in a precinct"""
        precinct_url = f"{self.SEED}{precinct}"
        officers = self.find_urls(precinct_url,  self.OFFICER_PATTERN)
        self.logger.info(f"Found {len(officers)} officers in precinct {precinct}")
        return officers
    
    def __parse_officer_profile__(self, officer_html: str) -> dict | None:
        """
        Parse an officer's profile
        Returns None if the officer profile is not valid, ie no name, tax id, or description  
        """
        officer = {}
        soup = BeautifulSoup(officer_html, 'html.parser')
        link_pattern = re.compile(r'^\/complaint\/\w+$')
        officer["complaints"]  = list(set([complaint['href'] for complaint in soup.find_all('a', href=link_pattern)]))
 
        soup: Tag |  None  = soup.find("div", class_="identity") # type: ignore
        if not soup:
            self.logger.error("Could not find identity div")
            return None
        
        officer["tax_id"] = self.__find_and_extract__(soup, "span", "taxid", "No tax id found for officer", "Tax #")
        if not officer["tax_id"]:
            return None
        

        title = self.__find_and_extract__(soup, 'h1', "title name", "No title found for officer")
        if not title:
            return None
        
        officer["first_name"], officer["last_name"] = title.split(" ") if len(title.split(" ")) < 3  else (title.split(" ")[0], title.split(" ")[2])
        self.logger.info(f"Found officer {officer['first_name']} {officer['last_name']}")


        description = soup.find("span", class_="desc") # type: ignore

        if not description:
            self.logger.error("No description found for officer")
        else:
            description = description.text
            officer_descriptions = description.replace(",", "").split(" ")
            if len(officer_descriptions) == 3:
                officer["race"], officer["gender"], officer["age"] = officer_descriptions
            else:
                self.logger.warning(f"Could not parse officer description: {description}")


        officer["rank"] =  self.__find_and_extract__(soup, "span", "rank", "No rank found for officer", "Rank: ")   
        department = self.__find_and_extract__(soup, "span", "department", "No department found for officer", "Department: ")
        officer["badge"] = self.__find_and_extract__(soup, "span", "badge", "No badge found for officer", "Badge #: ")
        officer["work_history"] = [precinct.text for precinct in soup.find_all("a", href=self.COMPLAINT_PATTERN) if precinct.text and precinct.text != department]


        return officer
    
    def __parse_complaint__(self, complaint_html: str, complaint_link: str) -> dict | None:
        """
        Parse a complaint
        """
        incident = {}
        soup = BeautifulSoup(complaint_html, 'html.parser')

        details_text = self.__find_and_extract__(soup, "div", "details", "No details found for complaint")
        if not details_text:
            return None
        details = [detail.strip() for detail in details_text.split('\n') if detail.strip()]

        incident_location = self.__get_location__(details_text)
        precinct_number, precinct_name = self.__get_precinct__(details_text)

        victim = self.__parse_victim__(soup)
        force = self.__get_force__(soup)
        officer_involved_badges = self.__get_officer_badges__(soup)
        witnesses = self.__get_witnesses__(details)

        incident = self.__build_incident__(details, details_text, incident_location, precinct_number, precinct_name, victim, force, officer_involved_badges, witnesses, complaint_link)

        return incident

    def __get_location__(self, details_text):
        location_match = re.search(self.LOCATION_REGEX, details_text)
        return location_match.group(1).strip() if location_match else None

    def __get_precinct__(self, details_text):
        precinct_match = re.search(self.PRECINCT_REGEX, details_text, re.IGNORECASE)
        precinct_number = precinct_match.group(1).strip() if precinct_match else None
        precinct_name = precinct_match.group(2).strip() if precinct_match else None
        return precinct_number, precinct_name

    def __parse_victim__(self, soup):
        parsed_victim = [complaint.text.strip().replace("\xa0", ",").split(",") for complaint in soup.find_all('td', class_="complainant")][0]
        return {
            "ethnicity": parsed_victim[0] if parsed_victim and parsed_victim[0] else None,
            "gender": parsed_victim[1] if len(parsed_victim) > 1 and parsed_victim[1] else None,
            "age": parsed_victim[3] if len(parsed_victim) > 3 and parsed_victim[3] else None
        }

    def __get_force__(self, soup):
        return ", ".join(list(set([allegation.text.strip().replace("Force: ", "") for allegation in soup.find_all('td', class_="allegation") if "Force: " in allegation.text.strip()])))

    def __get_officer_badges__(self, soup):
        officer_involved = soup.find_all('a', class_="name")
        return list(set([officer.get('title', '') for officer in officer_involved]))

    def __get_witnesses__(self, details):
        witnesses = []
        add_flag = False
        for detail in details:
            if add_flag: witnesses.append(detail)
            if detail == "Witness Officers:": add_flag = True
        return witnesses

    def __build_incident__(self, details, details_text, incident_location, precinct_number, precinct_name, victim, force, officer_involved_badges, witnesses, complaint_link):
        incident = {}
        incident["location"] = incident_location
        incident["precinct_number"] = precinct_number
        incident["precinct_name"] = precinct_name
        incident["victim"] = victim
        incident["force"] = force
        incident["officer_involved_badges"] = officer_involved_badges
        incident["witnesses"] = witnesses
        incident["complaint_link"] = complaint_link
        return incident

    def extract_data(self, debug=False) -> list[dict]:
        """Extract the officer profiles from 50a"""
        precincts = self.find_urls(f"{self.SEED}/commands", self.COMPLAINT_PATTERN)
        self.logger.info(f"Found {len(precincts)} precincts")
        officers = []


        if debug:
            precincts = precincts[:10]

        for index, precinct in enumerate(precincts):
            if index % 10 == 0 and index != 0:
                self.logger.info(f"Scrapped {index} precincts and have found {len(officers)} officers")
            time.sleep(self.RATE_LIMIT)
            officers += self.__find_officers__(precinct)
            
        self.logger.info(f"Found {len(officers)} officers")


        officer_profiles = []
        complaints = []
        if debug:
            officers = officers[:10]

        for index, officer in enumerate(officers):
            if index % 10 == 0 and index != 0:
                self.logger.info(f"Scrapped {index} officers and have found {len(officer_profiles)} officer profiles")
            response = self.fetch(f"{self.SEED}{officer}")
            if not response: 
                continue
            officer_profiles.append(self.__parse_officer_profile__(response))
            complaints += officer_profiles[-1].pop("complaints")

        self.logger.info(f"Found {len(officer_profiles)} officer profiles")

        if debug:
            complaints = complaints[:10]

        incidents = []
        for index, complaint in enumerate(complaints):
            if index % 10 == 0 and index != 0:
                self.logger.info(f"Scrapped {index} complaints")
            response = self.fetch(f"{self.SEED}{complaint}")
            if not response: 
                continue
            incidents.append(self.__parse_complaint__(response, complaint))
        return officer_profiles
    
    
    
