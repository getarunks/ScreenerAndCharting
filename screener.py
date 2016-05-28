import os, re, sys, time, datetime, copy, calendar
import pandas
import json
import time
import urllib2
from urllib2 import urlopen
import sqlite3

def mySleep(t):
    #time.sleep(t)
    print(" ")    
"""
This class extracts json data saved from google screener to panda data frame.
DF is having columns of SYMBOL and CompanyName
"""
class google_sceerner_json_DataExtract(object):
    def __init__(self):
        #self.json_file = 'EPS5yearGreaterThanZeroNSE.txt'
        self.json_file = 'NIFTYAllStocks.txt'
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
            
class getData_bussinesStd(object):
    def __init__(self, stockLinkId, reportType):
        self.linkId = stockLinkId
        self.reportType = reportType
        self.cashFlow_link = 'http://www.business-standard.com/company/'+stockLinkId+'/cash-flow/1/'+reportType
        self.result_dict = {}
        self.ratio_link = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-ratios/1/'+reportType
        self.EPS_Quaterly_1 = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-quaterly/1/'+reportType
        self.EPS_Quaterly_2 = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-quaterly/2/'+reportType
        self.finacialOverview_link = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-overview/'+reportType
        self.finacialOverview_link1 = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-overview/2/'+reportType
        self.finacialPL_link = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-profit-loss/'+reportType
        self.finacialPL_link1 = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-profit-loss/2/'+reportType
        # promotor holding link has only compId, no compFormat
        compId = re.findall('\d+', stockLinkId)
        self.promotorLink = 'http://www.business-standard.com/stocks/share-holding-pattern/'+str(int(compId[0]))
        """
        Lets not bombard the free websites with requestes. Sleep 1 seconds after
        each query.
        """        
        mySleep(1)
        
    def getPromotorHoldings(self):
        try:            
            source = urlopen(self.promotorLink).read()
            PHQuater1 = source.split('(in %)</td>')[1].split('<td class="tdh">')[1].split('</td>')[0]
            PHQuater2 = source.split('(in %)</td>')[1].split('<td class="tdh">')[2].split('</td>')[0]
            PHQuater3 = source.split('(in %)</td>')[1].split('<td class="tdh">')[3].split('</td>')[0]
            PHQuater4 = source.split('(in %)</td>')[1].split('<td class="tdh">')[4].split('</td>')[0]
            PHQuater5 = source.split('(in %)</td>')[1].split('<td class="tdh">')[5].split('</td>')[0]
            
            string = 'Total of Promoters'
            totalPromoterQ1 = source.split(string)[1].split('<td class="">')[1].split('</td>')[0]
            totalPromoterQ2 = source.split(string)[1].split('<td class="">')[2].split('</td>')[0]
            totalPromoterQ3 = source.split(string)[1].split('<td class="">')[3].split('</td>')[0]
            totalPromoterQ4 = source.split(string)[1].split('<td class="">')[4].split('</td>')[0]
            totalPromoterQ5 = source.split(string)[1].split('<td class="">')[5].split('</td>')[0]           
            
            string = '<strong>Institutions</strong>'
            totalInstitQ1 = source.split(string)[1].split('<td class="">')[1].split('</td>')[0]
            totalInstitQ2 = source.split(string)[1].split('<td class="">')[2].split('</td>')[0]
            totalInstitQ3 = source.split(string)[1].split('<td class="">')[3].split('</td>')[0]
            totalInstitQ4 = source.split(string)[1].split('<td class="">')[4].split('</td>')[0]
            totalInstitQ5 = source.split(string)[1].split('<td class="">')[5].split('</td>')[0]
            
            string = 'Foreign Institutional Investors</td>'
            FIIQ1 = source.split(string)[1].split('<td class="">')[1].split('</td>')[0]
            FIIQ2 = source.split(string)[1].split('<td class="">')[2].split('</td>')[0]
            FIIQ3 = source.split(string)[1].split('<td class="">')[3].split('</td>')[0]
            FIIQ4 = source.split(string)[1].split('<td class="">')[4].split('</td>')[0]
            FIIQ5 = source.split(string)[1].split('<td class="">')[5].split('</td>')[0]
            
            
            string = 'Financial Institutions / Banks</td>'
            FinInstitQ1 = source.split(string)[1].split('<td class="">')[1].split('</td>')[0]
            FinInstitQ2 = source.split(string)[1].split('<td class="">')[2].split('</td>')[0]
            FinInstitQ3 = source.split(string)[1].split('<td class="">')[3].split('</td>')[0]
            FinInstitQ4 = source.split(string)[1].split('<td class="">')[4].split('</td>')[0]
            FinInstitQ5 = source.split(string)[1].split('<td class="">')[5].split('</td>')[0]
            
            string = 'Mutual  Funds / UTI</td'
            MFQ1 = source.split(string)[1].split('<td class="">')[1].split('</td>')[0]
            MFQ2 = source.split(string)[1].split('<td class="">')[2].split('</td>')[0]
            MFQ3 = source.split(string)[1].split('<td class="">')[3].split('</td>')[0]
            MFQ4 = source.split(string)[1].split('<td class="">')[4].split('</td>')[0]
            MFQ5 = source.split(string)[1].split('<td class="">')[5].split('</td>')[0]
            
            self.result_dict['PHQuater1'] = PHQuater1
            self.result_dict['PHQuater2'] = PHQuater2
            self.result_dict['PHQuater3'] = PHQuater3
            self.result_dict['PHQuater4'] = PHQuater4
            self.result_dict['PHQuater5'] = PHQuater5
            
            self.result_dict['totalPromoterQ1'] = totalPromoterQ1
            self.result_dict['totalPromoterQ2'] = totalPromoterQ2
            self.result_dict['totalPromoterQ3'] = totalPromoterQ3
            self.result_dict['totalPromoterQ4'] = totalPromoterQ4
            self.result_dict['totalPromoterQ5'] = totalPromoterQ5
            
            self.result_dict['totalInstitQ1'] = totalInstitQ1
            self.result_dict['totalInstitQ2'] = totalInstitQ2
            self.result_dict['totalInstitQ3'] = totalInstitQ3
            self.result_dict['totalInstitQ4'] = totalInstitQ4
            self.result_dict['totalInstitQ5'] = totalInstitQ5
            
            self.result_dict['FIIQ1'] = FIIQ1
            self.result_dict['FIIQ2'] = FIIQ2
            self.result_dict['FIIQ3'] = FIIQ3
            self.result_dict['FIIQ4'] = FIIQ4
            self.result_dict['FIIQ5'] = FIIQ5

            self.result_dict['FinInstitQ1'] = FinInstitQ1
            self.result_dict['FinInstitQ2'] = FinInstitQ2
            self.result_dict['FinInstitQ3'] = FinInstitQ3
            self.result_dict['FinInstitQ4'] = FinInstitQ4
            self.result_dict['FinInstitQ5'] = FinInstitQ5            
            
            self.result_dict['MFQ1'] = MFQ1
            self.result_dict['MFQ2'] = MFQ2
            self.result_dict['MFQ3'] = MFQ3
            self.result_dict['MFQ4'] = MFQ4
            self.result_dict['MFQ5'] = MFQ5

            print("in percent                %s\t%s\t%s\t%s\t%s" % (PHQuater1, PHQuater2, PHQuater3, PHQuater4, PHQuater5))
            print("Tot PH                  : %s\t\t%s\t\t%s\t\t%s\t\t%s" % (totalPromoterQ1, totalPromoterQ2, totalPromoterQ3, totalPromoterQ4, totalPromoterQ5))
            print("Tot Institutions        : %s\t\t%s\t\t%s\t\t%s\t\t%s" % (totalInstitQ1, totalInstitQ2, totalInstitQ3, totalInstitQ4, totalInstitQ5))
            print("Financial Institutions  : %s\t\t%s\t\t%s\t\t%s\t\t%s\n" % (FinInstitQ1, FinInstitQ2, FinInstitQ3, FinInstitQ4, FinInstitQ5))
            print("FII                     : %s\t\t%s\t\t%s\t\t%s\t\t%s" % (FIIQ1, FIIQ2, FIIQ3, FIIQ4, FIIQ5))
            print("Mutal Funds             : %s\t\t%s\t\t%s\t\t%s\t\t%s" % (MFQ1, MFQ2, MFQ3, MFQ4, MFQ5))
            
            return True
            
        except Exception,e:
            print 'faild in getPromotorHoldings loop',str(e)
            return False               
                
    def getCashFlowData(self):
        try:
            cashFlow_source = urllib2.urlopen(self.cashFlow_link).read()
            string = 'Net Cash From Operating Activities</td>'
            CFyear1 = cashFlow_source.split(string)[1].split('<td class="">')[1].split('</td>')[0]
            CFyear2 = cashFlow_source.split(string)[1].split('<td class="">')[2].split('</td>')[0]
            CFyear3 = cashFlow_source.split(string)[1].split('<td class="">')[3].split('</td>')[0]
            
            string = 'Figures in Rs crore</td>'
            firstYear = cashFlow_source.split(string)[1].split('<td class="tdh">')[1].split('</td>')[0]
            secondYear = cashFlow_source.split(string)[1].split('<td class="tdh">')[2].split('</td>')[0]
            thirdYear = cashFlow_source.split(string)[1].split('<td class="tdh">')[3].split('</td>')[0]
            
            print 'Cash Flow from Operations: ' + self.reportType         
            print("          %s\t%s\t%s" % (firstYear, secondYear, thirdYear))
            print("in Crs:   %s\t%s\t%s" % (CFyear1, CFyear2, CFyear3))
            
            self.result_dict['CFYearName1'] = firstYear
            self.result_dict['CFYearName2'] = secondYear
            self.result_dict['CFYearName3'] = thirdYear
            self.result_dict['CFYear1'] = float(CFyear1)
            self.result_dict['CFYear2'] = float(CFyear2)
            self.result_dict['CFYear3'] = float(CFyear3)
            
        except Exception,e:
            print 'faild in getCashFlowData loop',str(e)
            return False            
             
    def getEPSdata(self):
        try:
            try:
                self.EPS_Quaterly_1_Source = urllib2.urlopen(self.EPS_Quaterly_1).read()
                self.EPS_Quaterly_2_Source = urllib2.urlopen(self.EPS_Quaterly_2).read()
            except Exception,e:
                #Try once again
                print 'open failed. try again after 2 seconds', str(e)
                mySleep(2)
                self.EPS_Quaterly_1_Source = urllib2.urlopen(self.EPS_Quaterly_1).read()
                self.EPS_Quaterly_2_Source = urllib2.urlopen(self.EPS_Quaterly_2).read()

            sourceCode = self.EPS_Quaterly_1_Source
            Q1 = float(sourceCode.split('EPS (Rs)</td>')[1].split('<td class="">')[1].split('</td>')[0])
            Q2 = float(sourceCode.split('EPS (Rs)</td>')[1].split('<td class="">')[2].split('</td>')[0])
            Q3 = float(sourceCode.split('EPS (Rs)</td>')[1].split('<td class="">')[3].split('</td>')[0])
            Q4 = float(sourceCode.split('EPS (Rs)</td>')[1].split('<td class="">')[4].split('</td>')[0])
            Q1YoY = float(sourceCode.split('EPS (Rs)</td>')[1].split('<td class="">')[5].split('</td>')[0])

            sourceCode = self.EPS_Quaterly_2_Source
            Q2YoY = float(sourceCode.split('EPS (Rs)</td>')[1].split('<td class="">')[1].split('</td>')[0])
            Q3YoY = float(sourceCode.split('EPS (Rs)</td>')[1].split('<td class="">')[2].split('</td>')[0])
            Q4YoY = float(sourceCode.split('EPS (Rs)</td>')[1].split('<td class="">')[3].split('</td>')[0])

            sourceCode = self.EPS_Quaterly_1_Source
            string = 'Figures in Rs crore</td>'
            self.result_dict['Q1Name'] = sourceCode.split(string)[1].split('<td class="tdh">')[1].split('</td>')[0]
            self.result_dict['Q2Name'] = sourceCode.split(string)[1].split('<td class="tdh">')[2].split('</td>')[0]
            self.result_dict['Q3Name'] = sourceCode.split(string)[1].split('<td class="tdh">')[3].split('</td>')[0]
            self.result_dict['Q4Name'] = sourceCode.split(string)[1].split('<td class="tdh">')[4].split('</td>')[0]

            #print Q1Name + Q1Name + Q3Name + Q4Name

            self.result_dict['EPS_Q1'] = Q1
            self.result_dict['EPS_Q2'] = Q2
            self.result_dict['EPS_Q3'] = Q3
            self.result_dict['EPS_Q4'] = Q4
            self.result_dict['EPS_Q1YoY'] = Q1YoY
            self.result_dict['EPS_Q2YoY'] = Q2YoY
            self.result_dict['EPS_Q3YoY'] = Q3YoY
            self.result_dict['EPS_Q4YoY'] = Q4YoY
            
            """
            Check and return if any of the EPS is zero to avoid divide by zero
           
            list = [Q1YoY, Q2YoY, Q3YoY, Q4YoY]
            if (any(x == 0 for x in list)):
                return False
            """
            
            """ We make all 0 to 0.1
            """
            Q1YoY = 0.1 if Q1YoY == 0 else Q1YoY
            Q2YoY = 0.1 if Q2YoY == 0 else Q2YoY
            Q3YoY = 0.1 if Q3YoY == 0 else Q3YoY
            Q4YoY = 0.1 if Q4YoY == 0 else Q4YoY
            
            self.result_dict['EPSQ1Change'] = (Q1 - Q1YoY)/Q1YoY*100             
            self.result_dict['EPSQ2Change'] = (Q2 - Q2YoY)/Q2YoY*100
            self.result_dict['EPSQ3Change'] = (Q3 - Q3YoY)/Q3YoY*100
            self.result_dict['EPSQ4Change'] = (Q4 - Q4YoY)/Q4YoY*100

            try:
                source = urlopen(self.finacialOverview_link).read()
            except Exception,e:
                #Try once again
                print 'open failed. try again after 2 seconds', str(e)
                mySleep(2)
                source = urlopen(self.finacialOverview_link).read() 
            try:
                Y1 = float(source.split('Earning Per Share (Rs)</td>')[1].split('<td class="">')[1].split('</td>')[0])
                Y2 = float(source.split('Earning Per Share (Rs)</td>')[1].split('<td class="">')[2].split('</td>')[0])
                Y3 = float(source.split('Earning Per Share (Rs)</td>')[1].split('<td class="">')[3].split('</td>')[0])
                
                string = 'Particulars '
                self.result_dict['Y1Name'] = source.split(string)[1].split('<td class="tdh">')[1].split('</td>')[0]
                self.result_dict['Y2Name'] = source.split(string)[1].split('<td class="tdh">')[2].split('</td>')[0]
                self.result_dict['Y3Name'] = source.split(string)[1].split('<td class="tdh">')[3].split('</td>')[0]
                
                try:
                    source = urlopen(self.finacialOverview_link1).read()
                except Exception,e:
                #Try once again
                    print 'open failed. try again after 2 seconds', str(e)
                    mySleep(2)
                    source = urlopen(self.finacialOverview_link1).read()
                    
                Y4 = float(source.split('Earning Per Share (Rs)</td>')[1].split('<td class="">')[1].split('</td>')[0])
                self.result_dict['Y4Name'] = source.split(string)[1].split('<td class="tdh">')[1].split('</td>')[0]                
            except Exception,e:
                print 'failed when spliting finacialoverview link trying finacialPL link',str(e)
                try:
                    source = urlopen(self.finacialPL_link).read()
                except Exception,e:
                #Try once again
                    print 'open failed. try again after 2 seconds', str(e)
                    mySleep(2)
                    source = urlopen(self.finacialPL_link).read()
                string = '<td class="tdL" colspan="0">Earning Per Share (Rs.)</td>'
                Y1 = float(source.split(string)[1].split('<td class="amount">')[1].split('</td>')[0])
                Y2 = float(source.split(string)[1].split('<td class="amount">')[2].split('</td>')[0])
                Y3 = float(source.split(string)[1].split('<td class="amount">')[3].split('</td>')[0])

                string = 'Figures in Rs crore</td>'
                self.result_dict['Y1Name'] = source.split(string)[1].split('<td class="tdh">')[1].split('</td>')[0]
                self.result_dict['Y2Name'] = source.split(string)[1].split('<td class="tdh">')[2].split('</td>')[0]
                self.result_dict['Y3Name'] = source.split(string)[1].split('<td class="tdh">')[3].split('</td>')[0]
                
                try:
                    source = urlopen(self.finacialPL_link1).read()               
                except Exception,e:
                #Try once again
                    print 'open failed. try again after 2 seconds', str(e)
                    mySleep(2)
                    source = urlopen(self.finacialPL_link1).read() 
                string = '<td class="tdL" colspan="0">Earning Per Share (Rs.)</td>'
                Y4 = float(source.split(string)[1].split('<td class="amount">')[1].split('</td>')[0])
                string = 'Figures in Rs crore</td>'
                self.result_dict['Y4Name'] = source.split(string)[1].split('<td class="tdh">')[1].split('</td>')[0]
                print 'second link succesfull'
            
            self.result_dict['EPS_Y1'] = Y1
            self.result_dict['EPS_Y2'] = Y2
            self.result_dict['EPS_Y3'] = Y3
            self.result_dict['EPS_Y4'] = Y4          
            
            """ We make all 0 denomenators to 0.1 to avoid divide by zero
            """
            Y2 = 0.1 if Y2 == 0 else Y2
            Y3 = 0.1 if Y3 == 0 else Y3
            Y4 = 0.1 if Y4 == 0 else Y4
            
            self.result_dict['EPSY1Change'] = (Y1 - Y2)/Y2*100             
            self.result_dict['EPSY2Change'] = (Y2 - Y3)/Y3*100
            self.result_dict['EPSY3Change'] = (Y3 - Y4)/Y4*100
            
            return True;
            
        except Exception,e:
            print 'failed in getEPSdata Report_bussinesStd loop',str(e)
            return False
            
    def getRatios(self):
        try:
            self.ratioSource = urlopen(self.ratio_link).read()
            string = 'Return on Net Worth (%)</td>'
            returnOnNetWorth_year1 = self.ratioSource.split(string)[1].split('<td class="">')[1].split('</td>')[0]
            returnOnNetWorth_year2 = self.ratioSource.split(string)[1].split('<td class="">')[2].split('</td>')[0]
            returnOnNetWorth_year3 = self.ratioSource.split(string)[1].split('<td class="">')[3].split('</td>')[0]
            
            string = '<td class="tdh tdC">Ratios</td>'
            year1 = self.ratioSource.split(string)[1].split('<td class="tdh">')[1].split('</td>')[0]
            year2 = self.ratioSource.split(string)[1].split('<td class="tdh">')[2].split('</td>')[0]
            year3 = self.ratioSource.split(string)[1].split('<td class="tdh">')[3].split('</td>')[0]
            
            string = 'Debt-Equity Ratio</td>'
            debtToEquity_year1 = self.ratioSource.split(string)[1].split('<td class="">')[1].split('</td>')[0]
            debtToEquity_year2 = self.ratioSource.split(string)[1].split('<td class="">')[2].split('</td>')[0]
            debtToEquity_year3 = self.ratioSource.split(string)[1].split('<td class="">')[3].split('</td>')[0]
            
            string = 'Interest Coverage ratio</td>'
            interestCoverage_year1 = self.ratioSource.split(string)[1].split('<td class="">')[1].split('</td>')[0]
            interestCoverage_year2 = self.ratioSource.split(string)[1].split('<td class="">')[2].split('</td>')[0]
            interestCoverage_year3 = self.ratioSource.split(string)[1].split('<td class="">')[3].split('</td>')[0]
            
            print("Ratios                \t%s\t%s\t%s" % (year1, year2, year3))        
            print("Return On Net Worth : \t%s\t%s\t%s" % (returnOnNetWorth_year1, returnOnNetWorth_year2, returnOnNetWorth_year3))
            print("Interest Coverage   : \t%s\t%s\t%s" % (interestCoverage_year1, interestCoverage_year2, interestCoverage_year3 ))
            print("Debt-Equity         : \t%s\t%s\t%s" % (debtToEquity_year1, debtToEquity_year2, debtToEquity_year3))
            
            self.result_dict['RatioYearName1'] = year1
            self.result_dict['RatioYearName2'] = year2
            self.result_dict['RatioYearName3'] = year3
            self.result_dict['RONWyear1'] = float(returnOnNetWorth_year1)
            self.result_dict['RONWyear2'] = float(returnOnNetWorth_year2)
            self.result_dict['RONWyear3'] = float(returnOnNetWorth_year3)
            self.result_dict['ICyear1'] = float(interestCoverage_year1)
            self.result_dict['ICyear2'] = float(interestCoverage_year2)
            self.result_dict['ICyear3'] = float(interestCoverage_year3)   
            self.result_dict['DEyear1'] = float(debtToEquity_year1)
            self.result_dict['DEyear2'] = float(debtToEquity_year2)
            self.result_dict['DEyear3'] = float(debtToEquity_year3) 
            return True
            
        except Exception,e:
            print 'faild in getRatio bussinesSTD loop',str(e)
            return False

