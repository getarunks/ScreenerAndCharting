"""
This class extracts json data saved from Bussiness Std to panda data frame.
DF is having columns of SYMBOL, CompanyName, CompId, compFormat, linkId
"""

import pandas, re, json

compFormat_onlyOnce = 0
BS_DataFrame = pandas.DataFrame()
class compFormat_bussinesStd(object):
    def __init__(self, stock):
        self.stock = stock;
        self.saved_json_BS = 'data_BS.json'
        self.target_tag = 'searchresults' #use to identify the json data needed
        self.result = pandas.DataFrame()

    def get_json_object_from_file(self):
        """ Return the json object from the .json file download.
        Returns: (json obj): modified json object fr file.
        """
        with open(self.saved_json_BS) as f:
            data_str = f.read()

        #replace all the / then save back the file
        update_str = re.sub(r"\\",'',data_str)
        #print update_str
        update_str = re.sub(r"<div class=",':',update_str)
        #print update_str
        update_str = re.sub(r"stock_symb",',"stock_symb',update_str)
        #print update_str
        update_str = re.sub(r"stock_name",',"stock_name',update_str)
        #print update_str
        update_str = re.sub(r"</div>:",'',update_str)
        #print update_str
        update_str = re.sub(r"\"clrBoth\"></div>\"",'"',update_str)
        #print update_str
        update_str = re.sub(r">",':"',update_str)
        #print update_str
        json_raw_data = json.loads(update_str)
        return json_raw_data

    def convert_json_to_df(self):
        """ Convert JSON data to data frame
            return Dataframe obj
        """
        json_raw_data = self.get_json_object_from_file()

        new_data_list = []
        for n in json_raw_data['searchresults']:
            stockFormat = n['compFormatted']+'-'+n['compId']
            temp_stock_dict={'SYMBOL':n['stock_symb'],
                             'CompanyName':n['stock_name'],
                             'compId' :n['compId'],
                             'compFormat' :n['compFormatted'],
                             'linkId' :stockFormat,
                             }
            new_data_list.append(temp_stock_dict)

        return pandas.DataFrame(new_data_list)

    def get_compFormat(self):
        global BS_DataFrame, compFormat_onlyOnce
        if compFormat_onlyOnce < 1 :
            #print self.stock
            temp_data_frame = self.convert_json_to_df()
            # save all the info to csv file for debugging
            temp_data_frame.to_csv(r'bussiness-std.csv', index =False)
            BS_DataFrame = temp_data_frame
            compFormat_onlyOnce = 1

        temp_data_frame = BS_DataFrame
        # Let's find matching index first
        i = 0
        for n in temp_data_frame['SYMBOL']:
            if n == self.stock:
                break
            else:
                i = i + 1

        lastIndex =  temp_data_frame.index[-1]

        if i < lastIndex:
            row = temp_data_frame.loc[i]
            #print row
            self.result = row['linkId']
        else:
            self.result = 'NODATA'

