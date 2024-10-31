'''
This module contains the CaseStudy class, which analyzes a case study to determine its relevance to decarbonization.
The class fetches the HTML content from the given URL, extracts the relevant text, generates keywords (optional),
determines relevance, and summarizes (if relevant).
'''
from pathlib import Path
import logging
from .scorer import DecarbonizationScorer
from ..summarization.summarizer import summarize_google_pegasus, extract_keywords_vlt5
from ..utils import *

# Suppress the warning about missing weights
logging.getLogger("transformers").setLevel(logging.ERROR)


class CaseStudy:
    """
    Analyzes a case study to determine its relevance to decarbonization.

    Parameters
    ----------
    title : str
        Title of the case study.
    url : str
        URL of the case study.
    scorer : DecarbonizationScorer
        Scorer object to assess relevance.
    target_keywords_json : Path | str
        Path to target keywords JSON file.
    generate_keywords : bool, optional
        Whether to generate keywords. Defaults to False.
    verbose : bool, optional
        Whether to print verbose output. Defaults to False.

    Attributes
    ----------
    title : str
        Title of the case study.
    url : str
        URL of the case study.
    generate_keywords : bool
        Whether to generate keywords.
    scorer : DecarbonizationScorer
        Scorer object to assess relevance.
    target_keywords_json : Path | str
        Path to target keywords JSON file.
    verbose : bool
        Whether to print verbose output.
    _html_content : str
        HTML content of the case study.
    text : str
        Extracted text from the case study.
    summary : str
        Summary of the case study.
    keywords : list
        Keywords extracted from the case study.
    relevant_to_decarbonization : str
        Relevance to decarbonization ("Relevant", "Possibly Relevant", or "Unrelated").
    relevance_score : int
        Relevance score (0-100).
    """

    def __init__(self, title: str, url: str, scorer: DecarbonizationScorer,
                 target_keywords_json: Path | str, generate_keywords: bool = False,
                 verbose: bool = False):

        self.title = title
        self.url = url
        self.generate_keywords = generate_keywords
        self.scorer = scorer(target_keywords_json)
        self.target_keywords_json = target_keywords_json
        self.verbose = verbose

        self._html_content = ""
        self.text = ""
        self.summary = ""
        self.keywords = []
        self.relevant_to_decarbonization = None
        self.relevance_score = 0

        self._analyze_content()

    def _analyze_content(self):
        """
        Orchestrates the analysis process.

        Fetches content, extracts text, generates keywords (optional),
        determines relevance, and summarizes (if relevant).
        """
        self._get_html_content()
        self._get_text()

        if self.generate_keywords:
            self._extract_keywords()

        self._determine_relevance()

        if self.verbose:
            self._print_analysis_details()

        if self.relevance_score >= 50:
            self._summarize()

    def _get_html_content(self):
        """Fetches the HTML content from the given URL."""
        self._html_content = get_page_body(self.url)

    def _get_text(self):
        """Extracts the relevant text from the HTML content."""
        self.text = extract_ispt_article_text(self._html_content)

    def _summarize(self, device: str = "cpu"):
        """
        Summarizes the extracted text.

        Parameters
        ----------
        device : str, optional
            Device to use for summarization. Defaults to "cpu".
        """
        if self.verbose:
            print("Summarizing the text...")
        self.summary = summarize_google_pegasus(self.text, device=device)

    def _extract_keywords(self, device: str = "cpu"):
        """
        Extracts keywords from the text.

        Parameters
        ----------
        device : str, optional
            Device to use for keyword extraction. Defaults to "cpu".
        """
        self.keywords = extract_keywords_vlt5(self.text, device=device)

    def _determine_relevance(self):
        """Calculates the relevance score and categorizes the case study."""
        self.relevance_score = max(self.scorer(self.text, self.keywords))
        self.relevance_score = max(0, min(100, self.relevance_score))

        if self.relevance_score >= 50:
            self.relevant_to_decarbonization = "Relevant"
        elif self.relevance_score >= 25:
            self.relevant_to_decarbonization = "Possibly Relevant"
        else:
            self.relevant_to_decarbonization = "Unrelated"

    def _print_analysis_details(self):
        """Prints details of the analysis if verbose is True."""
        print(f"CaseStudy: {self.title} has been created.")
        if self.generate_keywords:
            print("Keywords generated using VLT5 model.")
        print(f"Relevance Score: {self.relevance_score}")
        print(f"Relevance to Decarbonization: {
              self.relevant_to_decarbonization}")

    def to_csv_row(self):
        """
        Returns a comma-separated string representation of the CaseStudy,
        including title, URL, relevance, keywords, and summary (if available).

        Returns
        -------
        str
            Comma-separated string with case study information.
        """
        keywords_str = "; ".join(self.keywords) if self.keywords else ""
        summary_str = self.summary.replace(",", ";") if self.summary else ""
        return f'"{self.title}","{self.url}",{self.relevance_score},"{keywords_str}","{summary_str}"'

    def __repr__(self):
        """Returns a string representation of the CaseStudy object."""
        message = f"CaseStudy(title={self.title}, url={self.url})"

        if self.summary:
            message += f"\nSummary:\n {self.summary}\n\n"
        else:
            message += f"\nText: {self.text[:100]}...\n\n"

        if self.keywords:
            message += f"Keywords: {self.keywords}\n"
        message += f"({self.relevant_to_decarbonization} to the decarbonization theme)"

        return message
