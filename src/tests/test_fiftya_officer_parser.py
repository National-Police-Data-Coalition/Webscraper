import pytest
from bs4 import BeautifulSoup
from scraping.FiftyA.FiftyAOfficerParser import FiftyAOfficerParser


@pytest.fixture
def officer_parser():
    return FiftyAOfficerParser(None)


def test_parse_officer_with_valid_soup(officer_parser):
    soup = BeautifulSoup(
        """<html>
            <h1 class='title name'>John Doe</h1>
            <span class='desc'>White Male, 30</span>
            <span class='rank'>Officer</span>
            <span class='badge'>12345</span>
            <span class='taxid'>123456789</span>
            <span class='department'>Police Department</span>
            <a href='/complaint/1'>Complaint 1</a>
            <a href='/complaint/2'>Complaint 2</a>
            <div class="commandhistory">
                <a href='/command/precinct1'>Precinct 1</a>
                <a href='/command/precinct2'>Precinct 2</a>
            </div>
        </html>""",
        'html.parser',
    )

    expected_result = {
        'first_name': 'John',
        'last_name': 'Doe',
        'race': 'White',
        'tax_id': '123456789',
        'gender': 'Male',
        'age': '30',
        'rank': 'Officer',
        'badge': '12345',
        'work_history': ['Precinct 1', 'Precinct 2'],
        'complaints': ['/complaint/1', '/complaint/2'],
    }

    result = officer_parser.parse_officer(soup)

    assert result == expected_result


def test_parse_officer_with_missing_fields(officer_parser):
    soup = BeautifulSoup(
        """
        <html>
            <h1 class='title name'>John Doe</h1>
            <span class='badge'>12345</span>
            <span class='taxid'>123456789</span>
        </html>
        """,
        'html.parser',
    )

    expected_result = {
        'first_name': 'John',
        'last_name': 'Doe',
        'tax_id': '123456789',
        'badge': '12345',
        'complaints': [],
        'work_history': [],
    }

    result = officer_parser.parse_officer(soup)

    assert result == expected_result


def test_parse_officer_with_invalid_soup(officer_parser):
    soup = BeautifulSoup('<html></html>', 'html.parser')

    result = officer_parser.parse_officer(soup)

    assert result is None


def test_get_work_history_with_valid_soup(officer_parser):
    soup = BeautifulSoup(
        """<html>
            <div class="commandhistory">
                <a href='/command/precinct1'>Precinct 1</a>
                <a href='/command/precinct2'>Precinct 2</a>
            </div>
        </html>""",
        'html.parser',
    )

    expected_result = ['Precinct 1', 'Precinct 2']

    result = officer_parser._get_work_history(soup)

    assert result == expected_result


def test_get_work_history_with_missing_div(officer_parser):
    soup = BeautifulSoup('<html></html>', 'html.parser')

    expected_result = []

    result = officer_parser._get_work_history(soup)

    assert result == expected_result


def test_get_work_history_with_missing_links(officer_parser):
    soup = BeautifulSoup(
        """<html>
            <div class="commandhistory">
            </div>
        </html>""",
        'html.parser',
    )

    expected_result = []

    result = officer_parser._get_work_history(soup)

    assert result == expected_result