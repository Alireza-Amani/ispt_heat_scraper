'''
This file must be run to cache the models locally before running the main script.
'''
import os
import logging
from transformers import AutoModelForSeq2SeqLM

# Set logging level to INFO
logging.basicConfig(level=logging.INFO)

# for text summarization
MODEL_NAME_1 = "google/pegasus-cnn_dailymail"

# for keyword extraction
MODEL_NAME_2 = "Voicelab/vlt5-base-keywords"


def is_model_cached(model_name: str) -> bool:
    """Checks if the specified model is cached locally.

    Parameters
    ----------
    model_name : str
        The name of the model to check.

    Returns
    -------
    bool
        True if the model is cached, False otherwise.

    Examples
    --------
    >>> is_model_cached("bert-base-uncased")
    True
    """
    # Construct the expected cache directory path
    cache_dir = os.path.join(os.path.expanduser(
        "~"), ".cache", "huggingface", "hub", "models--"+model_name.replace("/", "--"))
    # Check if the directory exists
    return os.path.exists(cache_dir)


# Pre-cache the models if it's not already cached
for model_name_ in [MODEL_NAME_1, MODEL_NAME_2]:
    if not is_model_cached(model_name=model_name_):
        print(f"Caching model '{model_name_}'...")
        _ = AutoModelForSeq2SeqLM.from_pretrained(model_name_)
        print(f"Model '{model_name_}' has been cached.")
    else:
        print(f"Model '{model_name_}' is already cached.")
