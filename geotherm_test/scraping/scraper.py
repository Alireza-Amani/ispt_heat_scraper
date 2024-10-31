'''
This module contains a BeautifulScraper class that uses BeautifulSoup to scrape
web pages for article titles and links.
'''
import time
import requests
from bs4 import element
from ..utils import log_and_print, get_page_body, extract_articles


class BeautifulScraper:
    """
    A customized web scraper using BeautifulSoup.

    Attributes
    ----------
    url : str
        The URL of the web page to scrape.
    retries : int, optional
        The number of times to retry fetching the page if it fails (default is 3).
    retry_delay : int, optional
        The delay in seconds between retries (default is 1).
    verbose : bool, optional
        Whether to print log messages to the console (default is False).
    body : bs4.element.Tag
        The parsed HTML content of the web page.
    articles : dict
        A dictionary storing extracted article titles as keys and their
        corresponding links as values.

    Methods
    -------
    fetch_page()
        Fetches the HTML content of the web page.
    find_articles_links_titles(elemental_address=None)
        Extracts article titles and links based on the provided address.
    """

    def __init__(self, url: str, retries: int = 3, retry_delay: int = 1, verbose: bool = False):
        """
        Initializes a BeautifulScraper instance.

        Parameters
        ----------
        url : str
            The URL of the web page to scrape.
        retries : int, optional
            The number of times to retry fetching the page if it fails (default is 3).
        retry_delay : int, optional
            The delay in seconds between retries (default is 1).
        verbose : bool, optional
            Whether to print log messages to the console (default is False).
        """
        self.url = url
        self.retries = retries
        self.retry_delay = retry_delay
        self.verbose = verbose

        self.body = self._fetch_page()
        self.articles = dict()

    def _fetch_page(self) -> element.Tag:
        """
        Fetches the HTML content of the web page.

        Returns
        -------
        bs4.element.Tag
            The parsed HTML content of the web page.
        """
        for _ in range(self.retries):
            try:
                body = get_page_body(self.url)
                return body
            except requests.RequestException as e:
                message = f"Error fetching page: {e}\nRetrying..."
                log_and_print(message, verbose=self.verbose)
                time.sleep(self.retry_delay)

        message = f"Failed to fetch the page after {self.retries} retries."
        log_and_print(message, verbose=self.verbose)

    def find_articles_links_titles(self, elemental_address: dict = None):
        """
        Extracts article titles and links based on the provided address.

        Parameters
        ----------
        elemental_address : dict, optional
            A dictionary specifying the HTML structure for locating articles,
            titles, and links. For example:

            ```python
            elemental_address = {
                'container_tag': 'div',
                'title': {'tag': 'h2', 'attr': {'class': 'article-title'}},
                'link': {'tag': 'a', 'attr': {'class': 'article-link'}}
            }
            ```

        Raises
        ------
        NotImplementedError
            If no `elemental_address` is provided.
        """
        if elemental_address:
            articles_container = self.body.find_all(
                elemental_address['container_tag'])
            self.articles = extract_articles(
                articles_container,
                elemental_address['title'],
                elemental_address['link']
            )
        else:
            message = "Please provide a specific address to look for the titles and links."
            raise NotImplementedError(message)
            ''' (TODO)
            Potential code to look for the titles and links:
            ------------------------------------------------
            Look for "div", "section", "article" tags that contain an "a" tag
            with an "href" attribute and a header tag (e.g., "h1", "h2", "h3").
           '''

    def __repr__(self):
        """
        Returns a string representation of the BeautifulScraper object.
        """
        message = f"BeautifulScraper(url='{self.url}'"
        if self.articles:
            message += f", articles={{...}} ({len(self.articles)} entries))"
        else:
            message += ")"
        return message
