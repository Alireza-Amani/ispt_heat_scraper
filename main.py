# Imports ----------------------------------------------------------------------
from pathlib import Path
from geotherm_test.system.ispt_scraper import IsptHeatScraper
# ______________________________________________________________________________

# Variables --------------------------------------------------------------------

# the address of the website where the projects are listed
WEBURL = "https://ispt.eu/projects/?theme-tag=heat"

# the html (elemental) address of the projects on the website
projects_html_address = {
    'container_tag': 'article',
    'title': {'tag': 'h2', 'attr': {'class': 'entry-title'}},
    'link': {'tag': 'a', 'attr': {'class': 'post-block-wrapper'}, 'type': 'href'},
}

# the target keywords, for the sake of relevance check, are stored in a json file
KEYWRODS_JSON_FILE = Path("./data/keywords.json")

# the output directory where the search results will be stored as a csv file
OUTPUT_DIR = Path("./output")

# either to generate keywords using the VLT5 (AI) model or not
GENERATE_KEYWORDS = True

# verbose mode
VERBOSE = True
# ______________________________________________________________________________

# Main -------------------------------------------------------------------------

# create an instance of the system
ispt_heat_scraper = IsptHeatScraper(
    case_studies_url=WEBURL,
    cases_html_address=projects_html_address,
    keyword_json=KEYWRODS_JSON_FILE,
    output_dir=OUTPUT_DIR,
    verbose=VERBOSE
)

# run the system
ispt_heat_scraper.run(GENERATE_KEYWORDS)
