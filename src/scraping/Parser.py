from bs4 import BeautifulSoup, Tag
import logging

class ParserMixin:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def __find_and_extract__(self, soup: BeautifulSoup | Tag, tag: str, class_: str, error_message: str, replace_text: str | None = None) -> str | None:
        element = soup.find(tag, class_=class_)
        if not element:
            self.logger.error(error_message)
            return None
        text = element.text
        if replace_text:
            text = text.replace(replace_text, "")
        return text