def getReportType(consolidated):
    if consolidated == 0:
        reportType = 'Standalone'
    else:
        reportType = 'Consolidated'
    return reportType
            
           
##### All command line function below

 #Add stock list here to run Beat command
stockListBeat = [u'3MINDIA']

def createDB():
    sqlite_file = 'stock_db.sqlite'
    
    conn =sqlite3.connect(sqlite_file)
    c = conn.cursor()
    
    table_name = 'SYMBOLS'
    c.execute('CREATE TABLE {tn} ({nf} {ft} PRIMARY KEY)'\
            .format(tn=table_name,nf='SYMBOL', ft = 'TEXT'))
            
    for stock in stockListBeat:
        cf = compFormat_bussinesStd(stock)
        cf.get_compFormat()
        if cf.result == 'NODATA':
            print 'No Data for: ' + stock
            del cf
            return

        reportType = getReportType(0)
        BSdata = getData_bussinesStd(cf.result, reportType)
        if BSdata.getEPSdata() == False:
            print 'get_averageEPS returned False'
            return

        """ Add EPS for last four quaters
        """
        EPS = BSdata.result_dict['EPS_Q1'] +  BSdata.result_dict['EPS_Q1'] + \
                BSdata.result_dict['EPS_Q3'] +  BSdata.result_dict['EPS_Q4']

    #http://stackoverflow.com/questions/7026911/sqlite-no-return-type-in-python    
    conn.commit()
    conn.close()


