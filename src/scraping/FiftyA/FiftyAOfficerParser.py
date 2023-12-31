import re
import logging
from scraping.Parser import ParserMixin
from bs4 import BeautifulSoup


class FiftyAOfficerParser(ParserMixin):
    COMPLAINT_PATTERN = re.compile(r'^\/complaint\/\w+$')
    PRECINT_PATTERN = re.compile(r'^\/command\/\w+$')
    

    def __init__(self, logger: logging.Logger | None = None):
        if not logger:
            logger = logging.getLogger(__name__)
        self.logger = logger

    def _get_tax_id(self, soup):
        return self._find_and_extract(soup, 'span', 'taxid', 'No tax id found for officer', 'Tax #')

    def _get_complaints(self, soup):
        complaint_links = soup.find_all('a', href=self.COMPLAINT_PATTERN)
        return [complaint.get('href') for complaint in complaint_links]

    def _get_work_history(self, soup) -> list[str]:
        soup = soup.find('div', class_='commandhistory')
        if not soup:
            self.logger.warning('Could not find work history div')
            return []
        work_history = []
        work_history_links = soup.find_all('a', href=self.PRECINT_PATTERN)
        work_history += [work.text for work in work_history_links]
        return work_history

    def parse_officer(self, soup: BeautifulSoup) -> dict | None:
        if not soup:
            self.logger.error('Could not find identity div')
            return None

        officer = {}

        officer['complaints'] = self._get_complaints(soup)

        tax_id = self._get_tax_id(soup)
        if not tax_id:
            self.logger.error('Officer does not have a tax id')
            return None
        officer['tax_id'] = tax_id

        title = self._find_and_extract(soup, 'h1', 'title name', 'No title found for officer')
        if title:
            first_name, last_name = (
                title.split(' ') if len(title.split(' ')) < 3 else (title.split(' ')[0], title.split(' ')[2])
            )
            officer['first_name'] = first_name
            officer['last_name'] = last_name
        else:
            self.logger.error('No title found for officer')

        description = soup.find('span', class_='desc')  # type: ignore
        if description:
            description = description.text
            officer_descriptions = description.replace(',', '').split(' ')
            if len(officer_descriptions) == 3:
                officer['race'], officer['gender'], officer['age'] = officer_descriptions
            else:
                self.logger.warning(f'Could not parse officer description: {description}')

        rank = self._find_and_extract(soup, 'span', 'rank', 'No rank found for officer', 'Rank: ')
        if rank:
            officer['rank'] = rank

        badge = self._find_and_extract(soup, 'span', 'badge', 'No badge found for officer', 'Badge #: ')
        officer['badge'] = badge
        work_history = self._get_work_history(soup)
        officer['work_history'] = work_history

        return officer
