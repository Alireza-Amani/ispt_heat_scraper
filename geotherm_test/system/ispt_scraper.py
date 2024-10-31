'''
The IsptHeatScraper class is a systematized way to scrape, analyze, and save case
 studies from the ISPT Heat project website.
'''
from datetime import datetime
from pathlib import Path
import validators
from ..scraping.scraper import BeautifulScraper
from ..analysis.case_study import CaseStudy
from ..analysis.scorer import DecarbonizationScorer


class IsptHeatScraper:
    """
    Scrapes case studies from the ISPT Heat project website, analyzes them for
    relevance to decarbonization, and saves the results to a CSV file.

    Attributes
    ----------
    case_studies_url : str
        URL of the page containing the list of case studies.
    cases_html_address : dict
        Dictionary specifying the HTML elements containing the case study links and titles.
        This should be in the format expected by `BeautifulScraper.find_articles_links_titles`.
    keyword_json : Path or str
        Path to a JSON file containing the keywords used for relevance scoring.
    output_dir : Path or str
        Path to the directory where the results will be saved.
    verbose : bool, optional
        Whether to print progress messages. Defaults to False.

    Methods
    -------
    run()
        Executes the scraping, analysis, and saving process.
    """

    def __init__(self, case_studies_url: str, cases_html_address: dict,
                 keyword_json: Path | str, output_dir: Path | str, verbose: bool = False):
        """
        Parameters
        ----------
        case_studies_url : str
            URL of the page containing the list of case studies.
        cases_html_address : dict
            Dictionary specifying the HTML elements containing the case study links and titles.
            This should be in the format expected by `BeautifulScraper.find_articles_links_titles`.
        keyword_json : Path or str
            Path to a JSON file containing the keywords used for relevance scoring.
        output_dir : Path or str
            Path to the directory where the results will be saved.
        verbose : bool, optional
            Whether to print progress messages. Defaults to False.
        """
        self.case_studies_url = case_studies_url
        self.cases_html_address = cases_html_address
        self.keyword_json = keyword_json
        self.output_dir = output_dir
        self.verbose = verbose

        self._assertions()

        # Initialize the scraper
        self.scraper = BeautifulScraper(
            url=self.case_studies_url, verbose=self.verbose)

        self.case_studies = []  # List of CaseStudy objects
        self.output_file = None  # Path to the output file

        print(f"Created a scraper for the ISPT Heat project case studies at {
              self.case_studies_url}.\n")

    def run(self, generate_ai_keywords: bool = False):
        """Executes the scraping, analysis, and saving process."""

        print("Starting the scraping process.\n")

        self._create_output_files()
        self._proccess_case_studies(generate_ai_keywords)
        self._save_results()

        print(f"Results saved in {self.output_file}")

    def _proccess_case_studies(self, generate_ai_keywords: bool):
        """Finds and processes the case studies."""
        self._find_case_studies()

        print("Processing the case studies.\n")

        for case_title, case_link in self.scraper.articles.items():
            case_ = CaseStudy(
                title=case_title,
                url=case_link,
                scorer=DecarbonizationScorer,
                target_keywords_json=self.keyword_json,
                generate_keywords=generate_ai_keywords,
            )
            self.case_studies.append(case_)

    def _save_results(self):
        """Saves the results to a CSV file."""
        with open(self.output_file, 'a', encoding="utf-8") as f:
            for case in self.case_studies:
                if case.summary is not None:
                    f.write(case.to_csv_row())
                    f.write("\n")

    def _find_case_studies(self):
        """Tasks the scraper to extract case study links and titles."""
        self.scraper.find_articles_links_titles(self.cases_html_address)

        print(f"Found {len(self.scraper.articles)} case studies.\n")

    def _create_output_files(self):
        """Creates the output CSV file."""
        self.output_file = Path(self.output_dir) / "results.csv"

        # If it exists, append the name with the current date and time
        if self.output_file.exists():
            now = datetime.now()
            dt_string = now.strftime("%d_%m_%Y_%H_%M_%S")
            self.output_file = Path(self.output_dir) / \
                f"results_{dt_string}.csv"

        # Write the header
        with open(self.output_file, 'w', encoding="utf-8") as f:
            f.write("Title,URL,Relevance Score (out of 100),Keywords,Summary\n")

    def _assertions(self):
        """Performs assertions to validate input parameters."""
        # Check if the case_studies_url is valid
        message = f"The given URL {self.case_studies_url} is invalid"
        assert validators.url(self.case_studies_url), message

        # Check if the keyword_json is a valid file
        message = f"The keywords' file {self.keyword_json} does not exist"
        assert Path(self.keyword_json).exists(), message

        # Check if the output_dir is a valid directory
        message = f"The output directory {self.output_dir} does not exist"
        assert Path(self.output_dir).is_dir(), message

    def __repr__(self):
        """Returns a string representation of the object."""
        return (
            f"{self.__class__.__name__}(\n"
            f"  case_studies_url='{self.case_studies_url}',\n"
            f"  cases_html_address={self.cases_html_address},\n"
            f"  keyword_json='{self.keyword_json}',\n"
            f"  output_dir='{self.output_dir}',\n"
            f"  verbose={self.verbose}\n"
            ")"
        )
