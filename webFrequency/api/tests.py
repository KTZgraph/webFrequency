# from django.test import TestCase

# Create your tests here.
"""
Unitests for class FrequencyKeywords
"""
import unittest
from bs4 import BeautifulSoup

import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'webFrequency.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "webFrequency.settings")

from api.frequency import FrequencyKeywords, FrequencyKeywordException

class TestFrequencyKeywords(unittest.TestCase):
    """Tests for class TestFrequencyKeywords"""

    web_keywords = ["https://www.python.org/", "https://www.nazwa.pl/"]
    def test_get_keywords_frequency(self):
        """
        Tests for `get_keywords_frequency` with webpages that have keywords - should return non empty frequence value

        """
        for url in self.web_keywords:
            result = FrequencyKeywords.get_keywords_frequency(url)
            self.assertTrue(result[0])

    web_no_keywords = ["https://allegro.pl/", "https://www.onet.pl/", "https://www.wp.pl/"]
    def test_get_keywords_frequency_empty_keywords(self):
        """
        Tests for `get_keywords_frequency` with webpages that haven't keywords - should return None

        """
        for url in self.web_no_keywords:
            result = FrequencyKeywords.get_keywords_frequency(url)
            self.assertFalse(result[0])

    url_values = [
        [ "https://www.nazwa.pl/", 
            {
                "nazwa.pl" : 6,
                "poczta" : 1,
                "hosting" : 4,
                "ssl" : 7,
                "darmowe" : 1,
                "domen" : 1,
                "www" : 9,
                "certyfikaty" : 1  
            }
        ]
    ]
    def test_returned_value(self):
        for elem in self.url_values:
            response_dict =  FrequencyKeywords.get_keywords_frequency(elem[0])[0]
            self.assertEqual(elem[1], response_dict)
    
    def test_get_keyword_list(self):
        """
        Tests for function `get_keyword_list` - calculating Frequency of keywords from meta tag in visible HTML tags

        """
        string_values = [
            [ "Ala ma kota.", ["kot"], [] ],
            [ "Ala   {}   kot,  345, 34534, rere, 67. 20-20", ["kot", "ala", "rere", "45543"], ["ala", "kot", "rere"] ],
            ["1234,  34, 34;34;3 Hello-WoRld", ["hello-world", "1234", "34"], ["1234", "34", "hello-world" ]],
            ["python-proggraming", ["python"], [] ],
            ["empty 23 key word list", [], ["empty", "23", "key", "word" ,"list"] ],
            ["not empty 23 key word list", ["Empty", "23y", "kEy", "wOrd" ,"liSt"], []  ]
        ]
        for arg in string_values:
            result = FrequencyKeywords.get_keyword_list(arg[0], arg[1])
            self.assertEqual(result, arg[2])

    valid_html = [
        ["<h1>test tekst</h1>", [['test', 'tekst']] ],
        ["<a><h1>test tekst</h1></a>", [ None, ['test', 'tekst']] ],
        ["<dfg>fdfdg</dfg>", [["fdfdg"]] ]
    ]
    def test_get_keywords_meta(self):
        """
        Tests value for text from html tags
        """
        for html in self.valid_html:
            result = []
            soup = BeautifulSoup(html[0],'html.parser')
            for elem in soup.find_all(True, recursive=True): #wyciaganie danych pomiedzy tagami
                key_words_list = FrequencyKeywords.get_keyword_list(elem.find(text=True, recursive = False))
                result.append(key_words_list)
            self.assertEqual(result, html[1])
        
    valid_urls = [
        "https://allegro.pl/",
        "https://www.onet.pl/",
        "https://www.wp.pl/",
        "https://www.python.org/"
    ]
    def test_check_url_valid_data(self):
        """
        Tests for function `check_url` with valid data

        """
        for url in self.valid_urls:
            FrequencyKeywords.check_url(url)
            self.assertRaises(FrequencyKeywordException, FrequencyKeywords.check_url(url))

    invalid_urls= [
        "https://www.wp./",
        "https://www..pl/",
        "https://.wp.pl/"
    ]
    def test_check_url_broken_url(self):
        """
        Tests for function `check_url` with invalid data

        """
        for url in self.invalid_urls:
            try:
                raised = False
                FrequencyKeywords.check_url(url)
            except FrequencyKeywordException:
                raised = True
            self.assertTrue(raised, True)
