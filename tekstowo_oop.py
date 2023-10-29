import argparse
import os
import string
import time
from datetime import datetime
from typing import Dict, List, Tuple

import langdetect
import requests
from bs4 import BeautifulSoup
from icecream import ic
from tqdm import tqdm


### CLASSES
class Scraper():

    # CLASS INIT
    def __init__(self):
        self.alphabet = list(string.ascii_uppercase) + ["pozostale"]
        #self.letter = "Q"
        #self.letter_url = f"https://www.tekstowo.pl/artysci_na,{self.letter}.html"

    # CLASS METHODS
    def max_page_number_lut(self, 
                            url: str) -> int:
        """
        Extract a maximium page number for given letter.

        Parameters:
            url (str): URL to look for maximum number in

        Returns:
            max_page (int): a maximum page number found
        """
        max_page = 0

        try:
            req = requests.get(url, timeout=60)
            req.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"An error occured: {e}")
            return max_page

        if req.ok:
            soup = BeautifulSoup(req.content, "lxml")

            if soup:
                for page in soup.find_all(class_="page-link"):
                    if page.text.isnumeric() and int(page.text) > max_page:
                        max_page = int(page.text)

        return max_page
    
    def max_page_number_letter(self, letter: str) -> dict:
        """
        Extract maximum page number for given letter
        Returns the value of the last page containing the songs
        per artist.
        """

        letter_max_page = 0

        if len(letter) < 2:
            ltr = letter.upper()

        url = f"https://www.tekstowo.pl/artysci_na,{ltr}.html"

        try:
            letter_max_page = self.max_page_number_lut(url)
            print(f"Letter {ltr} has {letter_max_page} pages of artists.")
        except Exception as e:
            print(f"An error has occured for letter {ltr}: {e}")

        return letter_max_page
    
    def create_lut_pagination(self) -> dict:
        """
        Creates a look-up table for each letter in the alphabet.

        Parameters:
            alphabet (str): a list of all letters and/or other 

        Returns:
            lut_letters (dict): contains a key/value pairs of alphabet 
                uppercase letters and maximum page number retrieved 
                for it.
        """

        lut_pages = {}

        print("Creating LUT, please wait...")

        for idx, letter in enumerate(tqdm(self.alphabet)):
            time.sleep(0.3)
            url = f"https://www.tekstowo.pl/artysci_na,{letter}.html"

            try:
                lut_pages[letter] = self.max_page_number_lut(url)
            except Exception as e:
                print(f"An error has occured for letter {letter}: {e}")

        print("LUT created")
        return lut_pages
    
    def get_artists(
        self,
        letter: str, 
        max_page_per_letter: Dict[str, int] or int
        ) -> Tuple[List[str], int]:
        
        """
        Scrape all of the artists starting with a given letter in the alphabet.

        Parameters:
            letter (str): a single capital letter from the alphabet
            max_page_per_letter (dict or int): a dictionary of key-value 
                pairs of capital letters with responding maximum number of
                pages

        Returns:
            urls (list): a list of artists' URLs for further scraping
            len(urls) (int): a total number of collected URLs
        """

        urls = []

        if isinstance(max_page_per_letter, dict):
            limit = max_page_per_letter[letter]
        elif isinstance(max_page_per_letter, int):
            limit = max_page_per_letter
        else:
            raise ValueError(
                "max_page_per_letter should be either a dictionary \
                with capital letters as keys and integers as values or a plain \
                integer value."
            )
        
        print(f"Collecting artists starting with a letter {letter}...")

        with tqdm(total=limit) as pbar:
            for page in range(1, limit + 1):
                url = f"https://www.tekstowo.pl/artysci_na,{letter},strona,{page}.html"

                try:
                    time.sleep(2)
                    response = requests.get(url, timeout=60)
                    if response.ok:
                        soup = BeautifulSoup(response.content, "lxml")
                        for link in soup.find_all("a"):
                            item = link.get("href")
                            if isinstance(item, str) and "piosenki_" in item:
                                urls.append("https://tekstowo.pl" + item)
                except Exception as e:
                    print(e)

                #print(f"{letter}: Visited {page}/{limit}")
                pbar.update(1)

        #print(f"{generate_timestamp()}: Letter {letter}: collected {len(urls)} artists")
        print(f"Letter {letter} artists collected.")

        return urls, len(urls)

    def get_artist_songs(
        self, 
        artist_url: str
        ) -> list:
        """
        Extract all the songs from a given artist.

        Parameters:
            artist_url (str): a URL leading to the artist's
            page

        Returns:
            A list of URLs to all of the songs from a given
            artist. 
        """
        urls = []
        processed_first_page = False

        while not processed_first_page:
            time.sleep(5)
            try:
                response = requests.get(artist_url, timeout=60)

                # Check for request success
                response.raise_for_status()

                soup = BeautifulSoup(response.content, "html.parser")
                songs = soup.find_all(class_="box-przeboje")
                artist = soup.find(class_="col-md-7 col-lg-8 px-0")
                artist = artist.text.split(" (")[0].strip()

                for song in songs:
                    song_title_element = song.find(class_="title")

                    if song_title_element:
                        if artist in song_title_element.text.strip():
                            song_url = "https://tekstowo.pl" + song_title_element["href"]
                            if (
                                not ".plpiosenka" in song_url
                                and song_url not in urls
                                and not "dodaj_tekst" in song_url
                            ):
                                urls.append(song_url)

                button_next_page = soup.find_all(class_="page-link")
                if button_next_page and len(button_next_page) > 0:
                    button_next_page = button_next_page[-1]

                    if "następna" in button_next_page.text.lower():
                        artist_url = "https://tekstowo.pl" + button_next_page["href"]
                    else:
                        break
                else:
                    break
            except requests.exceptions.RequestException as e:
                print(f"An error occurred during the HTTP request: {e}")
                return False
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                return False

        print(f"Artist {artist}, collected {len(urls)} song URLs")
        return urls
    
    def extract_song(self, song_url: str) -> Tuple[str]:
        """
        Scrapes the song (and song_translation if found) and its
        title from a given song_url.

        Parameters:
            song_url (str): a URL to a single song

        Returns:
            song (str): a string containing song's lyrics
            song_translation (str): a string containing 
                song's lyrics translated, returnd if found
            song_title (str): extrated song's title 
        """

        song = ""
        song_translation = None

        try:
            response = requests.get(song_url, timeout=60)
            if response.ok:
                # Scrape URL content with BeautifulSoup
                soup = BeautifulSoup(response.content, "lxml")

                # Song title
                song_title = soup.find(class_="col-lg-7").text.strip()

                # Original song
                song_html = soup.find(class_="inner-text")
                song = song_html.text.strip()

                # Translated version
                transl_html = soup.find("div", id="translation")
                song_translation = transl_html.text.strip().split("\t\t")[0]
        except Exception as e:
            print(e)

        return song, song_translation, song_title

    def assess_language(self, song_text: str) -> str:
        """
        Detect the language of provided song.

        Parameters:
            song_text (str): song's lyrics

        Returns:
            song_lang (str): 
        """
        if not isinstance(song_text, str):
            return False

        try:
            return langdetect.detect(song_text)
        except langdetect.lang_detect_exception.LangDetectException:
            return False

    def save_songs(self,
        title: str, 
        original_song: str, 
        translated_song: str, 
        lang_base: str, 
        lang_transl: str
    ):
        """
        Save the scraped song with corresponding languages
        and title.

        Parameters: 
            title (str): song title
            original_song (str): lyrics of a song to be saved
            translated_song (str): translated lyrics of a song
                to be saved
            lang_base (str): language of original lyrics
            lang_transl (str): language of translated lyrics, 
                returned if lyrics were present

        Returns:
            True (bool): if everything was processed properly
        """

        # Saving directory
        save_dir = "teksty/"
        os.makedirs(save_dir, exist_ok=True)

        # Title cannot have backslash in it
        clean_title = title.replace("/", "-")

        # Original song
        if isinstance(lang_base, str) and len(lang_base) < 3 and len(original_song) > 10:
            original_song_filename = f"{clean_title}__{lang_base.upper()}.txt"

            # Save to a file
            with open(
                os.path.join(save_dir, original_song_filename), "w", encoding="utf-8"
            ) as f:
                f.write(original_song)
                print(f"Song saved: {title}")
                #print(f"{generate_timestamp()}: Original successfully saved: {title}")
        else:
            #print(f"{generate_timestamp()}: Song {title} is too short or has no text.")
            print(f"{title}: Lyrics not found or empty")

        # Translated song
        if isinstance(lang_transl, str) and len(lang_transl) < 3 and len(translated_song) > 10:
            translated_song_filename = f"{clean_title}__TRAN__{lang_transl.upper()}.txt"

            # Save to a file
            with open(
                os.path.join(save_dir, translated_song_filename), "w", encoding="utf-8"
            ) as f:
                f.write(translated_song)
                #print(f"{generate_timestamp()}: Translation successfully saved: {title}")
        else:
            #print(f"{generate_timestamp()}: Translation not found or empty.")
            print(f"{title}: Translation not found or empty")
    
        return True