class EPSData:
    def __init__(self):
        self.yearName = []
        self.annualEPS = []
        self.yearChange = []
        self.qtrName= []
        self.qtrEPS = []
        self.qtrYoYEPS = []        
        self.qtrChange = []

"""
Filter only if following 4 conditions are met
1. current quater EPS growth > previous quater EPS growth
2. Annual EPS > 5
3. Current Annual EPS Growth >= 0
4. Average EPS growth of latest two quaters > 40%
"""   
def check_criteria(epsData_array, averageEPSgrowth, EPS, index):
    if (epsData_array[index].qtrChange[0] < epsData_array[index].qtrChange[1]) or (EPS < 5) or \
        (averageEPSgrowth < 40) or (epsData_array[index].yearChange[0] < 0):
        print 'skipping ',epsData_array[index].qtrChange[0], ' < ', epsData_array[index].qtrChange[1]
        return 0

    return 1

#def runBeatTheMarket():
def Beat(showFIIonly):

    stock_dict_EPSAnnual = {}
    stock_dict_EPSG = {}
    stock_dict_EPSData = {}
    
    length = len(stockListBeat)
    print 'Total no of stock: ', length
    mySleep(1)
    epsData_array = [EPSData() for i in range(length+1)]
    
    count = index = 0
    for stock in stockListBeat:
        print ("Analysing %s index = %d filtered so far = %d" % (stock, count, index))
        cf = compFormat_bussinesStd(stock)
        cf.get_compFormat()
        if cf.result == 'NODATA':
            print 'No Data for: ' + stock
            del cf
            return
            
        reportType = getReportType(0)
        BSdata = getData_bussinesStd(cf.result, reportType)
        if BSdata.getEPSdata() == False:
            print 'get_averageEPS returned False'
            return
            
        """
        Save EPS data to use later for printing. An attempt to reduce querring from website.
        """
        epsData_array[index].yearName.append(BSdata.result_dict['Y1Name'])
        epsData_array[index].yearName.append(BSdata.result_dict['Y2Name'])
        epsData_array[index].yearName.append(BSdata.result_dict['Y3Name'])
        epsData_array[index].yearName.append(BSdata.result_dict['Y4Name'])
                
        epsData_array[index].annualEPS.append(round(BSdata.result_dict['EPS_Y1'], 2))
        epsData_array[index].annualEPS.append(round(BSdata.result_dict['EPS_Y2'], 2))
        epsData_array[index].annualEPS.append(round(BSdata.result_dict['EPS_Y3'], 2))
        epsData_array[index].annualEPS.append(round(BSdata.result_dict['EPS_Y4'], 2))
        
        epsData_array[index].yearChange.append(round(BSdata.result_dict['EPSY1Change'], 2))
        epsData_array[index].yearChange.append(round(BSdata.result_dict['EPSY2Change'], 2))
        epsData_array[index].yearChange.append(round(BSdata.result_dict['EPSY3Change'], 2))
        
        epsData_array[index].qtrName.append(BSdata.result_dict['Q1Name'])
        epsData_array[index].qtrName.append(BSdata.result_dict['Q2Name'])
        epsData_array[index].qtrName.append(BSdata.result_dict['Q3Name'])
        epsData_array[index].qtrName.append(BSdata.result_dict['Q4Name'])
        
        epsData_array[index].qtrEPS.append(round(BSdata.result_dict['EPS_Q1'], 2))
        epsData_array[index].qtrEPS.append(round(BSdata.result_dict['EPS_Q2'], 2))
        epsData_array[index].qtrEPS.append(round(BSdata.result_dict['EPS_Q3'], 2))
        epsData_array[index].qtrEPS.append(round(BSdata.result_dict['EPS_Q4'], 2))
        
        epsData_array[index].qtrYoYEPS.append(round(BSdata.result_dict['EPS_Q1YoY'], 2))
        epsData_array[index].qtrYoYEPS.append(round(BSdata.result_dict['EPS_Q2YoY'], 2))
        epsData_array[index].qtrYoYEPS.append(round(BSdata.result_dict['EPS_Q3YoY'], 2))
        epsData_array[index].qtrYoYEPS.append(round(BSdata.result_dict['EPS_Q4YoY'], 2))

        epsData_array[index].qtrChange.append(round(BSdata.result_dict['EPSQ1Change'], 2))
        epsData_array[index].qtrChange.append(round(BSdata.result_dict['EPSQ2Change'], 2))
        epsData_array[index].qtrChange.append(round(BSdata.result_dict['EPSQ3Change'], 2))
        epsData_array[index].qtrChange.append(round(BSdata.result_dict['EPSQ4Change'], 2))      
        
        """ Add EPS for last four quaters
        """
        EPS = BSdata.result_dict['EPS_Q1'] +  BSdata.result_dict['EPS_Q1'] + \
                BSdata.result_dict['EPS_Q3'] +  BSdata.result_dict['EPS_Q4']
        """
        averageEPSgrowth = (BSdata.result_dict['EPSQ1Change'] + BSdata.result_dict['EPSQ2Change'] + \
                            BSdata.result_dict['EPSQ3Change'] + BSdata.result_dict['EPSQ4Change'])/4
        """
        averageEPSgrowth = (BSdata.result_dict['EPSQ1Change'] + BSdata.result_dict['EPSQ2Change'])/2

        print 'EPS: ' + str(EPS)
        print BSdata.result_dict['EPSQ1Change'], BSdata.result_dict['EPSQ2Change']
        print 'Av EPS ' + str(averageEPSgrowth)
        """
        Filter only if following 4 conditions are met
        1. current quater EPS growth > previous quater EPS growth
        2. Annual EPS > 5
        3. Current Annual EPS Growth >= 0
        4. Average EPS growth of latest two quaters > 40%
        
        ret = check_criteria(epsData_array, averageEPSgrowth, EPS, index)
        if ret == 0:
            epsData_array[index].yearName = []
            epsData_array[index].annualEPS = []
            epsData_array[index].yearChange = []
            epsData_array[index].qtrName = []
            epsData_array[index].qtrEPS = []
            epsData_array[index].qtrYoYEPS = []
            epsData_array[index].qtrChange = []
            count +=1
            del cf, BSdata
            continue
        """
        
        """skip if TTM EPS data is negative"""
        if EPS < 0:
            count +=1
            del cf, BSdata
            continue;
        
        stock_dict_EPSAnnual[stock] = round(EPS,2)
        stock_dict_EPSG[stock] = averageEPSgrowth
        stock_dict_EPSData[stock] = epsData_array[index]
        """
        sort_list = [(k,v) for v,k in sorted(
                    [(v,k) for k,v in stock_dict.items()], reverse=True)]
        """    
        sort_list = [(k,v) for v,k in sorted(
                    [(v,k) for k,v in stock_dict_EPSG.items()], reverse=True)]

        index += 1
        count += 1
        del cf, BSdata
                        
    print sort_list[0:30]

    textFile = open("BeatReport.txt", "w")
    index = 0
    for n in sort_list:        
        stock = n[0]
        epsData = stock_dict_EPSData[stock]
        #print ("================Testing index %d %s" % (index, epsData_array[index].qtrChange[0]))
        print ("================Testing index %d %s %s" % (index, epsData.qtrChange[0], epsData.qtrChange[1]))
        #print("Testing: %s\n" % (epsData[index].qtrChange[0]))
        
        ratioError = cashFlowError =PHError = 0
        cf = compFormat_bussinesStd(n[0])
        cf.get_compFormat()
        if cf.result == 'NODATA':
            print 'No Data for: ' + stock
            cf.result = compFormatFailed(stock)
            if cf.result == False:
                del cf
                return False

        reportType = getReportType(0)
        BSdata = getData_bussinesStd(cf.result, reportType)        
        
        if BSdata.getPromotorHoldings() == False:
            print("%s: getPromotorHoldings returned False" % (stock))
            PHError = 1               

        # we are not interested if FII is not involved
        if PHError != 1 and showFIIonly == 1:
            if (float(BSdata.result_dict['FIIQ1']) == 0) and (float(BSdata.result_dict['FIIQ2']) == 0):
                index += 1                
                continue
        
        if BSdata.getRatios() == False:
            print("%s: getRatios returned False" % (stock))
            textFile.write("Raito fetch error. please look manually\n")
            ratioError = 1
            
        if BSdata.getCashFlowData() == False:
            print("%s: getCashFlowData returned False" % (stock))
            cashFlowError = 1 
            
        textFile.write("=======================================\n")
        textFile.write("Symbol: %s \tEPS: %s \tAv. EPS growth(last 2 Qtrs): %d%s\n" % \
                        (stock, stock_dict_EPSAnnual[stock], stock_dict_EPSG[stock], '%'))
        textFile.write("Annual EPS Data: %s\n" % (reportType))
        textFile.write("                          %15s%15s%15s%15s\n" % (epsData.yearName[0],
                                                                   epsData.yearName[1],
                                                                   epsData.yearName[2],
                                                                   epsData.yearName[3]))
        textFile.write("EPS Data                : %15s%15s%15s%15s\n" % (epsData.annualEPS[0], 
                                                                   epsData.annualEPS[1], 
                                                                   epsData.annualEPS[2], 
                                                                   epsData.annualEPS[3]))
        textFile.write("Change in percentage    : %15d%15d%15d\n" % (epsData.yearChange[0], 
                                                               epsData.yearChange[1], 
                                                               epsData.yearChange[2]))
        textFile.write("Quarterly EPS Data: %s\n" % (reportType))
        textFile.write("                          %15s%15s%15s%15s\n" % (epsData.qtrName[0],
                                                                   epsData.qtrName[1],
                                                                   epsData.qtrName[2],
                                                                   epsData.qtrName[3]))
        textFile.write("Current Year            : %15s%15s%15s%15s\n" % (epsData.qtrEPS[0],
                                                                   epsData.qtrEPS[1],
                                                                   epsData.qtrEPS[2],
                                                                   epsData.qtrEPS[3]))
        textFile.write("Previous Year           : %15s%15s%15s%15s\n" % (epsData.qtrYoYEPS[0],
                                                                   epsData.qtrYoYEPS[1],
                                                                   epsData.qtrYoYEPS[2],
                                                                   epsData.qtrYoYEPS[3]))
        textFile.write("Change in percentage    : %15d%15d%15d%15d\n" %(epsData.qtrChange[0],
                                                                   epsData.qtrChange[1],
                                                                   epsData.qtrChange[2],
                                                                   epsData.qtrChange[3])) 
        textFile.write("--------\n")
        
        if ratioError == 1:
            print 'getRatios returned False'
            textFile.write("Raito fetch error. please look manually\n")
        else:
            textFile.write("Ratios                    %15s%15s%15s\n" % (BSdata.result_dict['RatioYearName1'], BSdata.result_dict['RatioYearName2'], BSdata.result_dict['RatioYearName3']))        
            textFile.write("Return On Net Worth     : %15s%15s%15s\n" % (BSdata.result_dict['RONWyear1'], BSdata.result_dict['RONWyear2'], BSdata.result_dict['RONWyear3']))
            textFile.write("Interest Coverage       : %15s%15s%15s\n" % (BSdata.result_dict['ICyear1'], BSdata.result_dict['ICyear2'], BSdata.result_dict['ICyear3']))
            textFile.write("Debt-Equity             : %15s%15s%15s\n" % (BSdata.result_dict['DEyear1'], BSdata.result_dict['DEyear2'], BSdata.result_dict['DEyear3']))
            textFile.write("--------\n")
            
        if cashFlowError == 1:
            textFile.write("Cash flow fetch erro. please look manually")
        else:
            textFile.write("Cash from Ops(in Cr)    : %15s%15s%15s\n" % (BSdata.result_dict['CFYear1'], BSdata.result_dict['CFYear2'], BSdata.result_dict['CFYear3']))
        
        if PHError == 1:
            print 'getPromotorHoldings returned False'
            textFile.write("PromotorHoldings fetch error. please look manually\n")
        else:
            textFile.write("--------\n")
            textFile.write('Promoter Holdings Info:\n')
            textFile.write("in percent                %15s%15s%15s%15s%15s\n" % (BSdata.result_dict['PHQuater1'], BSdata.result_dict['PHQuater2'], BSdata.result_dict['PHQuater3'], BSdata.result_dict['PHQuater4'], BSdata.result_dict['PHQuater5']))
            textFile.write("Tot PH                  : %15s%15s%15s%15s%15s\n" % (BSdata.result_dict['totalPromoterQ1'], BSdata.result_dict['totalPromoterQ2'], BSdata.result_dict['totalPromoterQ3'], BSdata.result_dict['totalPromoterQ4'], BSdata.result_dict['totalPromoterQ5']))
            textFile.write("Tot Institutions        : %15s%15s%15s%15s%15s\n" % (BSdata.result_dict['totalInstitQ1'], BSdata.result_dict['totalInstitQ2'], BSdata.result_dict['totalInstitQ3'], BSdata.result_dict['totalInstitQ4'], BSdata.result_dict['totalInstitQ5']))
            textFile.write("FII                     : %15s%15s%15s%15s%15s\n" % (BSdata.result_dict['FIIQ1'], BSdata.result_dict['FIIQ2'], BSdata.result_dict['FIIQ3'], BSdata.result_dict['FIIQ4'], BSdata.result_dict['FIIQ5']))
            textFile.write("Financial Institutions  : %15s%15s%15s%15s%15s\n" % (BSdata.result_dict['FinInstitQ1'], BSdata.result_dict['FinInstitQ2'], BSdata.result_dict['FinInstitQ3'], BSdata.result_dict['FinInstitQ4'], BSdata.result_dict['FinInstitQ5']))
            textFile.write("Mutual Funds            : %15s%15s%15s%15s%15s\n" % (BSdata.result_dict['MFQ1'], BSdata.result_dict['MFQ2'], BSdata.result_dict['MFQ3'], BSdata.result_dict['MFQ4'], BSdata.result_dict['MFQ5']))
                                
        textFile.write("=======================================\n")
        index += 1
        
    textFile.close()               
        
    #print stock_dict
    
