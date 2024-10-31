'''
This file is used to install the package in the system.
'''
from setuptools import setup, find_packages

setup(
    name='ispt_heat_scraper',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'ipykernel',
        'validators',
        'beautifulsoup4',
        'requests',
        'ipywidgets==8.1.5',
        'jupyterlab-widgets==3.0.13',
        'widgetsnbextension==4.0.13',
        'transformers',
        'torch',
        'protobuf',
        'tiktoken',
        'tokenizers',
        'numpy',
        'sentencepiece'
    ],
    author='Alireza Amani',
    author_email='alireza.amani101@gmail.com',
    description='A small example system for scraping case studies from ISPT website',
)
