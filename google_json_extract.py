"""
This class extracts json data saved from google screener to panda data frame.
DF is having columns of SYMBOL and CompanyName
"""

import pandas, re, json
import common_code

class google_sceerner_json_DataExtract(object):
    def __init__(self):
        #self.json_file = 'EPS5yearGreaterThanZeroNSE.txt'
        self.json_file = common_code.google_json_file
        self.result_df = pandas.DataFrame()

    def get_json_from_file(self):
        with open(self.json_file) as f:
            data_str = f.read()
        # replace all / then save back
        update_str = re.sub(r"\\", '',data_str)
        json_rawData = json.loads(update_str)
        return json_rawData

    def convert_json_to_df(self):
        json_rawData = self.get_json_from_file()
        new_data_list = []
        for n in json_rawData['searchresults']:
            temp_stock_dict={'SYMBOL':n['ticker'],
            'CompanyName':n['title'],
            }
            new_data_list.append(temp_stock_dict)
        return pandas.DataFrame(new_data_list)

    def retrieve_stock_data(self):
        temp_df = self.convert_json_to_df()
        #print temp_df
        self.result_df = temp_df

