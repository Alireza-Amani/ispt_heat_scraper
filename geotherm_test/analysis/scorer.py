'''
This is the `scorer.py` file. It contains the `DecarbonizationScorer` class,
which is used to score text and AI-generated keywords based on their relevance
to decarbonization. The class takes a JSON file containing target keywords and
their associated scores as input and calculates the scores for the input text
and keywords.
'''
from pathlib import Path
import json
from ..utils import *


class DecarbonizationScorer:
    """
    Scores text and AI-generated keywords based on their relevance to decarbonization.

    The scorer uses a JSON file containing target keywords and their associated scores
    to evaluate the input text and keywords.

    Parameters
    ----------
    keywords_json : str | Path
        Path to the JSON file containing the target keywords and scores.

    Attributes
    ----------
    keywords_json : str | Path
        Path to the JSON file containing the target keywords and scores.
    target_keywords : dict
        Dictionary of target keywords and their associated scores loaded from the JSON file.
    text_score : int
        Score of the input text based on the presence of target keywords.
    ai_keywords_score : int
        Score of the AI-generated keywords based on their match with the target keywords.

    Raises
    ------
    AssertionError
        If the provided `keywords_json` file does not exist.

    Examples
    --------
    >>> scorer = DecarbonizationScorer("keywords.json")
    >>> text = "This is an example text about reducing carbon emissions."
    >>> ai_keywords = ["decarbonization", "renewable energy"]
    >>> text_score, ai_keywords_score = scorer(text, ai_keywords)
    >>> print(f"Text Score: {text_score}, AI Keywords Score: {ai_keywords_score}")
    """

    def __init__(self, keywords_json: str | Path):
        """
        Initializes the DecarbonizationScorer with the provided keywords JSON file.
        """
        self.keywords_json = keywords_json
        assert Path(keywords_json).exists(), f"File {
            keywords_json} does not exist."
        self.target_keywords = self._load_keywords(keywords_json)

        self.text_score = 0
        self.ai_keywords_score = 0

    def _load_keywords(self, keywords_json: str | Path) -> dict:
        """
        Loads the keywords and their scores from the JSON file.

        Parameters
        ----------
        keywords_json : str | Path
            Path to the JSON file.

        Returns
        -------
        dict
            Dictionary of keywords and scores.
        """
        with open(keywords_json, encoding='utf-8') as f:
            keywords = json.load(f)
        return keywords

    def _ai_keywords_score(self, ai_gen_keywords: list[str], weight: int = 2) -> int:
        """
        Calculates the score for the AI-generated keywords.

        Parameters
        ----------
        ai_gen_keywords : list[str]
            List of AI-generated keywords.
        weight : int, optional
            Weighting factor for the AI keywords score, by default 2.
        """
        for keygroup in self.target_keywords:

            group_keywords = self.target_keywords[keygroup].get('synonyms', [])
            group_score = self.target_keywords[keygroup].get("score", 0)

            if fuzzy_match_two_sets_keywords(chunk_keywords(ai_gen_keywords), group_keywords):
                self.ai_keywords_score += group_score * weight

    def _text_score(self, text: str) -> int:
        """
        Calculates the score for the input text.

        Parameters
        ----------
        text : str
            The input text to be scored.
        """
        for keygroup in self.target_keywords:

            group_keywords = self.target_keywords[keygroup].get('synonyms', [])
            group_score = self.target_keywords[keygroup].get("score", 0)

            for keyword in group_keywords:
                if number_of_hits := fuzzy_match_keyword(text, keyword):
                    self.text_score += number_of_hits * group_score

    def __call__(self, text: str, ai_gen_keywords: list[str] = None) -> tuple[int, int]:
        """
        Scores the input text and AI-generated keywords.

        Parameters
        ----------
        text : str
            The input text to be scored.
        ai_gen_keywords : list[str]
            List of AI-generated keywords.

        Returns
        -------
        tuple[int, int]
            A tuple containing the text score and the AI keywords score.
        """
        self._text_score(text)

        if ai_gen_keywords:
            self._ai_keywords_score(ai_gen_keywords)

        return self.text_score, self.ai_keywords_score

    def __repr__(self):
        return f"DecarbonizationScorer(target_keywords in {self.keywords_json})"