def compFormatFailed(stockSymbol):
    return input('Please enter Bussiness std stock ID for %s \' \': ' % (stockSymbol))
    return False
    
def getCashFlow(stockSymbol, consolidated):
    #print 'get_stock details for: ' +stockSymbol
    cf = compFormat_bussinesStd(stockSymbol)
    cf.get_compFormat()
    if cf.result == 'NODATA':
        print 'No Data for: ' + stockSymbol
        cf.result = compFormatFailed(stockSymbol)
        if cf.result == False:
            del cf
            return False
    
    reportType = getReportType(consolidated)
    report = getData_bussinesStd(cf.result, reportType)   
    if report.getCashFlowData() == False:
        print stockSymbol + ' error fetching data'
        del cf
        return
        
    del cf, report
    
def getPH(stockSymbol):
    #print 'get_stock details for: ' +stockSymbol
    cf = compFormat_bussinesStd(stockSymbol)
    cf.get_compFormat()
    if cf.result == 'NODATA':
        print 'No Data for: ' + stockSymbol
        cf.result = compFormatFailed(stockSymbol)
        if cf.result == False:
            del cf
            return False
        
    report = getData_bussinesStd(cf.result, 'doesntmatter')
    if report.getPromotorHoldings() == False:
        print stockSymbol + ' error fetching data'
        del cf
        return
        
    del cf, report


