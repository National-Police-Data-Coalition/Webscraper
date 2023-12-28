import pytest
from unittest.mock import patch
from scraping.FiftyA import FiftyA

@patch.object(FiftyA, '__parse_officer_profile__')
@patch.object(FiftyA, 'fetch')
@patch.object(FiftyA, 'find_urls')
def test_extract_data(mock_find_urls, mock_fetch, mock_parse):
    mock_find_urls.return_value = ['/precinct1', '/precinct2', '/precinct3']
    mock_fetch.return_value = 'response'
    mock_parse.return_value = {'officer': 'data'}
    scraper = FiftyA()

    result = scraper.extract_data()

    assert mock_find_urls.call_count == 1 + len(mock_find_urls.return_value)
    assert mock_fetch.call_count ==  len(mock_find_urls.return_value) ** 2
    assert mock_parse.call_count ==  len(mock_find_urls.return_value) ** 2
    assert result == [mock_parse.return_value] * len(mock_find_urls.return_value) ** 2

@pytest.fixture
def fiftyA():
    return FiftyA()

def test_find_officers(fiftyA):
    with patch.object(fiftyA, 'find_urls', return_value=['/officer1', '/officer2']) as mock_find_urls:
        result = fiftyA.__find_officers__('/precinct1')
        mock_find_urls.assert_called_once_with(f"{fiftyA.SEED}/precinct1", fiftyA.officer_pattern)
        assert result == ['/officer1', '/officer2']

def test_parse_officer_profile(fiftyA):
    mock_response = """
    <div class="identity">
            <h1 class="title name">John Doe</h1>
            <span class="taxid">Tax #123</span>
    </div>
    """
    result = fiftyA.__parse_officer_profile__(mock_response)
    assert result is not None