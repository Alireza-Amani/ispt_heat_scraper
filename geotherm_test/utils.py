'''
This module contains utility functions for web scraping and text processing.
'''
import re
from difflib import SequenceMatcher
from copy import deepcopy
import requests
from bs4 import BeautifulSoup
from bs4 import element, Comment
import validators


def remove_unwanted_elements(html_content: element.Tag) -> element.Tag:
    """
    Removes unwanted elements and comments from a BeautifulSoup object.

    Parameters
    ----------
    html_content : element.Tag
          The BeautifulSoup object to clean.

    Returns
    -------
    bs4.BeautifulSoup
        The cleaned BeautifulSoup object.
    """
    html_content = deepcopy(html_content)
    decomposable_elements = [
        "script", "style", "noscript", "nav", "form", "footer",
    ]

    for tag in decomposable_elements:
        for element_ in html_content.find_all(tag):
            element_.decompose()

    # Remove comments
    for element_ in html_content(text=lambda text: isinstance(text, Comment)):
        element_.extract()

    return html_content


def get_page_body(url: str) -> element.Tag:
    """
    Requests a page and returns the parsed body element.

    Parameters
    ----------
    url : str
        The URL of the page to request.

    Returns
    -------
    element.Tag
        The body element of the page.
    """

    # Request the page
    response = requests.get(url, timeout=10)

    # raise an exception if the request failed
    response.raise_for_status()

    # Parse the page
    parsed_page = BeautifulSoup(response.content, "html.parser")

    # Find the body tag and clean it
    body_tag = parsed_page.find("body")
    cleaned_body = remove_unwanted_elements(body_tag)

    # Return the body element
    return cleaned_body


def log_and_print(message: str, logger=None, verbose: bool = False):
    """
    Logs and prints a message.

    Parameters
    ----------
    message : str
        The message to log and print.
    logger : logging.Logger, optional
        The logger to log the message to. If None, the message is not logged. The default is None.
    verbose : bool, optional
        Whether to print the message. The default is False.
    """

    # Log the message
    if logger is not None:
        logger.info(message)

    # Print the message
    if verbose:
        print(message)


def extract_article_info(article_tag, title_config, link_config):
    """
    Extracts the title and link from an article element.

    Parameters
    ----------
    article_tag : bs4.element.Tag
        The article element to extract information from.
    title_config : dict
        Configuration for finding the title, containing 'tag' and 'attr' keys.
    link_config : dict
        Configuration for finding the link, containing 'tag' and 'attr' keys.

    Returns
    -------
    tuple or None
        A tuple containing the title and link if found, otherwise None.
    """
    try:
        # Find the title and link within the article tag
        title = article_tag.find(
            title_config['tag'], attrs=title_config['attr']).text
        link_tag = article_tag.find(
            link_config['tag'], attrs=link_config['attr'], href=True)

        # Validate the link
        link = link_tag['href'] if link_tag and validators.url(
            link_tag['href']) else None

        if link and title:
            return title, link
        else:
            return None

    except requests.exceptions.Timeout:
        message = "The request timed out."
        print(message)
        return None
    except requests.exceptions.RequestException as e:
        message = f"An error occurred: {e}"
        print(message)
        return None


def extract_articles(container, title_config, link_config):
    """
    Extracts article information from a container element.

    Parameters
    ----------
    container : bs4.element.Tag
        The container element holding the articles.
    title_config : dict
        Configuration for finding the title within each article.
    link_config : dict
        Configuration for finding the link within each article.

    Returns
    -------
    dict
        A dictionary mapping article titles to their links.
    """
    # store the articles in a dictionary
    articles = {}

    # iterate over each article element in the container
    for article in container:
        article_info = extract_article_info(article, title_config, link_config)

        # if the article information was found, add it to the dictionary
        if article_info:
            title, link = article_info
            articles[title] = link

    return articles