def getRatios(stockSymbol, consolidated):
    #print 'get_stock details for: ' +stockSymbol
    cf = compFormat_bussinesStd(stockSymbol)
    cf.get_compFormat()
    if cf.result == 'NODATA':
        print 'No Data for: ' + stockSymbol
        cf.result = compFormatFailed(stockSymbol)
        if cf.result == False:
            del cf
            return False
    
    reportType = getReportType(consolidated)        
    report = getData_bussinesStd(cf.result, reportType)   
    if report.getRatios() == False:
        print stockSymbol + ' error fetching data'
        del cf        
        
    #del cf, report    

def getEPSG(stockSymbol, consolidated):    
    reportType = getReportType(consolidated)        
    cf = compFormat_bussinesStd(stockSymbol)
    cf.get_compFormat()
    if cf.result == 'NODATA':
        print 'No Data for: ' + stockSymbol
        cf.result = compFormatFailed(stockSymbol)
        if cf.result == False:
            del cf
            return False
    
    reportType = getReportType(consolidated)        
    report = getData_bussinesStd(cf.result, reportType)   
    if report.getEPSdata() == False:
        print stockSymbol + ' error fetching data'
        del cf
        return False
        
    print 'Annual EPS Data: '+reportType
    print("                      %15s%15s%15s%15s" % (report.result_dict['Y1Name'],
                                               report.result_dict['Y2Name'],
                                                report.result_dict['Y3Name'],
                                                report.result_dict['Y4Name'] ))
    print("EPS Data       :      %15s%15s%15s%15s" % (report.result_dict['EPS_Y1'], 
                                                    report.result_dict['EPS_Y2'], 
                                                    report.result_dict['EPS_Y3'], 
                                                    report.result_dict['EPS_Y4']))
    print("Change percent :      %15d%15d%15d" %(report.result_dict['EPSY1Change'], 
                                                    report.result_dict['EPSY2Change'],
                                                    report.result_dict['EPSY3Change']))    
    print 'Quaterly EPS Data: ' + reportType         
    print("                      %15s%15s%15s%15s" % (report.result_dict['Q1Name'],
                                               report.result_dict['Q2Name'],
                                                report.result_dict['Q3Name'], 
                                                report.result_dict['Q4Name']))
    print("Current Year   :      %15s%15s%15s%15s" % (report.result_dict['EPS_Q1'], 
                                                    report.result_dict['EPS_Q2'], 
                                                    report.result_dict['EPS_Q3'], 
                                                    report.result_dict['EPS_Q4']))
    print("Previous Year  :      %15s%15s%15s%15s" % (report.result_dict['EPS_Q1YoY'], 
                                                     report.result_dict['EPS_Q2YoY'], 
                                                     report.result_dict['EPS_Q3YoY'],
                                                     report.result_dict['EPS_Q4YoY']))
    print("Change percent :      %15d%15d%15d%15d" %(report.result_dict['EPSQ1Change'],
                                                     report.result_dict['EPSQ2Change'], 
                                                     report.result_dict['EPSQ3Change'], 
                                                     report.result_dict['EPSQ4Change']))
    onGoingAnnualEPS = float(report.result_dict['EPS_Q1']) + float(report.result_dict['EPS_Q2']) + float(report.result_dict['EPS_Q3']) +  float(report.result_dict['EPS_Q4'])
    print("On going Annual EPS: %0.2f" % (onGoingAnnualEPS))
    return report
    
