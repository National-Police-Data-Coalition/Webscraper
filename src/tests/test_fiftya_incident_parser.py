import pytest
from scraping.FiftyA.FiftyAIncidentParser import FiftyAIncidentParser
from unittest.mock import patch
from bs4 import BeautifulSoup

@pytest.fixture
def incident_parser():
    return FiftyAIncidentParser(logger=None)


def test_get_stop_type_with_reason(incident_parser):
    details = ["Some details", "Reason for contact: Traffic violation", "More details"]
    result = incident_parser._get_stop_type(details)
    assert result == "Traffic violation"


def test_get_stop_type_without_reason(incident_parser):
    details = ["Some details", "More details"]
    result = incident_parser._get_stop_type(details)
    assert result is None


def test_get_stop_type_with_multiple_reasons(incident_parser):
    details = [
        "Some details",
        "Reason for contact: Traffic violation",
        "More details",
        "Reason for contact: Suspicious activity",
    ]
    result = incident_parser._get_stop_type(details)
    assert result == "Traffic violation"


def test_get_location_with_location(incident_parser):
    details_text = "Location: New York"
    expected_location = "New York"
    assert incident_parser._get_location(details_text) == expected_location


def test_get_location_without_location(incident_parser):
    details_text = "No location information available"
    expected_location = None
    assert incident_parser._get_location(details_text) == expected_location


def test_get_location_with_leading_trailing_spaces(incident_parser):
    details_text = "   Location:   New York   "
    expected_location = "New York"
    assert incident_parser._get_location(details_text) == expected_location


def test_parse_victim(incident_parser):
    # Create a sample HTML soup
    soup = BeautifulSoup(
        """
    <td class="complainant">
        Female,&nbsp;<span class="age">48</span>
    </td>
    """,
        "html.parser",
    )

    

    assert incident_parser._parse_victim(soup) == {
        "ethnicity": None,
        "gender": "Female",
        "age": "48",
    }
    
    
def test_parse_victim_with_some_none(incident_parser):
    soup = BeautifulSoup(
        """
        <td class="complainant">
                White&nbsp;Male,&nbsp;<span class="age">35</span>
              </td>
    """,
        "html.parser",
    )
    assert incident_parser._parse_victim(soup) == {
        "ethnicity": "White",
        "gender": "Male",
        "age": "35",
    }


def test_parse_victim_with_no_victim(incident_parser):
    # Create a sample HTML soup
    soup = BeautifulSoup(
        """
    <td class="complainant">
    </td>
    """,
        "html.parser",
    )

    assert incident_parser._parse_victim(soup) is None


# def test_parse_complaint():
#     parser = FiftyAIncidentParser(logger=None)
#     complaint_html = """
#         <html>
#             <div class="details">
#                 Incident: January 1, 2022
#                 Location: New York
#                 Reason for contact: Traffic violation
#                 Outcome: Arrest
#             </div>
#             <a href="https://example.com">Link</a>
#         </html>
#     """
#     complaint_link = "https://example.com"

#     expected_result = {
#         "id": None,
#         "source_id": None,
#         "date_record_recorded": "01-01-2022 00:00:00",
#         "time_of_incident": "01-01-2022 00:00:00",
#         "description": "Incident scraped from: https://example.com",
#         "location": "New York In NYPD None Precinct None",
#         "longitude": 40.7128,
#         "latitude": 74.0060,
#         "stop_type": "Traffic violation",
#         "call_type": None,
#         "has_attachments": True,
#         "from_report": True,
#         "was_victim_arrested": True,
#         "arrest_id": None,
#         "criminal_case_brought": None,
#         "case_id": None,
#         "victims": [{"ethnicity": None, "gender": None, "age": None}],
#         "perpetrators": [],
#         "tags": None,
#         "agencies_present": [None],
#         "participants": [],
#         "attachments": None,
#         "investigations": None,
#         "results_of_stop": None,
#         "actions": None,
#         "use_of_force": "",
#         "legal_case": None,
#     }

#     result = parser.parse_complaint(complaint_html, complaint_link)

#     assert result == expected_result