class Files():

    # CLASS INIT
    def __init__ (self):
        pass

    # CLASS METHODS


if __name__ == "__main__":

    ### PARSER
    parser = argparse.ArgumentParser(
    description="Crawler and scraper dedicated to tekstowo.pl domain"
    )

    parser.add_argument(
        "--letter",
        "--ARTIST_LETTER",
        help="Choose a letter to scrape the lyrics from (default = Q)",
        default="Q",
        type=str,
    )

    parser.add_argument(
        "--save_progress",
        "--SAVE_PROGRESS",
        help="Choose the interval of creating a save_progress file",
        default=30,
        type=int,
    )

    args = parser.parse_args()

    # Config
    ARTIST_LETTER: str = args.letter
    SAVE_PROGRESS: int = args.save_progress

    # Main scraping script
    tekstowo_scraper = Scraper()
    #tekstowo_scraper.max_page_number_letter(ARTIST_LETTER)
    #tekstowo_scraper.create_lut_pagination()

    urls, cnt = tekstowo_scraper.get_artists(ARTIST_LETTER, 2)

    for url in urls:
        songs = tekstowo_scraper.get_artist_songs(url)
        
        for song in songs:
            s, st, t = tekstowo_scraper.extract_song(song)

            s_t = tekstowo_scraper.assess_language(s)
            st_t = tekstowo_scraper.assess_language(st)

            tekstowo_scraper.save_songs(t, s, st, s_t, st_t)