def getAll(stockSymbol, consolidated):
    print("=============================")
    getEPSG(stockSymbol, consolidated)
    print("=============================")
    getRatios(stockSymbol, consolidated)
    print("=============================")
    getCashFlow(stockSymbol, consolidated)
    print("=============================")
    print("Promoter Holding Pattern:")
    getPH(stockSymbol)
    print("=============================")
    
    
def getCompleteReport(EPSY1, EPSY2, EPSY3, EPSCurrQtr, EPSQtrAlone):
    googleSceernerData = google_sceerner_json_DataExtract()
    googleSceernerData.retrieve_stock_data()
    googleSceernerData.result_df.to_csv(r'google-data.csv', index=False)
    
    textFile = open("FirstReport.txt", "w")
    
    metStocks_CANSLIM = []    
    metStocks_4qtrs = []
    metStocks_3qtrs = []
    failedStocks = []
    
    index = 0
    condMetOnce = 0
    for stockSymbol in googleSceernerData.result_df['SYMBOL']:
        print("Processing stock %s, index = %d out of %d\n" %  (stockSymbol, index, (len(googleSceernerData.result_df['SYMBOL']))))
        report = getEPSG(stockSymbol, 0)
        if report == False:
            failedStocks.append(stockSymbol)
            index +=1
            continue
        elif report.result_dict['EPSQ1Change'] >= float(EPSQtrAlone) and\
            report.result_dict['EPSQ2Change'] >= float(EPSQtrAlone) and\
            report.result_dict['EPSQ3Change'] >= float(EPSQtrAlone) and\
            report.result_dict['EPSQ4Change'] >= float(EPSQtrAlone):
            textFile.write("%s meets your stringent EPSG requirement\n" % (stockSymbol))
            textFile.flush()
            metStocks_4qtrs.append(stockSymbol)
            print "meets requirement"
            condMetOnce = 1
        elif report.result_dict['EPSQ1Change'] >= float(EPSQtrAlone) and\
            report.result_dict['EPSQ2Change'] >= float(EPSQtrAlone) and\
            report.result_dict['EPSQ3Change'] >= float(EPSQtrAlone):
            metStocks_3qtrs.append(stockSymbol)
            condMetOnce = 1
            
        if report.result_dict['EPSY1Change'] >= float(EPSY1) and\
            report.result_dict['EPSY2Change'] >= float(EPSY2) and\
            report.result_dict['EPSY3Change'] >= float(EPSY3) and\
            report.result_dict['EPSQ1Change'] >= float(EPSCurrQtr):
            #skip if already in one list
            if condMetOnce == 0:
                textFile.write("%s meets CANSLIM funtamentals\n" % (stockSymbol))
                textFile.flush()
                metStocks_CANSLIM.append(stockSymbol)
        index += 1
        condMetOnce = 0
    
    print("%d stocks meets 4 qtr criteria\n" % len(metStocks_4qtrs))
    print metStocks_4qtrs
    print("%d stocks meets 3 qtr criteria\n" % len(metStocks_3qtrs))
    print metStocks_3qtrs
    print("%d stocks meets CANSLIM criteria\n" % len(metStocks_CANSLIM))
    print metStocks_CANSLIM
    print ("%d stocks failed to find in Bussiness std\n" % len(failedStocks))
    print failedStocks
    
    textFile.write("Following stocks have %s growth for last 4 quaters:\n" % (EPSQtrAlone))
    json.dump(metStocks_4qtrs, textFile)
    textFile.write("Following stocks have %s growth for last 3 quaters:\n" % (EPSQtrAlone))    
    json.dump(metStocks_3qtrs, textFile)
    textFile.write("Following stocks have met CANSLIM Y1: %s, Y2: %s, Y3: %s Cur Qtr %s:\n" % (EPSY1, EPSY2, EPSY3, EPSCurrQtr))   
    json.dump(metStocks_CANSLIM, textFile)    
    textFile.write("Following stocks failed to find in Buss Std\n")
    json.dump(failedStocks, textFile)
    textFile.close()
    
    del googleSceernerData

