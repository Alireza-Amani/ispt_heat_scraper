# A prototype system for scraping and summarizing projects related to the decarbonization of the industrial heat

I am interested in the projects relevant to the decarbonization of the industrial heat hosted on the [ISPT (the Institute for Sustainable Process Technology) website](https://ispt.eu/). One can access these projects by navigating to [Heat projects](https://ispt.eu/projects/?theme-tag=heat).

I designed a Python package, named *ispt_heat_scraper*, do automate the search for these projects. ispt_heat_scraper uses `beautifulsoup4` and `requests` libraries to scrape the ISPT website and extract the title, link, and full description of the search result.
* I choose bs4 (over more advanced libraries like Selenium) because it is lightweight and sufficient for the task at hand.

The next step is to determine the relevance of the projects to our focus area. I used two methods (methods A and B) for this both of which depend of a list of pre-defined target keywords.
These keywords are grouped under different category, each category given different score, and are stored in a [json file](../data/keywords.json). These keywords are based on two important peer-reviewed papers, which I will quote the highlighted text chunks below.
- [To decarbonize industry, we must decarbonize heat](https://www.sciencedirect.com/science/article/pii/S2542435120305754)
    > **R&D pathways**

    > In this section, we discuss four pathways for decarbonizing heat production, as illustrated in Figure 3:

    > 1.  **Zero-carbon fuels**
    > 2.  **Zero-carbon heat sources**
    > 3.  **Electrification of heat**
    > 4.  **Better heat management**
- [Assessing the potential of decarbonization options for industrial sectors](https://www.sciencedirect.com/science/article/pii/S2542435124000266)
   > The key abatement options considered to decarbonize industrial processes are highlighted in Figure 1, which include the following:

    > *   **Switching to low-carbon fuel/energy supply:** this includes using alternative low-carbon fuel for industries such as hydrogen (green and blue hydrogen, and biohydrogen), biomass (includes waste and virgin biomass, and biomass fuels), or low-carbon electricity.
    > *   **Carbon capture and storage (CCS):** these are plants used to capture combustion- and process-related CO2 emissions from industry. The captured emissions are then stored underground.
    > *   **Process modification or alternative low-carbon novel processes:** some industrial commodities can be produced using alternative and novel production routes to save emissions (such as secondary aluminum production using microwave drying in paper production). Deploying novel processes is sometimes accompanied by fuel switching, depending on the nature of the industrial process.
    > *   **Resource and energy efficiency (REE):** these refer to technologies or practices used to reduce emissions by using fewer raw materials (example: recycling), or enabling the use of emissions-free materials, or by using less energy to produce a product. Finding specific data about REE for each process is challenging. Therefore, we note the limitation of our paper regarding this.

The method A uses the target keywords and look for similar (Python's `difflib` library) or exact match in the project description and uses the predefined scores to calculate the relevance score (0-100) of the project to the decarbonization of the industrial heat. The method B uses a pre-trained NLP model (VLT5) to extract keywords from the project description and compare them to the target keywords to calculate the relevance score. A hit in the method B is given the double score of the method A. This is because I assume that the extracted keywords are the main focus of the project.

The final step is to summarize the project description. I used a pre-trained NLP model (Google's Pegasus) to summarize the project description. This is a powerful model that is trained using the CNN/DailyMail dataset to generate abstractive summaries of news articles. Please refer to the [huggingface documentation](https://huggingface.co/google/pegasus-cnn_dailymail) for more information.
The output of the system is a comma-separated file (CSV) that contains the following columns:

- Project title
- Project link
- Relevance score
- Keywords extracted from the project description
- Summary of the project description (only for the projects with relevance score > 50)


## Future work and limitations:
- The current web scraper does not support pagination.
- The current system does not support the extraction of the project's image.
- A more robust/dynamic set of parameter is required for the summarization model. For instance, the maximum length of the summary, the minimum length of the summary, etc.
- The NLP models can be fine-tuned to:
    - Extract more relevant keywords
    - Generate summaries in a custom format/length
    - Generate more accurate/appropriate summaries of scientific/technical texts
- The system can be extended to other websites with similar structures or potentially use APIs to extract the data.
- The system can be extended to support other output formats (e.g., JSON, Excel, etc.) or other storage options (e.g., database).
- Include unit tests. 
