# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import quandl
import json
import time
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
    #print (df)
    return df
    
    df_localData.set_index('PERIOD', inplace=True)
    

def run_screener():
    df_quandlCode = pd.DataFrame.from_csv(r'deb_tickers.csv')
    latest_qtr = '2016-03-31'
    #print (df_quandlCode.head(2))
    #df_quandlCode = df_quandlCode.head(20)
    EPSQtrChange = 1.00
    
    metStocks_4qtrs = []
    metStocks_3qtrs = []
    metStocks_2qtrs = []
    failedStocks = []
    outdatedStocks = []
    lessthan4qtrsStocks = []
    
    textFile = open("FirstReport.txt", "w")

    stockIndex = 0
    totalStocks = len(df_quandlCode)
    print (totalStocks)
    for index, row in df_quandlCode.iterrows():
        print ('processing ', row['Quandl_Code'], 'stock index = ', stockIndex, ' out of ', totalStocks)
        stockIndex += 1
        df_row = get_data(row['Quandl_Code'], latest_qtr, False)
        if df_row.empty:
            failedStocks.append(row['Quandl_Code'])
        #print ('index= ', df_row.tail(1).index)
        if (df_row.tail(1).index == latest_qtr):
            print(row['Quandl_Code'], ' have latest data')
        else:
            print ('old qtr data, not considering...')
            outdatedStocks.append(row['Quandl_Code'])
            continue
        
        rowLen = len(df_row.index)
        if rowLen < 4:
            lessthan4qtrsStocks.append(row['Quandl_Code'])
            textFile.write("%s is less than 4 qtr\n" % (row['Quandl_Code']))
            continue
        
        # we are interested only on latest 4 qtrs
        df_row = df_row.tail(4)
        indexes = df_row.tail(4).index
        #print (df_row)
        """
        Q1Change = df_row.ix['2015-06-30', 'STANDALONE']
        Q2Change = df_row.ix['2015-09-30', 'STANDALONE']
        Q3Change = df_row.ix['2015-12-31', 'STANDALONE']
        Q4Change = df_row.ix['2016-03-31', 'STANDALONE']
        """
        """
        Q1 is recent quater
        """
        Q1Change = df_row.ix[indexes[3], 'STANDALONE']
        Q2Change = df_row.ix[indexes[2], 'STANDALONE']
        Q3Change = df_row.ix[indexes[1], 'STANDALONE']
        Q4Change = df_row.ix[indexes[0], 'STANDALONE']
        
        if Q1Change > EPSQtrChange and Q2Change > EPSQtrChange and \
            Q3Change > EPSQtrChange and Q4Change > EPSQtrChange:
            metStocks_4qtrs.append(row['Quandl_Code'])
            print(row['Quandl_Code'], ' meets 4 qtr requirement')
            textFile.write("%s meets your stringent 4 qtr EPSG requirement\n" % (row['Quandl_Code']))
            continue
                
        if  Q1Change > EPSQtrChange and Q2Change > EPSQtrChange and \
            Q3Change > EPSQtrChange:
            metStocks_3qtrs.append(row['Quandl_Code'])
            print(row['Quandl_Code'], ' meets 3 qtr requirement')
            textFile.write("%s meets your stringent 3 qtr EPSG requirement\n" % (row['Quandl_Code']))
            continue
            
        if Q1Change > EPSQtrChange and Q2Change > EPSQtrChange:           
            metStocks_2qtrs.append(row['Quandl_Code'])
            print(row['Quandl_Code'], ' meets 2 qtr requirement')
            textFile.write("%s meets your stringent 2 qtr EPSG requirement\n" % (row['Quandl_Code']))
            continue
        
    print("%d stocks meets 4 qtr criteria\n" % len(metStocks_4qtrs))
    print (metStocks_4qtrs)
    print("%d stocks meets 3 qtr criteria\n" % len(metStocks_3qtrs))
    print (metStocks_3qtrs)
    print("%d stocks meets 2 qtr criteria\n" % len(metStocks_2qtrs))
    print (metStocks_2qtrs)
    print ("%d stocks failed to get any data\n" % len(failedStocks))
    print (failedStocks)
    print ("%d stocks failed to find updated data\n" % len(outdatedStocks))
    print (outdatedStocks)    
    
    textFile.write("Following stocks have %s growth for last 4 quaters:\n" % (EPSQtrChange))
    json.dump(metStocks_4qtrs, textFile)
    textFile.write("\n")
    textFile.write("Following stocks have %s growth for last 3 quaters:\n" % (EPSQtrChange))    
    json.dump(metStocks_3qtrs, textFile)
    textFile.write("\n")
    textFile.write("Following stocks have %s growth for last 2 quaters:\n" % (EPSQtrChange))    
    json.dump(metStocks_2qtrs, textFile)
    textFile.write("\n") 
    textFile.write("\n")
    textFile.write("Following stocks failed to find data\n")
    json.dump(failedStocks, textFile)
    textFile.write("Following stocks has outdated data\n")
    json.dump(outdatedStocks, textFile)
    textFile.write("\n")
    textFile.close()
    
        #print (row['Quandl_Code'], len(df_row.index))
        #print (df_row)
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