from Tkinter import Tk, Label, Button, Entry
class readInputParams:
    def __init__(self, master):
        self.master = master
        master.title("Enter Filter Criteria:")
        
        self.label_CANSLIMParams = Label(master, text="CANSLIM EPS Parameters:")
        self.label_latestYear = Label(master, text="Latest Year")
        self.label_prevYear = Label(master, text="Previous Year")
        self.label_prevprevYear = Label(master, text="2nd Prev Year")
        self.label_currentQtr = Label(master, text="current Qtr")        
        self.label_QtrEPSAlone = Label(master, text="Quater EPS Growth alone")        
        self.filter_button = Button(master, text="Filter", command=lambda: self.runFilter())
        self.entry_EPSY1 = Entry(master)
        self.entry_EPSY2 = Entry(master)
        self.entry_EPSY3 = Entry(master)
        self.entry_EPSCurrQtr = Entry(master)
        self.entry_EPSQtrAlone = Entry(master)
        
        #layout
        #first row
        self.label_latestYear.grid(row=1, column=2)
        self.label_prevYear.grid(row=1, column=3)
        self.label_prevprevYear.grid(row=1, column=4)
        self.label_currentQtr.grid(row=1, column=5)
        
        #second row
        self.label_CANSLIMParams.grid(row=2, column=1)
        self.entry_EPSY1.grid(row=2, column=2)
        self.entry_EPSY2.grid(row=2, column=3)
        self.entry_EPSY3.grid(row=2, column=4)
        self.entry_EPSCurrQtr.grid(row=2, column=5)
        
        #third row
        self.label_QtrEPSAlone.grid(row=3, column=1)
        self.entry_EPSQtrAlone.grid(row=3, column=2)
        
        #fourth row
        self.filter_button.grid(row=4, column=1) 
        
        #set default values
        self.entry_EPSY1.insert(0, 10)
        self.entry_EPSY2.insert(0, 8)
        self.entry_EPSY3.insert(0, 0)
        self.entry_EPSCurrQtr.insert(0, 15)
        self.entry_EPSQtrAlone.insert(0, 10)
        
    def runFilter(self):
        EPSY1 = self.entry_EPSY1.get()
        EPSY2 = self.entry_EPSY2.get()
        EPSY3 = self.entry_EPSY3.get()
        EPSCurrQtr = self.entry_EPSCurrQtr.get()
        EPSQtrAlone = self.entry_EPSQtrAlone.get()
        print("in filter Y1 %s Y2 %s Y3 %s Curren %s QtrAlone %s" %(EPSY1, EPSY2, EPSY3, EPSCurrQtr, EPSQtrAlone))
        getCompleteReport(EPSY1, EPSY2, EPSY3, EPSCurrQtr, EPSQtrAlone)
        print("CompleteReport Done..\n")
        
if __name__ == '__main__':
    skip_main = 0
    
    if skip_main != 1:
        print 'main'        
        root = Tk()
        my_gui = readInputParams(root)
        root.mainloop()  