#coding=utf-8
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from requests.models import PreparedRequest
import requests.exceptions
import requests
from collections import Counter
from bs4 import BeautifulSoup
from string import punctuation
from re import split as regex_split

class FrequencyKeywordException(Exception):
    """Class for specyfic exception from FrequencyKeyword """

class FrequencyKeywords:
    """Calculate Frequency of keywords in visible content of website.
        Similar to finding word (Ctrl+F) in webrowser but only for keywords from HTML meta tag.

    Args:
        url: (str) url of webiste.

    Attributes:
        url: (str) address url of webiste given by user
        frequeny: (dict) frequency of keywords
        status_code :(int) status of htttp response from website
        keywords: (list) keywords from meta tag from website

    Raises:
        FrequencyKeywordException: If website url is broken, or can't get data from webiste page

    """
    def __init__(self, url):
        self.url = url
        self.frequency, self.status_code  = self.get_keywords_frequency(url)
        self.keywords = list(self.frequency.keys()) if self.frequency else None

    @staticmethod
    def get_keywords_frequency(url):
        """Calculate Frequency of keywords from meta tag in visible HTML tags.

        Args:
            url: (str) url of webiste.

        Returns:

            frequeny: (dict) frequency of keywords from visible HTML tags.
            status_code : (int) status code from GET request on page

        """
        CHUNK_SIZE = 8096
        UNVISIBLE_TAGS = [ "th", "td","strong","noscript","id", "iframe", "label",
            "br","class", "base","span" , "title", "button", "script", "style", 
            "ul", "small", "div", "meta", "nav", "time", "tbody", "tr", "body", 
            "img", "code",  "form", "header","pre", "input", "body", "section", 
            "em", "td", "link", "fieldset", "blockquote"]

        keyword_counter = Counter()
        keywords = []
        status_code = None

        FrequencyKeywords.check_url(url)

        get_response = requests.get(url, stream=True) #stream for big files
        status_code = get_response.status_code

        for chunk in get_response.iter_content(CHUNK_SIZE):
            html = BeautifulSoup(chunk, 'html.parser')
            for elem in html.find_all(True, recursive=True):
                if elem.find('meta'):
                    tmp_k = FrequencyKeywords.get_keywords_meta(elem)
                    if tmp_k:
                        keywords = tmp_k
                else:
                    if elem.name not in UNVISIBLE_TAGS:
                        key_words_list = FrequencyKeywords.get_keyword_list(elem.find(text=True, recursive = False), keywords)
                        if key_words_list:
                            keyword_counter.update(key_words_list)
                elem.extract()

        if not keywords:
            return None, status_code
        
        frequency = {}
        for key, value in keyword_counter.items():
            if key in keywords:
                frequency[key] = value
        return frequency, status_code

    @staticmethod
    def get_keywords_meta(elem):
        """Returns list of words from HTML meta tag.
        Args:
            elem: 
        Returns:
            keywords: list of keywords webpage without duplicates.
        """
        web_keywords = elem.find('meta', attrs={'name': 'keywords'})
        if web_keywords:
            keywords_content = web_keywords.get("content")
            keywords = [ str(i).strip(punctuation).lower() for i in regex_split(";|,| ", keywords_content)] #split by , OR space
            return keywords

    @staticmethod
    def get_keyword_list(text, keywords=None):
        """Calculate Frequency of keywords from meta tag in visible HTML tags.

        Args:
            text: (str) text from HTML tag.
            keywords: (list) list of unique lower keywords from website. Default is None.

        Returns:
            word_list: (list) list of words which are in keywords arguments.
                if keyword is None return parsed list words from text argument.

        """
        if text:
            word_list = [str(i).strip(punctuation).lower() for i in text.split()]
            if keywords:
                key_list = list(filter(lambda x: x in keywords, word_list))
                return key_list
            return word_list

    @staticmethod
    def check_url(url):
        """Checks is url valid - is a valid string, and if webpage exists"""

        prepared_request = PreparedRequest()
        try:
            prepared_request.prepare_url(url, None)
            validate = URLValidator(schemes=('https', 'http'))
            validate(url)
        except ValidationError or requests.exceptions.MissingSchema:
            raise FrequencyKeywordException("Nie można podać wyniku: nieprawidłowy adres url.")

        try:
            requests.get(url, stream=True)
        except BaseException:
            raise FrequencyKeywordException("Strona o podanymadresie url nie istnieje.")

    def __str__(self):
        """Returns string of object frequency attribute."""

        if self.frequency:
            return '\n'.join([ str(k) + " : " + str(v) for k,v in  self.frequency.items()])
        else:
            return "{}"
