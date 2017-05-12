import re
from urllib2 import urlopen
import sqlite3
import common_code
import time

def myUrlopen(link):
    try:
        source = urlopen(link).read()
        common_code.webPageAcessed +=1
        if common_code.webPageAcessed % 10 == 0:
            print 'web page access count = ', common_code.webPageAcessed
    except Exception,e:
        #Sometime server might ot respond, try once again
        print 'open failed. try again after 5 seconds', str(e)
        time.sleep(5)
        source = urlopen(link).read()
        common_code.ebPageAcessed +=1
    return source

class getData_bussinesStd(object):
    def __init__(self, stockLinkId, stockSymbol):
        self.stockSymbol = stockSymbol
        self.linkId = stockLinkId
        self.sqlite_file = common_code.sqliteFile
        self.latestQtrName = common_code.current_qtr
        self.cashFlow_link = 'http://www.business-standard.com/company/'+stockLinkId+'/cash-flow/1/'
        self.result_dict = {}
        self.ratio_link = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-ratios/1/'
        
        self.EPS_Quaterly_1 = {}
        self.EPS_Quaterly_1['Standalone'] = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-quaterly/1/'
        self.EPS_Quaterly_1['Consolidated'] = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-quaterly/1/Consolidated'
        
        self.EPS_Quaterly_2 = {}
        self.EPS_Quaterly_2['Standalone'] = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-quaterly/2/'
        self.EPS_Quaterly_2['Consolidated'] = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-quaterly/2/Consolidated'
        
        self.finacialOverview_link = {}
        self.finacialOverview_link['Standalone'] = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-overview/'
        self.finacialOverview_link['Consolidated'] = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-overview/1/Consolidated'
        
        self.finacialOverview_link1 = {}
        self.finacialOverview_link1['Standalone'] = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-overview/2/'
        self.finacialOverview_link1['Consolidated'] = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-overview/2/Consolidated'
        
        self.finacialPL_link = {}
        self.finacialPL_link['Standalone'] = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-profit-loss/'
        self.finacialPL_link['Consolidated'] = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-profit-loss/1/Consolidated'
        
        self.finacialPL_link1 = {}
        self.finacialPL_link1['Standalone'] = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-profit-loss/2/'
        self.finacialPL_link1['Consolidated'] = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-profit-loss/2/Consolidated'
        
        self.balance_sheet_link = {}
        self.balance_sheet_link['Standalone'] = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-balance-sheet/'
        self.balance_sheet_link['Consolidated'] = 'http://www.business-standard.com/company/'+stockLinkId+'/financials-balance-sheet/1/Consolidated'
        
        self.summary_link = 'http://www.business-standard.com/company/'+stockLinkId
        # promotor holding link has only compId, no compFormat
        compId = re.findall('\d+', stockLinkId)
        self.promotorLink = 'http://www.business-standard.com/stocks/share-holding-pattern/'+str(int(compId[0]))

        """
        Lets not bombard the free websites with requestes. Sleep 1 seconds after
        each query.
        """
        common_code.mySleep(1)
        
