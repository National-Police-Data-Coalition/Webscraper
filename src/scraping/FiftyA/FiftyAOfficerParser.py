import re
from scraping.Parser import ParserMixin
from logging import Logger
from bs4 import BeautifulSoup

class FiftyAOfficerParser(ParserMixin):
    COMPLAINT_PATTERN = re.compile(r'^\/complaint\/\w+$')
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self.PRECINT_PATTERN = re.compile(r'^https://.*$')

    def _get_tax_id(self, soup):
        tax_id = self._find_and_extract(soup, "span", "taxid", "No tax id found for officer", "Tax #")
        if not tax_id:
            return None
        return tax_id
    
    def _get_complaints(self, soup):
        complaint_links = soup.find_all("a", href=self.COMPLAINT_PATTERN)
        return [complaint.get("href") for complaint in complaint_links]

    def parse_officer(self, soup: BeautifulSoup) -> dict | None:
        if not soup:
            self.logger.error("Could not find identity div")
            return None

        officer = {}

        officer["complaints"] = self._get_complaints(soup)

        tax_id = self._get_tax_id(soup)
        if not tax_id:
            self.logger.error("Officer does not have a tax id")
            return None
        officer["taxId"] = tax_id

        title = self._find_and_extract(soup, 'h1', "title name", "No title found for officer")
        if title:
            first_name, last_name = title.split(" ") if len(title.split(" ")) < 3  else (title.split(" ")[0], title.split(" ")[2])
            officer["first_name"] = first_name
            officer["last_name"] = last_name
        else:
            self.logger.error("No title found for officer")

        description = soup.find("span", class_="desc") # type: ignore
        if description:
            description = description.text
            officer_descriptions = description.replace(",", "").split(" ")
            if len(officer_descriptions) == 3:
                officer["race"], officer["gender"], officer["age"] = officer_descriptions
            else:
                self.logger.warning(f"Could not parse officer description: {description}")

        rank = self._find_and_extract(soup, "span", "rank", "No rank found for officer", "Rank: ")
        if rank:
            officer["rank"] = rank

        badge = self._find_and_extract(soup, "span", "badge", "No badge found for officer", "Badge #: ")
        officer["badge"] = badge

        department = self._find_and_extract(soup, "span", "department", "No department found for officer", "Department: ")
        work_history = [precinct.text for precinct in soup.find_all("a", href=self.PRECINT_PATTERN) if precinct.text and precinct.text != department]
        if work_history:
            officer["work_history"] = work_history

        return officer