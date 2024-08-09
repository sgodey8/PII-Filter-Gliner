# PII Filter Gliner

This readme is meant for fixed1.py and fixed2.py. This program filters out Personally Identifiable Information (PII) from text and calculates performance metrics for the filtering process.

## Description

The PII Filter uses regular expressions and the spaCy NLP library to identify and redact personally identifiable information from text data. It processes text to detect entities like names, dates, email addresses, phone numbers, and other sensitive information, replacing them with a <FILTERED> placeholder. The program also calculates performance metrics such as precision, recall, and F1-score to evaluate the effectiveness of the PII filtering.

## Getting Started

### Dependencies

* Windows 10 or higher
* Minimum required: Python 3.6
* Recommended: Python 3.8 or higher
* Required libraries: json, re, spacy

### Installing

* The code is in the fixed1.py and fixed2.py
* Copy the code and put it into your program
* Download the datasets as well
* dataset1.json goes with the code from fixed1.py and dataset2.json goes with fixed2.py
```
pip install spacy
python -m spacy download en_core_web_sm
```

### Executing program

* After copying the code make sure you also have dataset
* Make sure the dataset is named properly as the code is expecting a file named dataset1.json or dataset2.json depending on the the program you are using
* After you install the libraries you can run the program

## Help

* If you encounter a FileNotFoundError, ensure that your input JSON file is in the correct location as specified in the file_path variable.
* If you get a ModuleNotFoundError for 'spacy', make sure you've installed it:
```
pip install spacy
```

## Authors

Shreeyan Godey
shreeyan.godey@gmail.com

## Version History

* 0.1
    * Initial Release

## License

This project is licensed under the Apache License version 2.0.

## Acknowledgments

Dhar Rawal guided me through making this

## Medium Blog

* https://medium.com/@shreeyan.godey/pii-filter-implementation-adff4b80b981
