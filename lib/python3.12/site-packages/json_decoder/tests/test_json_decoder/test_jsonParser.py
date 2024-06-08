import unittest

from json_decoder import JsonParser


class JsonDataTest(unittest.TestCase):

    def test_list_jon_data(self):
        self.json_list_data_path = r'list_data.json'
        json_data = JsonParser.parserJson(self.json_list_data_path)
        print(json_data)

