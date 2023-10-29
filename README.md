
# speakleash-dedicated-web-crawlers

A collection of web crawlers dedicated to a given website/domain

## Lyrics Scraper for [tekstowo.pl](https://tekstowo.pl)  

This Python script scrapes lyrics data from the tekstowo.pl website for artists whose names start with a specified letter.

### Table of Contents

* Introduction
* Features
* Usage
* Requirements
* Installation
* Configuration
* How to Run
* Contributing
* License

### Introduction

This script is designed to scrape song lyrics and related information for artists whose names start with a given letter from the tekstowo.pl website. It utilizes web scraping techniques to collect lyrics data for further analysis or use.

### Features

* Web scraping of song lyrics and related information from tekstowo.pl.
* Options to specify the starting letter for artists' names and the save progress interval.

### Usage

1. Clone or download the repository to your local machine.
2. Install the required packages using pip or your preferred package manager.
3. Configure the scraping parameters as needed.
4. Run the script to start scraping song lyrics from tekstowo.pl.

### Requirements

* Python 3.x
* BeautifulSoup
* requests
* langdetect

You can install the required packages using pip:

```bash
pip install bs4 requests langdetect
```

### Installation

1. Clone the repository:

```bash
git clone git@github.com:speakleash/speakleash-dedicated-web-crawlers.git
cd speakleash-dedicated-web-crawlers
```

2. Install the required packages as mentioned in the Requirements section.

### Configuration  

You can configure the scraping parameters using command-line arguments:

* `--letter` or `--ARTIST_LETTER`: Choose a letter to scrape the lyrics from (default = Q).
* `--save_progress` or `--SAVE_PROGRESS`: Choose the interval for creating a save_progress file (default = 30).

### How to Run  

Run the script using Python and specify the desired options:

```bash
python tekstowo.py --letter <letter> --save_progress <interval>
```

Replace `<letter>` with the starting letter for artists' names, and `<interval>` with the desired save progress interval.

### Contributing

Contributions are welcome! Feel free to open an issue or create a pull request.

### License

This project is licensed under the MIT License.
