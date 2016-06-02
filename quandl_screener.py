# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import quandl
#print (dir(quandl))
#from Quandl import *#
quandl.ApiConfig.api_key = '7vZgPpWzjifpxspHesDz'
quandl.ApiConfig.api_version = '2015-04-09'

def get_local_data(filename):
    df = pd.DataFrame()
    try:
        df = pd.DataFrame.from_csv(filename)
        return df
    except :
        print (filename, 'not found')
        return df

def put_local_data(filename, df):
    df.to_csv(filename)
    
def get_Quandl_data(quandlCode, force_local):    
    df = pd.DataFrame()
    
    if force_local == True:
        return df
    string = 'DEB/'+quandlCode+'_Q_EPS4Q'
    print ('feching data from Quandl for  ', quandlCode)
    try:
        df = quandl.get(string)
    except:
        print('failed to get data from Quandl', quandlCode)
        
    return df;

"""
Function gets data from local disc. If not present or outdate, get from Quandl website.
return and empty DF on failure.
"""
def get_data(quandlCode, latest_qtr, force_local):
    filename = 'csvs/'+quandlCode+'.csv'
    #latest_qtr = '2016-03-31'
    
    df = get_local_data(filename)
    if df.empty:
        print ('local data failed')
        print ('fetching from Quandl')
        df = get_Quandl_data(quandlCode, force_local)
    else:
        latest_row = df.tail(1)        
        if latest_qtr == latest_row.index:
            print (quandlCode, ' has latest data locally')
            return df
        else:
            #local data outdated, fetch from web if not force_local
            if force_local == True:
                #return outdate local data
                return df
            df = get_Quandl_data(quandlCode, force_local)
    
    if df.empty:
        print ('fetch failed')
        return df
    
    #save df to local disc
    put_local_data(filename, df)
    print (df)
    return df
    
    df_localData.set_index('PERIOD', inplace=True)
    

def run_screener():
    df_quandlCode = pd.DataFrame.from_csv(r'deb_tickers.csv')
    latest_qtr = '2016-03-31'
    #print (df_quandlCode.head(2))
    df_quandlCode = df_quandlCode.head(2)

    for index, row in df_quandlCode.iterrows():
        df_row = get_data(row['Quandl_Code'], latest_qtr, True)
        print ('index= ', df_row.tail(1).index)
        if (df_row.tail(1).index == latest_qtr):
            print(row['Quandl_Code'], ' have latest data')
        else:
            print ('old qtr data, not considering...')
            continue
        
        #print (row['Quandl_Code'], len(df_row.index))
        print (df_row)
        #print ('last row', df_row.tail(1))
        
    #data = quandl.get("DEB/HATSUN_Q_EPS4Q")
    #print (data.head(20))

#print(data.head(20))

run_screener()
"""
#df.set_index('PERIOD', inplace=True)
row = next(df.iterrows())[1]
print (row['PERIOD'], row['STANDALONE'])

if row['STANDALONE'] < 0:
    print ("yes its less than zero")

for index, row in df.iterrows():
    print (row['PERIOD'], row['STANDALONE'])
    if row['STANDALONE'] < 0:
        print ("yes its less than zero")

#print (df['STANDALONE'])
"""


"""
df = pd.DataFrame.from_csv(r'deb_tickers.csv')
print (df.head(2))

for index, row in df.iterrows():
    print (row['Quandl_Code'], index)
    if index == 'INE470A01017':
        break
        
"""