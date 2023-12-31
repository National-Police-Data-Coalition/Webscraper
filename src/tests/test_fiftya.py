import pytest
from unittest.mock import patch
from scraping.FiftyA.FiftyA import FiftyA
from scraping.FiftyA.FiftyAOfficerParser import FiftyAOfficerParser
from scraping.FiftyA.FiftyAIncidentParser import FiftyAIncidentParser


@pytest.fixture
def fiftyA():
    return FiftyA()


@patch.object(FiftyA, "find_urls")
def test_find_officers(mock_find_urls, fiftyA):
    mock_find_urls.return_value = ["/officer1", "/officer2"]
    result = fiftyA._find_officers("/precinct1")
    mock_find_urls.assert_called_once_with(
        f"{fiftyA.SEED}/precinct1", fiftyA.OFFICER_PATTERN
    )
    assert result == ["/officer1", "/officer2"]


@patch.object(FiftyA, "find_urls")
def test_extract_data(mock_find_urls, fiftyA):
    # Mock the return value of find_urls
    precincts = ["/precinct1", "/precinct2", "/precinct3"]
    complaints = ["/complaint1"]
    fake_officer = {
        "name": "John Doe",
        "rank": "Officer",
        "complaints": complaints,
        "tax_id": "123456789"
    }
    mock_find_urls.return_value = precincts

    # Mock the return value of fetch method
    fiftyA.fetch = lambda url: f"Response for {url}"

    # Mock the officer parser
    officer_parser = FiftyAOfficerParser( fiftyA.logger)
    officer_parser.parse_officer = lambda soup: fake_officer
    FiftyAOfficerParser.__new__ = lambda cls, *args, **kwargs: officer_parser # type: ignore

    # Mock the incident parser
    incident_parser = FiftyAIncidentParser(None)
    incident_parser.parse_complaint = lambda response, complaint: {
        "complaint": complaint,
        "status": "Open",
    } # type: ignore
    
    FiftyAIncidentParser.__new__ = lambda cls, *args, **kwargs: incident_parser # type: ignore

    # Call the method under test
    result = fiftyA.extract_data()

    # Assert the expected results
    assert len(result) == len(precincts) ** 2
    assert result == [fake_officer] * len(precincts) ** 2
