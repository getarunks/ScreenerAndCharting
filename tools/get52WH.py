import json

class json_DataExtract(object):
    def __init__(self):
        self.json_file = 'online52NewHigh.json.txt'

    def get_json_from_file(self):
        with open(self.json_file) as f:
            data_str = f.read()
        json_rawData = json.loads(data_str)
        return json_rawData

    def convert_json_to_df(self):
        json_rawData = self.get_json_from_file()
        data_list = []
        for n in json_rawData['data']:
            data_list.append(n['symbol'])        
        #remove u from printing
        arr = [str(r) for r in data_list]
        print arr        
        return data_list

extractJson = json_DataExtract()
extractJson.convert_json_to_df()