#    result = self.splitString(sourceCode, 'EPS (Rs)</td>', '<td class="">', '</td>', 2, 4)
    """
    Function always return expectednoItems, if there are less items than requested, function 
    fill them with zeros.
    """
    def splitString(self, source, string1, string2, string3, firstElement, expectedNoItems):
        success = 1
        #output = 'error output'
        noItemsPresent = len(source.split(string1)[1].split(string2))
        #substract one coloumn of item headers
        noItemsPresent -= 1
        noItems = min(noItemsPresent, expectedNoItems)
        output = []

        """
        Fill zeros to avoid errors during unpack
        """        
        for counter in range(0, expectedNoItems):
            output.append(0)
            
        try:
            for counter in range(firstElement, noItemsPresent + 1):
                #print 'output[] =', counter, counter-firstElement
                if (counter - firstElement) >= expectedNoItems :
                    break
                output[counter-firstElement] = (source.split(string1)[1].split(string2)[counter].split(string3)[0])
                        
        except Exception,e:
            print "exception in splitString when looking for", string1, str(e)
            success = 0
            output[0] = 'error output'
            
        return {'success':success, 'output':output, 'itemsReturned':noItems }

    def yearlyUpdate(self):
        
        """
        We need matching data. ie. if quaterly data is standalone, we dont need to try consolidated here
        """
        if self.qtr_reportType == 'Consolidated':
            """
            This try-except loop is to figure out the reportType(conslidate/standalone)
            """
            try:
                reportType = 'Consolidated'
                self.balanceSheet_source = myUrlopen(self.balance_sheet_link[reportType])                        
                """
                We can't use splitString. We have to get exception here to switch to standalone
                """
                currentLiabilites = self.balanceSheet_source.split('Current Liabilities</td>')[1].split('<td class="">')[1].split('</td>')[0]            
            except Exception:
                print "exception in consolidated"
                reportType = 'Standalone'
                self.balanceSheet_source = myUrlopen(self.balance_sheet_link[reportType])
                currentLiabilites = self.balanceSheet_source.split('Current Liabilities</td>')[1].split('<td class="">')[1].split('</td>')[0]
        else:
            print "we directly moving to standalone in yearly"
            reportType = 'Standalone'
            self.balanceSheet_source = myUrlopen(self.balance_sheet_link[reportType])
            currentLiabilites = self.balanceSheet_source.split('Current Liabilities</td>')[1].split('<td class="">')[1].split('</td>')[0]
            
        print "report type: ", reportType       
        """
        Some stocks Anuual EPS is listed in finacial overview link, for other
        it is listed in P&L link. To solve this we need the below try except,
        """
        try:
            self.finacialOverview_source = myUrlopen(self.finacialOverview_link[reportType])
            result = self.splitString(self.finacialOverview_source, 'Earning Per Share (Rs)</td>', '<td class="">', '</td>', 1, 3)
            Y1EPS, Y2EPS, Y3EPS = result['output']            
            
            result = self.splitString(self.finacialOverview_source, 'Particulars ', '<td class="tdh">', '</td>', 1, 3)
            Y1Name, Y2Name, Y3Name = result['output']
            
            self.finacialOverview_source1 = myUrlopen(self.finacialOverview_link1[reportType])
            result = self.splitString(self.finacialOverview_source1, 'Earning Per Share (Rs)</td>', '<td class="">', '</td>', 1, 1)
            Y4EPS = result['output'][0]      
            
            result = self.splitString(self.finacialOverview_source1, 'Particulars ',  '<td class="tdh">', '</td>', 1, 1)
            Y4Name = result['output'][0]
            finacialPL_src_buffered = 0
        except Exception,e:
            print 'failed when spliting finacialoverview link trying finacialPL link',str(e)
            self.finacialPL_source = myUrlopen(self.finacialPL_link[reportType])
            result = self.splitString(self.finacialPL_source, '<td class="tdL" colspan="0">Earning Per Share (Rs.)</td>',
                                     '<td class="amount">', '</td>', 1, 3)
            Y1EPS, Y2EPS, Y3EPS = result['output']
            
            result = self.splitString(self.finacialPL_source, 'Figures in Rs crore</td>', '<td class="tdh">' ,'</td>', 1, 3)
            Y1Name, Y2Name, Y3Name = result['output']
            
            self.finacialPL_source1 = myUrlopen(self.finacialPL_link1[reportType])
            result = self.splitString(self.finacialPL_source1, '<td class="tdL" colspan="0">Earning Per Share (Rs.)</td>', 
                                        '<td class="amount">', '</td>', 1, 1)
            Y4EPS = result['output'][0]
            result = self.splitString(self.finacialPL_source1, 'Figures in Rs crore</td>', '<td class="tdh">', '</td>', 1, 1 )
            Y4Name = result['output'][0]                
            print 'second link succesfull'
            finacialPL_src_buffered = 1

        result = self.splitString(self.balanceSheet_source, 'Total Assets</b></td>', '<td class="">', '</td>', 1, 1 )
        totalAssets = result['output'][0]
        
        result = self.splitString(self.balanceSheet_source, 'Total Debt</td>', '<td class="">', '</td>', 1, 1)
        totalDebt = result['output'][0]
        
        """
        As per the program flow, finacialPL_src is buffered for finacial stocks.
        These finacial stocks has operating profit represented in different way. Handling this seperatly
        """
        if finacialPL_src_buffered == 0:
            self.finacialPL_source = myUrlopen(self.finacialPL_link[reportType])
            result = self.splitString(self.finacialPL_source, 'Operating Profit</b></td>', '<td class="">', '</td>', 1, 1)
            operatingProfit = result['output'][0]
        else :
            result = self.splitString(self.finacialPL_source, '<td class="tdL" colspan="0">Total</td>', '<td class="amount">', '</td>', 1, 1)
            operatingProfit = result['output'][0]
            print "operatingProfit ", operatingProfit
        
        result = self.splitString(self.finacialPL_source, 'Figures in Rs crore</td>', '<td class="tdh">', '</td>', 1, 1)
        currentYear = result['output'][0]
        
        self.summary_source = myUrlopen(self.summary_link)
        result = self.splitString(self.summary_source, 'Market Cap </td>', '<td class="bL1 tdR">', '</td>', 1, 1)
        marketCap = result['output'][0]
        marketCap = marketCap.replace(",", "")
        

        RoC = float(operatingProfit)/(float(totalAssets) - float(currentLiabilites))
        RoC *=100 #convert to percentage
        
        enterpriseValue = float(marketCap) + float(totalDebt)
        earningsYield = float(operatingProfit)/enterpriseValue*100
            
        print Y1Name, Y2Name, Y3Name, Y4Name
        print Y1EPS, Y2EPS, Y3EPS, Y4EPS
        """ We make all 0 denomenators to 0.1 to avoid divide by zero
        """
        Y2EPS = 0.1 if float(Y2EPS) == 0.00 else Y2EPS
        Y3EPS = 0.1 if float(Y3EPS) == 0.00 else Y3EPS
        Y4EPS = 0.1 if float(Y4EPS) == 0.00 else Y4EPS

        EPSY1Change = ((float(Y1EPS) - float(Y2EPS))/float(Y2EPS))*100
        EPSY2Change = ((float(Y2EPS) - float(Y3EPS))/float(Y3EPS))*100            
        EPSY3Change = ((float(Y3EPS) - float(Y4EPS))/float(Y4EPS))*100
                
        conn = sqlite3.connect(self.sqlite_file)
        c = conn.cursor()
                        
        c.execute("CREATE TABLE IF NOT EXISTS YEARLYSTOCKDATA \
            (symbol, Y1EPS, Y2EPS, Y3EPS, Y4EPS, \
            Y1Name, Y2Name, Y3Name, Y4Name,\
            EPSY1Change, EPSY2Change, EPSY3Change,\
            EBIT, TotAssest, CurLiability, MarketCap,\
            TotDebt, CurrYear, EarningsYield, RoC, \
            reportType)")
        c.execute('''DELETE FROM YEARLYSTOCKDATA WHERE symbol = ?''', (self.stockSymbol,))
        c.execute('''INSERT INTO YEARLYSTOCKDATA(symbol, Y1EPS, Y2EPS, Y3EPS, Y4EPS, \
            Y1Name, Y2Name, Y3Name, Y4Name,\
            EPSY1Change, EPSY2Change, EPSY3Change,\
            EBIT, TotAssest, CurLiability, MarketCap,\
            TotDebt, CurrYear, EarningsYield, RoC, \
            reportType)\
          values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
          (self.stockSymbol, Y1EPS, Y2EPS, Y3EPS, Y4EPS, Y1Name, Y2Name, Y3Name, Y4Name,
           EPSY1Change, EPSY2Change, EPSY3Change,
           operatingProfit, totalAssets, currentLiabilites, marketCap,
           totalDebt, currentYear, float("{0:.2f}".format(earningsYield)), float("{0:.2f}".format(RoC)),
           reportType))
        conn.commit()
        conn.close()
                
    def quaterlyUpdate(self):
        try:
            """ Lets start with consolidated and fallback to standalone if not available"""
            reportType = 'Consolidated'
            self.Quaterly_1_Source = myUrlopen(self.EPS_Quaterly_1[reportType])
            """ Try to decipher the report, if there is exception we have to try standalone"""
            result = self.splitString(self.Quaterly_1_Source, 'Figures in Rs crore</td>', '<td class="tdh">', '</td>', 1, 4)
            Q1Name, Q2Name, Q3Name, Q4Name = result['output']
            """ Sometimes consolidated data is present but not updated, in such scenarios
                we have to use standalone data
            """
            if Q1Name !=common_code.current_qtr and Q1Name != common_code.previous_qtr:
                print self.stockSymbol, " -- consolidated data is not updated. trying standalone by raising an exception"
                raise
        except Exception:
            reportType = 'Standalone'
            self.Quaterly_1_Source = myUrlopen(self.EPS_Quaterly_1[reportType])
            result = self.splitString(self.Quaterly_1_Source, 'Figures in Rs crore</td>', '<td class="tdh">', '</td>', 1, 4)
            Q1Name, Q2Name, Q3Name, Q4Name = result['output']
            
        print "Report Type: ", reportType
        self.qtr_reportType = reportType
        
        """ Do not proceed if latest qtr data is not any of (current or previous qtr) """
        if Q1Name != common_code.current_qtr and Q1Name != common_code.previous_qtr:
            print "Quite old data in server ", Q1Name
            return False

        result = self.splitString(self.Quaterly_1_Source, 'EPS (Rs)</td>', '<td class="">', '</td>', 1, 5)
        Q1, Q2, Q3, Q4, Q1YoY = result['output']
        
        self.Quaterly_2_Source = myUrlopen(self.EPS_Quaterly_2[reportType])
        result = self.splitString(self.Quaterly_2_Source, 'EPS (Rs)</td>', '<td class="">', '</td>', 1, 3)            
        Q2YoY, Q3YoY, Q4YoY = result['output']                        
 
        result = self.splitString(self.Quaterly_1_Source, 'Operating Profit</td>', '<td class="">', '</td>', 1, 4)
        EBIT_Q1, EBIT_Q2, EBIT_Q3, EBIT_Q4 = result['output']
        
        """ We make all denomiaor 0 to 0.1 to avoid divison by zero
        """
        Q1YoY = float(Q1YoY)
        Q2YoY = float(Q2YoY)
        Q3YoY = float(Q3YoY)
        Q4YoY = float(Q4YoY)

        Q1YoY = 0.1 if Q1YoY == 0.00 else Q1YoY
        Q2YoY = 0.1 if Q2YoY == 0.00 else Q2YoY
        Q3YoY = 0.1 if Q3YoY == 0.00 else Q3YoY
        Q4YoY = 0.1 if Q4YoY == 0.00 else Q4YoY
    
        EPSQ1Change = (float(Q1) - Q1YoY)/Q1YoY*100
        EPSQ2Change = (float(Q2) - Q2YoY)/Q2YoY*100
        EPSQ3Change = (float(Q3) - Q3YoY)/Q3YoY*100
        EPSQ4Change = (float(Q4) - Q4YoY)/Q4YoY*100

        conn = sqlite3.connect(self.sqlite_file)
        c = conn.cursor()
                        
        c.execute("CREATE TABLE IF NOT EXISTS QUATERLYSTOCKDATA \
            (symbol, EPS_Q1, EPS_Q2, EPS_Q3, EPS_Q4, \
            EPS_Q1YoY, EPS_Q2YoY, EPS_Q3YoY, EPS_Q4YoY,\
            Q1Name, Q2Name, Q3Name, Q4Name,\
            EPSQ1Change, EPSQ2Change, EPSQ3Change, EPSQ4Change,\
            EBIT_Q1, EBIT_Q2, EBIT_Q3, EBIT_Q4,\
            reportType)")
        c.execute('''DELETE FROM QUATERLYSTOCKDATA WHERE symbol = ?''', (self.stockSymbol,))
        c.execute('''INSERT INTO QUATERLYSTOCKDATA(symbol, EPS_Q1, EPS_Q2, EPS_Q3, EPS_Q4, \
          EPS_Q1YoY, EPS_Q2YoY, EPS_Q3YoY, EPS_Q4YoY,\
          Q1Name, Q2Name, Q3Name, Q4Name,\
          EPSQ1Change, EPSQ2Change, EPSQ3Change, EPSQ4Change,\
          EBIT_Q1, EBIT_Q2, EBIT_Q3, EBIT_Q4,\
          reportType)\
          values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
          (self.stockSymbol, float(Q1), float(Q2), float(Q3), float(Q4), float(Q1YoY), float(Q2YoY), float(Q3YoY), float(Q4YoY),
          Q1Name, Q2Name, Q3Name, Q4Name, EPSQ1Change, EPSQ2Change, EPSQ3Change, EPSQ4Change,
          float(EBIT_Q1), float(EBIT_Q2), float(EBIT_Q3), float(EBIT_Q4),
          reportType))
        print "Qtr data updated for", self.stockSymbol, Q1Name
        conn.commit()
        conn.close()
        return True        

    def updateCompleteDataBase(self):
        update_quaterly = 1
        update_yearly = 1
        try:
            conn = sqlite3.connect(self.sqlite_file)
            c = conn.cursor()
            sql_cmd = "SELECT * FROM QUATERLYSTOCKDATA WHERE symbol=?"
            c.execute(sql_cmd, [(self.stockSymbol)])
            qtr_row = c.fetchone()
            c.execute("SELECT * FROM QUATERLYSTOCKDATA WHERE symbol=?", [(self.stockSymbol)])
            yearly_row = c.fetchone()
            conn.close()
            """ if data is uptodate return """
            if qtr_row!=None and yearly_row!=None and \
                common_code.current_year == yearly_row[common_code.YearlyIndex_Y1Name] and\
                common_code.current_qtr == qtr_row[common_code.QuaterlyIndex_Q1Name]:
                return
            if common_code.current_qtr == qtr_row[common_code.QuaterlyIndex_Q1Name]:
                update_quaterly = 0
                self.qtr_reportType = qtr_row[common_code.QuaterlyIndex_reportType]
            if common_code.current_year == yearly_row[common_code.YearlyIndex_Y1Name]:
                update_yearly = 0
        except Exception,e:
            print "Exception updateCompleteDataBase. May be you want to fix this.", str(e)
            
        """ proceed with update """
        if update_quaterly == 1:
            print "call quaterlyUpdate ...."
            if self.quaterlyUpdate() == False:
                return False
        if update_yearly == 1:
            print "call yearly Update...."
            self.yearlyUpdate()
           
    def getPromotorHoldings(self):
        try:
            source = myUrlopen(self.promotorLink)
            result = self.splitString(source, '(in %)</td>', '<td class="tdh">', '</td>', 1, 5)
            self.result_dict['PHQuater1'], self.result_dict['PHQuater2'], self.result_dict['PHQuater3'],\
            self.result_dict['PHQuater4'], self.result_dict['PHQuater5'] = result['output']

            result = self.splitString(source, 'Total of Promoters', '<td class="">', '</td>', 1, 5 )
            self.result_dict['totalPromoterQ1'], self.result_dict['totalPromoterQ2'], self.result_dict['totalPromoterQ3'],\
            self.result_dict['totalPromoterQ4'] ,self.result_dict['totalPromoterQ5'] = result['output']

            result = self.splitString(source, '<strong>Institutions</strong>', '<td class="">', '</td>', 1, 5 )
            self.result_dict['totalInstitQ1'], self.result_dict['totalInstitQ2'], self.result_dict['totalInstitQ3'],\
            self.result_dict['totalInstitQ4'], self.result_dict['totalInstitQ5'] = result['output']

            result = self.splitString(source, 'Foreign Institutional Investors</td>', '<td class="">', '</td>', 1, 5 )
            self.result_dict['FIIQ1'], self.result_dict['FIIQ2'], self.result_dict['FIIQ3'], self.result_dict['FIIQ4'],\
            self.result_dict['FIIQ5'] = result['output']

            result = self.splitString(source, 'Financial Institutions / Banks</td>', '<td class="">', '</td>', 1, 5 )
            self.result_dict['FinInstitQ1'],  self.result_dict['FinInstitQ2'], self.result_dict['FinInstitQ3'],\
            self.result_dict['FinInstitQ4'], self.result_dict['FinInstitQ4'] = result['output']

            result = self.splitString(source, 'Mutual  Funds / UTI</td', '<td class="">', '</td>', 1, 5 )
            self.result_dict['MFQ1'], self.result_dict['MFQ2'], self.result_dict['MFQ3'], self.result_dict['MFQ4'],\
            self.result_dict['MFQ5'] = result['output']

            print("in percent                %s\t%s\t%s\t%s\t%s" % (self.result_dict['PHQuater1'], self.result_dict['PHQuater2'],\
            self.result_dict['PHQuater3'], self.result_dict['PHQuater4'], self.result_dict['PHQuater5'] ))
            print("Tot PH                  : %s\t\t%s\t\t%s\t\t%s\t\t%s" % (self.result_dict['totalPromoterQ1'], self.result_dict['totalPromoterQ2'],\
            self.result_dict['totalPromoterQ3'], self.result_dict['totalPromoterQ4'] ,self.result_dict['totalPromoterQ5']))
            print("Tot Institutions        : %s\t\t%s\t\t%s\t\t%s\t\t%s" % (self.result_dict['totalInstitQ1'], self.result_dict['totalInstitQ2'],\
            self.result_dict['totalInstitQ3'], self.result_dict['totalInstitQ4'], self.result_dict['totalInstitQ5']))
            print("Financial Institutions  : %s\t\t%s\t\t%s\t\t%s\t\t%s\n" % (self.result_dict['FinInstitQ1'],  self.result_dict['FinInstitQ2'],
            self.result_dict['FinInstitQ3'], self.result_dict['FinInstitQ4'], self.result_dict['FinInstitQ4']))
            print("FII                     : %s\t\t%s\t\t%s\t\t%s\t\t%s" % (self.result_dict['FIIQ1'], self.result_dict['FIIQ2'],\
            self.result_dict['FIIQ3'], self.result_dict['FIIQ4'],self.result_dict['FIIQ5']))
            print("Mutal Funds             : %s\t\t%s\t\t%s\t\t%s\t\t%s" % (self.result_dict['MFQ1'], self.result_dict['MFQ2'],\
            self.result_dict['MFQ3'], self.result_dict['MFQ4'], self.result_dict['MFQ5']))
            return True

        except Exception,e:
            print 'faild in getPromotorHoldings loop',str(e)
            return False

    def getCashFlowData(self):
        try:
            cashFlow_source = myUrlopen(self.cashFlow_link)
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
                
                """ The order of variables is important """
                self.stockSymbol, self.result_dict['EPS_Q1'],  self.result_dict['EPS_Q2'],  self.result_dict['EPS_Q3'],\
                self.result_dict['EPS_Q4'], self.result_dict['EPS_Q1YoY'],self.result_dict['EPS_Q2YoY'],\
                self.result_dict['EPS_Q3YoY'], self.result_dict['EPS_Q4YoY'], self.result_dict['Q1Name'],\
                self.result_dict['Q2Name'], self.result_dict['Q3Name'], self.result_dict['Q4Name'],\
                self.result_dict['EPSQ1Change'], self.result_dict['EPSQ2Change'], self.result_dict['EPSQ3Change'],\
                self.result_dict['EPSQ4Change'], self.result_dict['Y1Name'], self.result_dict['Y2Name'],\
                self.result_dict['Y3Name'], self.result_dict['Y4Name'], self.result_dict['EPS_Y1'],\
                self.result_dict['EPS_Y2'], self.result_dict['EPS_Y3'], self.result_dict['EPS_Y4'],\
                self.result_dict['EPSY1Change'], self.result_dict['EPSY2Change'], self.result_dict['EPSY3Change'],\
                self.result_dict['reportType'] = row
                
                conn.close()
                return True
                
                if common_code.is_stock_blacklisted(self.stockSymbol) == True:
                    return False

            print "Get data from web old data in DB ==============", self.stockSymbol, row[common_code.DBindex_Q1Name]
            common_code.dataBase_outdate_stocks += 1

        except Exception,e:
            print 'Exception while reading DB section. May be you wanna fix them.',str(e)
            import time
            time.sleep(5)
            
        print "web access needed..."

        try:
            try:
                """ Lets start with consolidated and fallback to standalone if not available"""
                reportType = 'Consolidated'
                step = -2
                self.EPS_Quaterly_1_Source = myUrlopen(self.EPS_Quaterly_1[reportType])
                sourceCode = self.EPS_Quaterly_1_Source
                Q1 = float(sourceCode.split('EPS (Rs)</td>')[1].split('<td class="">')[1].split('</td>')[0])                
            except Exception,e:
                print "exception in consolidated"
                step = -1
                reportType = 'Standalone'
                self.EPS_Quaterly_1_Source = myUrlopen(self.EPS_Quaterly_1[reportType])
                sourceCode = self.EPS_Quaterly_1_Source
                Q1 = float(sourceCode.split('EPS (Rs)</td>')[1].split('<td class="">')[1].split('</td>')[0])
            step = 0
            self.EPS_Quaterly_2_Source = myUrlopen(self.EPS_Quaterly_2[reportType])
            sourceCode = self.EPS_Quaterly_1_Source
            
            step = 1
            result = self.splitString(sourceCode, 'EPS (Rs)</td>', '<td class="">', '</td>', 2, 4)
            if result['success'] == 0:
                return False

            output = result['output']           
            Q2, Q3, Q4, Q1YoY = output
            
            step = 2
            sourceCode = self.EPS_Quaterly_2_Source
            
            result = self.splitString(sourceCode, 'EPS (Rs)</td>', '<td class="">', '</td>', 1, 3)            
            Q2YoY, Q3YoY, Q4YoY = result['output']            

            step = 3
            sourceCode = self.EPS_Quaterly_1_Source            
            result = self.splitString(sourceCode, 'Figures in Rs crore</td>', '<td class="tdh">', '</td>', 1, 4)
            self.result_dict['Q1Name'], self.result_dict['Q2Name'],self.result_dict['Q3Name'],\
            self.result_dict['Q4Name'] = result['output']
            self.result_dict['EPS_Q1'] = float(Q1)
            self.result_dict['EPS_Q2'] = float(Q2)
            self.result_dict['EPS_Q3'] = float(Q3)
            self.result_dict['EPS_Q4'] = float(Q4)
            self.result_dict['EPS_Q1YoY'] = float(Q1YoY)
            self.result_dict['EPS_Q2YoY'] = float(Q2YoY)
            self.result_dict['EPS_Q3YoY'] = float(Q3YoY)
            self.result_dict['EPS_Q4YoY'] = float(Q4YoY)

            step = 4
            """ We make all 0 to 0.1
            """
            Q1YoY = 0.1 if Q1YoY == 0 else float(Q1YoY)
            Q2YoY = 0.1 if Q2YoY == 0 else float(Q2YoY)
            Q3YoY = 0.1 if Q3YoY == 0 else float(Q3YoY)
            Q4YoY = 0.1 if Q4YoY == 0 else float(Q4YoY)

            self.result_dict['EPSQ1Change'] = (float(Q1) - Q1YoY)/Q1YoY*100
            self.result_dict['EPSQ2Change'] = (float(Q2) - Q2YoY)/Q2YoY*100
            self.result_dict['EPSQ3Change'] = (float(Q3) - Q3YoY)/Q3YoY*100
            self.result_dict['EPSQ4Change'] = (float(Q4) - Q4YoY)/Q4YoY*100
            step = 5
            source = myUrlopen(self.finacialOverview_link[reportType])

            try:
                result = self.splitString(source, 'Earning Per Share (Rs)</td>', '<td class="">', '</td>', 1, 3)
                Y1, Y2, Y3 = result['output']

                result = self.splitString(source, 'Particulars ', '<td class="tdh">', '</td>', 1, 3)
                self.result_dict['Y1Name'], self.result_dict['Y2Name'], self.result_dict['Y3Name'] = result['output']

                source = myUrlopen(self.finacialOverview_link1[reportType])

                result = self.splitString(source, 'Earning Per Share (Rs)</td>', '<td class="">', '</td>', 1, 1)
                Y4 = result['output'][0]
                
                result = self.splitString(source, 'Particulars ',  '<td class="tdh">', '</td>', 1, 1)
                self.result_dict['Y4Name'] = result['output'][0]
            except Exception,e:
                print 'failed when spliting finacialoverview link trying finacialPL link',str(e)
                print 'failed link ', self.finacialOverview_link1[reportType]
                source = myUrlopen(self.finacialPL_link[reportType])
                step = 6
                result = self.splitString(source, '<td class="tdL" colspan="0">Earning Per Share (Rs.)</td>',
                                         '<td class="amount">', '</td>', 1, 3)
                Y1, Y2, Y3 = result['output']
                
                step = 7
                result = self.splitString(source, 'Figures in Rs crore</td>', '<td class="tdh">' ,'</td>', 1, 3)
                self.result_dict['Y1Name'], self.result_dict['Y2Name'], self.result_dict['Y3Name'] = result['output']
                
                step = 8
                source = myUrlopen(self.finacialPL_link1[reportType])
                step = 9               
                result = self.splitString(source, '<td class="tdL" colspan="0">Earning Per Share (Rs.)</td>', 
                                            '<td class="amount">', '</td>', 1, 1)
                Y4 = result['output'][0]
                result = self.splitString(source, 'Figures in Rs crore</td>', '<td class="tdh">', '</td>', 1, 1 )
                self.result_dict['Y4Name'] = result['output'][0]                
                print 'second link succesfull'
            step = 10
            self.result_dict['EPS_Y1'] = Y1
            self.result_dict['EPS_Y2'] = Y2
            self.result_dict['EPS_Y3'] = Y3
            self.result_dict['EPS_Y4'] = Y4

            """ We make all 0 denomenators to 0.1 to avoid divide by zero
            """
            Y2 = 0.1 if float(Y2) == 0.00 else Y2
            Y3 = 0.1 if float(Y3) == 0.00 else Y3
            Y4 = 0.1 if float(Y4) == 0.00 else Y4
            step = 11
            self.result_dict['EPSY1Change'] = ((float(Y1) - float(Y2))/float(Y2))*100
            self.result_dict['EPSY2Change'] = ((float(Y2) - float(Y3))/float(Y3))*100            
            self.result_dict['EPSY3Change'] = ((float(Y3) - float(Y4))/float(Y4))*100
            step = 12
            c.execute("CREATE TABLE IF NOT EXISTS STOCKDATA \
                (symbol, EPS_Q1, EPS_Q2, EPS_Q3, EPS_Q4, \
                EPS_Q1YoY, EPS_Q2YoY, EPS_Q3YoY, EPS_Q4YoY,\
                Q1Name, Q2Name, Q3Name, Q4Name,\
                EPSQ1Change, EPSQ2Change, EPSQ3Change, EPSQ4Change,\
                Y1Name, Y2Name, Y3Name, Y4Name,\
                EPS_Y1, EPS_Y2, EPS_Y3, EPS_Y4,\
                EPSY1Change, EPSY2Change, EPSY3Change, reportType)")
            step = 13
            #print "Updating symbol... ", self.stockSymbol
            c.execute('''DELETE FROM STOCKDATA WHERE symbol = ?''', (self.stockSymbol,))

            self.result_dict['reportType'] = reportType
            step = 14
            c.execute('''INSERT INTO STOCKDATA(symbol, EPS_Q1, EPS_Q2, EPS_Q3, EPS_Q4, \
              EPS_Q1YoY, EPS_Q2YoY, EPS_Q3YoY, EPS_Q4YoY,\
              Q1Name, Q2Name, Q3Name, Q4Name,\
              EPSQ1Change, EPSQ2Change, EPSQ3Change, EPSQ4Change,\
              Y1Name, Y2Name, Y3Name, Y4Name,\
              EPS_Y1, EPS_Y2, EPS_Y3, EPS_Y4,\
              EPSY1Change, EPSY2Change, EPSY3Change, reportType)\
              values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, ?)''',
              (self.stockSymbol, self.result_dict['EPS_Q1'],  self.result_dict['EPS_Q2'],  self.result_dict['EPS_Q3'],  self.result_dict['EPS_Q4'],
              self.result_dict['EPS_Q1YoY'],self.result_dict['EPS_Q2YoY'], self.result_dict['EPS_Q3YoY'], self.result_dict['EPS_Q4YoY'],
              self.result_dict['Q1Name'], self.result_dict['Q2Name'], self.result_dict['Q3Name'], self.result_dict['Q4Name'],
              self.result_dict['EPSQ1Change'], self.result_dict['EPSQ2Change'], self.result_dict['EPSQ3Change'], self.result_dict['EPSQ4Change'],
              self.result_dict['Y1Name'], self.result_dict['Y2Name'], self.result_dict['Y3Name'], self.result_dict['Y4Name'],
              self.result_dict['EPS_Y1'], self.result_dict['EPS_Y2'], self.result_dict['EPS_Y3'], self.result_dict['EPS_Y4'],
              self.result_dict['EPSY1Change'], self.result_dict['EPSY2Change'], self.result_dict['EPSY3Change'], reportType))

            if self.latestQtrName == self.result_dict['Q1Name']:
                common_code.dataBase_updated_stocks += 1

            conn.commit()
            conn.close()

            print ("dataBase: out of outdated stocks = %d, updated = %d" % (common_code.dataBase_outdate_stocks, common_code.dataBase_updated_stocks))
            return True;

        except Exception,e:
            print 'failed in getEPSdata Report_bussinesStd loop',str(e)
            print 'step = ', step
            print 'report type ', reportType
            if step == 1:
                print self.EPS_Quaterly_1[reportType]
            if step == 2:
                print self.EPS_Quaterly_2[reportType]
                
            return False

    def getRatios(self):
        try:
            ratioSource = myUrlopen(self.ratio_link)
            result = self.splitString(ratioSource, 'Return on Net Worth (%)</td>', '<td class="">' ,'</td>', 1, 3)
            returnOnNetWorth_year1, returnOnNetWorth_year2, returnOnNetWorth_year3 = result['output']

            result = self.splitString(ratioSource, '<td class="tdh tdC">Ratios</td>', '<td class="tdh">' ,'</td>', 1, 3)
            year1, year2, year3 = result['output']

            result = self.splitString(ratioSource, 'Debt-Equity Ratio</td>', '<td class="">' ,'</td>', 1, 3)
            debtToEquity_year1, debtToEquity_year2, debtToEquity_year3 = result['output']

            result = self.splitString(ratioSource, 'Interest Coverage ratio</td>', '<td class="">' ,'</td>', 1, 3)
            interestCoverage_year1, interestCoverage_year2, interestCoverage_year3 = result['output']

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
