import re
import urllib2
from urllib2 import urlopen
import sqlite3
import common_code

class getData_bussinesStd(object):
    def __init__(self, stockLinkId, stockSymbol, reportType):
	self.stockSymbol = stockSymbol
        self.linkId = stockLinkId
        self.reportType = reportType
        self.sqlite_file = common_code.sqliteFile
        self.latestQtrName = common_code.current_qtr
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
        common_code.mySleep(1)

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
        """ First will try to get data from data base if not fetch from website """
        try:
            conn =sqlite3.connect(self.sqlite_file)
            c = conn.cursor()
            sql_cmd = "SELECT * FROM STOCKDATA WHERE symbol=?"
            c.execute(sql_cmd, [(self.stockSymbol)])
            row = c.fetchone()

            # fetch from web if data is none or outdated
            if row != None and self.latestQtrName == row[common_code.DBindex_Q1Name]:
                print "Latest Data found in DB for stock ", self.stockSymbol
                self.result_dict['EPS_Q1'] = row[common_code.DBindex_EPS_Q1]
                self.result_dict['EPS_Q2'] = row[common_code.DBindex_EPS_Q2]
                self.result_dict['EPS_Q3'] = row[common_code.DBindex_EPS_Q3]
                self.result_dict['EPS_Q4'] = row[common_code.DBindex_EPS_Q4]
                self.result_dict['EPS_Q1YoY'] = row[common_code.DBindex_EPS_Q1YoY]
                self.result_dict['EPS_Q2YoY'] = row[common_code.DBindex_EPS_Q2YoY]
                self.result_dict['EPS_Q3YoY'] = row[common_code.DBindex_EPS_Q3YoY]
                self.result_dict['EPS_Q4YoY'] = row[common_code.DBindex_EPS_Q4YoY]
                self.result_dict['Q1Name'] = row[common_code.DBindex_Q1Name]
                self.result_dict['Q2Name'] = row[common_code.DBindex_Q2Name]
                self.result_dict['Q3Name'] = row[common_code.DBindex_Q3Name]
                self.result_dict['Q4Name'] = row[common_code.DBindex_Q4Name]
                self.result_dict['EPSQ1Change'] = row[common_code.DBindex_EPSQ1Change]
                self.result_dict['EPSQ2Change'] = row[common_code.DBindex_EPSQ2Change]
                self.result_dict['EPSQ3Change'] = row[common_code.DBindex_EPSQ3Change]
                self.result_dict['EPSQ4Change'] = row[common_code.DBindex_EPSQ4Change]
                self.result_dict['Y1Name'] = row[common_code.DBindex_Y1Name]
                self.result_dict['Y2Name'] = row[common_code.DBindex_Y2Name]
                self.result_dict['Y3Name'] = row[common_code.DBindex_Y3Name]
                self.result_dict['Y4Name'] = row[common_code.DBindex_Y4Name]
                self.result_dict['EPS_Y1'] = row[common_code.DBindex_EPS_Y1]
                self.result_dict['EPS_Y2'] = row[common_code.DBindex_EPS_Y2]
                self.result_dict['EPS_Y3'] = row[common_code.DBindex_EPS_Y3]
                self.result_dict['EPS_Y4'] = row[common_code.DBindex_EPS_Y4]
                self.result_dict['EPSY1Change'] = row[common_code.DBindex_EPSY1Change]
                self.result_dict['EPSY2Change'] = row[common_code.DBindex_EPSY2Change]
                self.result_dict['EPSY3Change'] = row[common_code.DBindex_EPSY3Change]
                conn.close()
                return True
                
                if common_code.is_stock_blacklisted(self.stockSymbol) == True:
                    return False

            print "Get data from web old data in DB ==============", self.stockSymbol, row[common_code.DBindex_Q1Name]
            common_code.dataBase_outdate_stocks += 1

        except Exception,e:
            print ""
            #print 'failed in getEPSdata trying to read DB',str(e)
            #return False

        try:
            try:
                self.EPS_Quaterly_1_Source = urllib2.urlopen(self.EPS_Quaterly_1).read()
                self.EPS_Quaterly_2_Source = urllib2.urlopen(self.EPS_Quaterly_2).read()
            except Exception,e:
                #Try once again
                print 'open failed. try again after 2 seconds', str(e)
                common_code.mySleep(2)
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
                common_code.mySleep(2)
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
                    common_code.mySleep(2)
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
                    common_code.mySleep(2)
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
                    common_code.mySleep(2)
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

            c.execute("CREATE TABLE IF NOT EXISTS STOCKDATA \
                (symbol, EPS_Q1, EPS_Q2, EPS_Q3, EPS_Q4, \
                EPS_Q1YoY, EPS_Q2YoY, EPS_Q3YoY, EPS_Q4YoY,\
                Q1Name, Q2Name, Q3Name, Q4Name,\
                EPSQ1Change, EPSQ2Change, EPSQ3Change, EPSQ4Change,\
                Y1Name, Y2Name, Y3Name, Y4Name,\
                EPS_Y1, EPS_Y2, EPS_Y3, EPS_Y4,\
                EPSY1Change, EPSY2Change, EPSY3Change)")

            #print "Updating symbol... ", self.stockSymbol
            c.execute('''DELETE FROM STOCKDATA WHERE symbol = ?''', (self.stockSymbol,))

            c.execute('''INSERT INTO STOCKDATA(symbol, EPS_Q1, EPS_Q2, EPS_Q3, EPS_Q4, \
              EPS_Q1YoY, EPS_Q2YoY, EPS_Q3YoY, EPS_Q4YoY,\
              Q1Name, Q2Name, Q3Name, Q4Name,\
              EPSQ1Change, EPSQ2Change, EPSQ3Change, EPSQ4Change,\
              Y1Name, Y2Name, Y3Name, Y4Name,\
              EPS_Y1, EPS_Y2, EPS_Y3, EPS_Y4,\
              EPSY1Change, EPSY2Change, EPSY3Change)\
              values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
              (self.stockSymbol, self.result_dict['EPS_Q1'],  self.result_dict['EPS_Q2'],  self.result_dict['EPS_Q3'],  self.result_dict['EPS_Q4'],
              self.result_dict['EPS_Q1YoY'],self.result_dict['EPS_Q2YoY'], self.result_dict['EPS_Q3YoY'], self.result_dict['EPS_Q4YoY'],
              self.result_dict['Q1Name'], self.result_dict['Q2Name'], self.result_dict['Q3Name'], self.result_dict['Q4Name'],
              self.result_dict['EPSQ1Change'], self.result_dict['EPSQ2Change'], self.result_dict['EPSQ3Change'], self.result_dict['EPSQ4Change'],
              self.result_dict['Y1Name'], self.result_dict['Y2Name'], self.result_dict['Y3Name'], self.result_dict['Y4Name'],
              self.result_dict['EPS_Y1'], self.result_dict['EPS_Y2'], self.result_dict['EPS_Y3'], self.result_dict['EPS_Y4'],
              self.result_dict['EPSY1Change'], self.result_dict['EPSY2Change'], self.result_dict['EPSY3Change']))

            if self.latestQtrName == self.result_dict['Q1Name']:
                common_code.dataBase_updated_stocks += 1

            conn.commit()
            conn.close()

            print ("dataBase: out of outdated stocks = %d, updated = %d" % (common_code.dataBase_outdate_stocks, common_code.dataBase_updated_stocks))
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

