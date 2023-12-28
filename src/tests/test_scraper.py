import pytest
from unittest.mock import patch
from scraping.Scraper import Scraper

class TestScraper:
    @pytest.fixture
    def scraper(self):
        return Scraper()

    def test_init(self, scraper):
        assert scraper.rate_limit == 5

    @patch.object(Scraper, 'fetch')
    def test_fetch(self, mock_fetch, scraper):
        # Arrange
        mock_fetch.return_value = 'response'
        url = 'http://test.com'

        # Act
        result = scraper.fetch(url)

        # Assert
        mock_fetch.assert_called_once_with(url)
        assert result == 'response'

    @patch.object(Scraper, 'find_urls')
    def test_find_urls(self, mock_find_urls, scraper):
        # Arrange
        mock_find_urls.return_value = ['http://test.com/page1', 'http://test.com/page2']
        url = 'http://test.com'
        pattern = r'^/page/\w+$'

        # Act
        result = scraper.find_urls(url, pattern)

        # Assert
        mock_find_urls.assert_called_once_with(url, pattern)
        assert result == ['http://test.com/page1', 'http://test.com/page2']