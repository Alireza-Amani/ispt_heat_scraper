from transformers import pipeline
from transformers import T5Tokenizer, T5ForConditionalGeneration


def summarize_google_pegasus(text: str, min_length: int = 60, max_length: int = 100, device: str = "cpu"):
    """Summarizes text using the Google Pegasus model.

    This function utilizes the `google/pegasus-cnn_dailymail` model from
    Hugging Face Transformers to generate a concise summary of the input text.

    Parameters
    ----------
    text : str
        The text to be summarized.
    min_length : int, optional
        The minimum length of the summary in words. Default is 60.
    max_length : int, optional
        The maximum length of the summary in words. Default is 100.
    device : str, optional
        The device to run the model on ('cpu', 'cuda', 'mps', etc.).
        Default is 'cpu'.

    Returns
    -------
    str
        The generated summary of the input text.

    Raises
    ------
    OSError
        If the model is not found or cannot be loaded.
    ValueError
        If the input `text` is invalid or empty.

    Examples
    --------
    >>> text = "This is an example article with a lot of text. It discusses various topics and goes into detail about each one. The goal is to see how well the summarizer can condense this information."
    >>> summarize_google_pegasus(text)
    'This is an example article with a lot of text. It discusses various topics and goes into detail about each one. The summarizer can condense this information.'
    """

    MODEL_NAME = "google/pegasus-cnn_dailymail"

    try:
        summarizer = pipeline("summarization", model=MODEL_NAME,
                              tokenizer=MODEL_NAME, device=device)
        summary = summarizer(text, min_length=min_length,
                             max_length=max_length)
    except Exception as e:
        raise OSError(f"Error using the model '{MODEL_NAME}': {e}") from e

    summary = summary[0]['summary_text'].replace("<n>", "\n")

    return summary


def extract_keywords_vlt5(text: str, device: str = "cpu"):
    """Extracts keywords from text using the VLT5 model.

    This function utilizes the `Voicelab/vlt5-base-keywords` model from
    Hugging Face Transformers to identify and extract relevant keywords
    from the input text.

    Parameters
    ----------
    text : str
        The text from which to extract keywords.

    device : str, optional
        The device to run the model on ('cpu', 'cuda', 'mps', etc.).
        Default is 'cpu'.

    Returns
    -------
    list
        A list of extracted keywords from the input text.

    Raises
    ------
    Exception
        If the model is not found or cannot be loaded.

    Examples
    --------
    >>> text = "This is an example text about machine learning and natural language processing."
    >>> extract_keywords_vlt5(text)
    'machine learning, natural language processing, artificial intelligence'
    """
    MODEL_NAME = "Voicelab/vlt5-base-keywords"
    TASK_PREFIX = "Keywords: "

    try:
        model = T5ForConditionalGeneration.from_pretrained(
            MODEL_NAME).to(device)
        tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME, legacy=False)

        input_sequences = [TASK_PREFIX + text]
        input_ids = tokenizer(
            input_sequences, return_tensors="pt", truncation=False).input_ids.to(device)

        output = model.generate(
            input_ids,
            no_repeat_ngram_size=3,
            num_beams=4,
            max_length=120,
            min_length=60,
        )
        predicted_keywords = tokenizer.decode(
            output[0], skip_special_tokens=True)

    except Exception as e:
        raise OSError(f"Error using the model '{MODEL_NAME}': {e}") from e

    keywords_list = predicted_keywords.split(",")

    # remove leading/trailing whitespace and empty strings
    keywords_list = [keyword.strip() for keyword in keywords_list if keyword]

    return keywords_list
