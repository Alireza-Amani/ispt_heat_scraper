# ISPT case study scraper

**A Python package for scraping and summarizing projects related to the decarbonization of the industrial heat
hosted on https://ispt.eu/  (Institute for Sustainable Process Technology).**

## Description

The package provides a class `IsptHeatScraper` that can be used to:
- Scrape the ISPT website for projects classified under the category "Heat" and extract the following information:
    - Project title
    - Project link
    - Project full description

- Determine the relevance of the projects to the decarbonization of the industrial heat by:
    - Looking for specific keywords in the project description
    - Comparing AI-extracted keywords from the project description to a list of predefined keywords

    (Refer to the [data](#data) section for more details on the predefined keywords)

- Use a pre-trained NLP (Natural Language Processing) model to summarize the project description

## Features

* Uses the `beautifulsoup4` library to scrape the ISPT website
* Uses the `transformers` library to
    - Summarize the project description (Google's Pegasus model)
    - Extract keywords from the project description (VLT5 model)

## Installation

    ```bash
    git clone URL
    cd ispt_heat_scraper
    pip install .
    ```

## Usage
Please refer to the [main notebook](main.ipynb) for running the system.

## Requirements
The list of required libraries can be found in the [requirements.txt](requirements.txt) file.