def extract_ispt_article_text(parsed_html_content):
    """Extracts and formats the main text content of an article hosted by ISPT.

    Parameters
    ----------
    parsed_html_content : element.Tag
        The parsed HTML content of the article to be processed.

    Returns
    -------
    str
        A formatted string containing the extracted main article text, organized
        by title, introduction, headings, and paragraphs.

    Raises
    ------
    AttributeError
        If the `parsed_html_content` is invalid or does not contain the expected elements.
    """

    # limit to article content
    parsed_html_content = parsed_html_content.select_one("article")

    # Title (assuming it's within the main content)
    title = parsed_html_content.select_one("h1.entry-title").text.strip()

    # Introduction
    intro_paragraph = parsed_html_content.select_one("p.is-style-intro")
    introduction = intro_paragraph.text.strip() if intro_paragraph else ""

    # Initialize output string with title and introduction
    output_string = f"{title}\n\n{introduction}\n\n"

    # Headings and content
    current_heading = None

    # Extract headings and paragraphs, excluding the introduction
    for element_ in parsed_html_content.select("h2.wp-block-heading, p:not(.is-style-intro), ul"):
        if element_.name == "h2":
            current_heading = element_.text.strip()
            output_string += f"{current_heading}\n"
        elif element_.name == "ul":
            # Handle lists by extracting list items with newlines
            for item in element_.find_all("li"):
                output_string += f"- {item.get_text(strip=True)}\n"
        elif current_heading:
            output_string += f"{element_.text.strip()}\n"

    return output_string


def fuzzy_match_keyword(text: str, keyword: str, threshold: float = 0.8, verbose: bool = False) -> int:
    """Fuzzy matches a keyword or a phrase (multiple keywords) within a text.

    Parameters
    ----------
    text : str
        The text to search within.
    keyword : str
        The keyword or phrase to search for.
    threshold : float, optional
        The similarity threshold (between 0 and 1). Default is 0.8.
    verbose : bool, optional
        Whether to print matching information. Default is False.

    Returns
    -------
    int
        The number of times the keyword(s) were found in the text.

    Examples
    --------
    >>> fuzzy_match_keyword("This is a test string", "tets", num_keywords=1) # "tets" is similar to "test"
    1
    >>> fuzzy_match_keyword("This is another test", "another test", num_keywords=2)
    1
    """

    # Preprocess text and keyword: lowercase and remove special characters
    text = re.sub(r'[^\w\s]', '', text).lower()
    keyword = re.sub(r'[^\w\s]', '', keyword).lower()

    # split the keyword/text into words
    text_words = text.split()
    keyword_words = keyword.split()

    # determine the number of keywords
    num_keywords = len(keyword_words)

    # Initialize the number of hits
    number_of_hits = 0

    if num_keywords == 1:  # Single keyword matching
        for word in text_words:
            # Calculate similarity ratio
            ratio = SequenceMatcher(None, keyword, word).ratio()
            if ratio >= threshold:  # Check if ratio exceeds threshold
                number_of_hits += 1

            if number_of_hits > 0:
                if verbose:
                    print("Matched keyword:", word)
                    print("Similarity:", ratio)
                return number_of_hits

        if verbose:
            print(f"No match found for keyword: '{keyword}'")

        return False  # No match found

    else:  # Multiple keyword matching
        # Iterate through possible keyword chunks
        for i in range(len(text_words) - num_keywords + 1):
            text_chunk = text_words[i: i + num_keywords]
            avg_ratio = 0
            for j in range(num_keywords):
                # Calculate ratio for each keyword
                ratio = SequenceMatcher(
                    None, keyword_words[j], text_chunk[j]).ratio()
                avg_ratio += ratio
            avg_ratio /= num_keywords  # Calculate average similarity ratio
            if avg_ratio >= threshold:  # Check if average ratio exceeds threshold
                number_of_hits += 1

            if number_of_hits > 0:
                if verbose:
                    print("Matched keyword:", " ".join(text_chunk))
                    print("Similarity:", avg_ratio)

                return number_of_hits

        if verbose:
            print(f"No match found for keyword: '{keyword}'")

        return number_of_hits

# get two sets of keywords and fuzzy match them


