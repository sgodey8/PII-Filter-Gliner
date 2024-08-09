# PII Filter Gliner

This program filters out PII(Personally Identifiable Information) from text and returns it replacing the sensitive words with placeholders.

## Description

The PII Filter Gliner uses the GLiNER model to identify and redact personally identifiable information from text data. It processes text data to detect entities like names, addresses, and other sensitive information, replacing them with a <FILTERED> placeholder. The program also calculates performance metrics such as precision, recall, and F1-score to evaluate the effectiveness of the entity recognition.

## Getting Started

### Dependencies

* Windows 10 or higher
* Minimum required: Python 3.6
* Recommended: Python 3.8 or higher
* Required libraries: json, gliner, numpy

### Installing

* The code is in the gliner1.py and gliner2.py
* Copy the code and put it into your program
* Download the datasets as well
* dataset1.json goes with the code from gliner1.py and vice versa
```
pip install gliner
pip install json
pip install numpy
```

### Executing program

* After copying the code make sure you also have dataset
* Make sure the dataset is named properly as the code is expecting a file named dataset1.json
* After you install the libraries you can run the program

## Help

* FileNotFoundError: Ensure that your 'datasets.json' file is in the 'datasets' folder in the same directory as your script.
* ModuleNotFoundError: If you get this error for 'gliner', make sure you've installed it:
```
pip install gliner
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

* Dhar Rawal was a great help all throughout creating this code and guided me if I got stuck anywhere.

## Medium Blog

* https://medium.com/@shreeyan.godey/pii-filter-implementation-adff4b80b981
