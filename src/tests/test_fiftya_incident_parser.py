import pytest
from scraping.FiftyA.FiftyAIncidentParser import FiftyAIncidentParser

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
    details = ["Some details", "Reason for contact: Traffic violation", "More details", "Reason for contact: Suspicious activity"]
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