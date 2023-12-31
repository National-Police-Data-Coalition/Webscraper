import re   
from bs4 import BeautifulSoup
from scraping.Parser import ParserMixin
from datetime import datetime


class FiftyAIncidentParser(ParserMixin):
    LOCATION_REGEX = r'Location:\s*(.+)'
    PRECINCT_REGEX = r'In NYPD\s+(\S+)\s*Precinct\s*(.+)'
    TIME_FORMAT = "%m-%d-%Y %H:%M:%S"
    INCIDENT_REGEX = r"Incident: "
    REASON_FOR_CONTACT = "Reason for contact: "
    OUTCOME_REGEX = r'Outcome:.*\barrest\b'
    LINK_PATTERN = re.compile(r'^https://.*$')

    def __init__(self, logger):
        self.logger = logger

    def _get_stop_type(self, details: list[str]) -> str | None:
        reason = next((item for item in details if re.search(re.escape("Reason for contact:"), item)), None)
        if reason:
            return reason.replace("Reason for contact:", "").strip()
        return None

    def _get_location(self, details_text: str) -> str | None:
        location_match = re.search(self.LOCATION_REGEX, details_text)
        return location_match.group(1).strip() if location_match else None

    def _get_precinct(self, details_text):
        precinct_match = re.search(self.PRECINCT_REGEX, details_text, re.IGNORECASE)
        precinct_number = precinct_match.group(1).strip() if precinct_match else None
        precinct_name = precinct_match.group(2).strip() if precinct_match else None
        return precinct_number, precinct_name

    def _parse_victim(self, soup):
        parsed_victim = [complaint.text.strip().replace("\xa0", ",").split(",") for complaint in soup.find_all('td', class_="complainant")][0]
        return {
            "ethnicity": parsed_victim[0] if parsed_victim and parsed_victim[0] else None,
            "gender": parsed_victim[1] if len(parsed_victim) > 1 and parsed_victim[1] else None,
            "age": parsed_victim[3] if len(parsed_victim) > 3 and parsed_victim[3] else None
        }

    def __get_force__(self, soup):
        return ", ".join(list(set([allegation.text.strip().replace("Force: ", "") for allegation in soup.find_all('td', class_="allegation") if "Force: " in allegation.text.strip()])))

    def _get_officer_badges(self, soup):
        officer_involved = soup.find_all('a', class_="name")
        return list(set([officer.get('title', '') for officer in officer_involved]))

    def _get_witnesses(self, details):
        witnesses = []
        add_flag = False
        for detail in details:
            if add_flag: 
                witnesses.append(detail)
            if detail == "Witness Officers:": 
                add_flag = True
        return witnesses

    def parse_complaint(self, complaint_html: str, complaint_link: str) -> dict | None:
        """
        Parse a complaint
        """
        soup = BeautifulSoup(complaint_html, 'html.parser')

        details_text = self._find_and_extract(soup, "div", "details", "No details found for complaint")
        if not details_text:
            return None
        details = [detail.strip() for detail in details_text.split('\n') if detail.strip()]

        links = soup.find_all('a', href=self.LINK_PATTERN)

        incident_location = self._get_location(details_text)
        precinct_number, precinct_name = self._get_precinct(details_text)

        # table = soup.find('tbody')
        # perps = soup.find_all('a', class_="name")
        # perpetrators = list(set([perp.text for perp in perps]))

        victim = self._parse_victim(soup)
        force = self.__get_force__(soup)
        officer_involved_badges = self._get_officer_badges(soup)

        witnesses = self._get_witnesses(details)

        return {
            "id": None,
            "source_id": None,
            "date_record_recorded": datetime.now().strftime("%m-%d-%Y %H:%M:%S"),
            "time_of_incident": datetime.strptime(details[0].strip("Incident: "), "%B %d, %Y").strftime("%m-%d-%Y %H:%M:%S"),
            "description": f"Incident scraped from: {complaint_link}",
            "location": f"{incident_location} In NYPD {precinct_number} Precinct {precinct_name}" if incident_location and precinct_number and precinct_name else None,
            "longitude": 40.7128,  # TODO: Use the specific NYPD precinct
            "latitude": 74.0060,  # TODO: Use the specific NYPD precinct
            "stop_type": self._get_stop_type(details),
            "call_type": None,
            "has_attachments": bool(links),
            "from_report": True,
            "was_victim_arrested": bool(re.compile(self.OUTCOME_REGEX, re.IGNORECASE).search(details_text)),
            "arrest_id": None,  # TODO
            "criminal_case_brought": None,  # TODO
            "case_id": None,  # TODO
            "victims": [victim],
            "perpetrators": list(set(officer_involved_badges)),
            "tags": None,  # TODO - No idea what this (from db: f"<Tag {self.id}: {self.term}>")
            "agencies_present": [f"NYPD {precinct_number} Precinct {precinct_name}" if precinct_number and precinct_name else None],
            "participants": witnesses,
            "attachments": None,  # TODO - not sure how to store this
            "investigations": None,  # TODO - I think this is unfinished in db
            "results_of_stop": None,  # TODO - Not sure what this is
            "actions": None,  # TODO
            "use_of_force": force,
            "legal_case": None,  # TODO
        }
        