def fuzzy_match_two_sets_keywords(keywords_set_1: set, keywords_set_2: set, threshold: float = 0.85, verbose: bool = False) -> int:
    """Fuzzy matches two sets of keywords.

    Parameters
    ----------
    keywords_set_1 : set
        The first set of keywords to match.
    keywords_set_2 : set
        The second set of keywords to match.
    threshold : float, optional
        The similarity threshold (between 0 and 1). Default is 0.8.
    verbose : bool, optional
        Whether to print matching information. Default is False.

    Returns
    -------
    int
        The number of times the keywords from set 1 were found in set 2.

    Examples
    --------
    >>> fuzzy_match_two_sets_keywords({"machine learning", "natural language processing"}, {"machine learning", "deep learning"})
    1
    """

    # Initialize the number of hits
    number_of_hits = 0

    # Iterate through keywords in the first set
    for keyword_1 in keywords_set_1:
        # Iterate through keywords in the second set
        for keyword_2 in keywords_set_2:
            # Calculate similarity ratio
            ratio = SequenceMatcher(None, keyword_1, keyword_2).ratio()
            if ratio >= threshold:  # Check if ratio exceeds threshold
                number_of_hits += 1

            if number_of_hits > 0:
                if verbose:
                    print("Matched keywords:", keyword_1, keyword_2)
                    print("Similarity:", ratio)

                return number_of_hits

    if verbose:
        print("No match found for the two sets of keywords.")

    return number_of_hits


def fuzzy_match_two_sets_keywords(keywords_set_1: set, keywords_set_2: set, threshold: float = 0.85, verbose: bool = False) -> bool:
    """Fuzzy matches two sets of keywords.

    Parameters
    ----------
    keywords_set_1 : set
        The first set of keywords to match.
    keywords_set_2 : set
        The second set of keywords to match.
    threshold : float, optional
        The similarity threshold (between 0 and 1). Default is 0.8.
    verbose : bool, optional
        Whether to print matching information. Default is False.

    Returns
    -------
    bool
        True if a match is found, False otherwise.

    Examples
    --------
    >>> fuzzy_match_two_sets_keywords({"machine learning", "natural language processing"}, {"machine learning", "deep learning"})
    True
    """

    # process the keywords
    keywords_set_1 = {keyword.lower() for keyword in keywords_set_1}
    keywords_set_2 = {keyword.lower() for keyword in keywords_set_2}

    # Iterate through keywords in the first set
    for keyword_1 in keywords_set_1:
        # Iterate through keywords in the second set
        for keyword_2 in keywords_set_2:
            # Calculate similarity ratio
            ratio = SequenceMatcher(None, keyword_1, keyword_2).ratio()
            if ratio >= threshold:  # Check if ratio exceeds threshold
                if verbose:
                    print("Matched keywords:", keyword_1, keyword_2)
                    print("Similarity:", ratio)

                return True

    if verbose:
        print("No match found for the two sets of keywords.")

    return False


def chunk_keywords(keywords):
    """Chunks a set of keywords into sets of 1 and 2-word combinations.

    Parameters
    ----------
    keywords : set of str
        A set of keywords.

    Returns
    -------
    set of str
        A set of strings, where each string is a 1-word or 2-word combination
        from the input keywords.

    Examples
    --------
    >>> keywords = {
    ...     "carbon capture technology",
    ...     "solar energy",
    ...     "wind power",
    ... }
    >>> chunk_keywords(keywords)
      {
          "carbon",
          "capture",
          "carbon capture",
          "technology",
          "solar",
          "energy",
          "wind",
          "power",
      }
    """

    # Initialize the set of chunked keywords
    chunked_keywords = set()

    # Iterate through each keyword
    for keyword in keywords:
        # Split the keyword into words
        words = keyword.split()
        for i, word in enumerate(words):
            chunked_keywords.add(word)  # Add single word

            # Add word pair if not the last word
            if i < len(words) - 1:
                chunked_keywords.add(f"{word} {words[i + 1]}")  # Add word pair
    return chunked_keywords
