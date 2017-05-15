"""
Set of apis to read the derails of DB.
"""
import pandas, sqlite3
import google_json_extract
import BS_json_extract
import BS_get_and_decode_webpage
import common_code
#http://pythoncentral.io/introduction-to-sqlite-in-python/
def deleteDB():
    sqlite_file = common_code.sqliteFile
    conn =sqlite3.connect(sqlite_file)
    c = conn.cursor()

    c.execute("DROP TABLE YEARLYSTOCKDATA")
    c.execute("DROP TABLE QUATERLYSTOCKDATA")
    conn.commit()
    conn.close()

"""
Template showing how to upate a stock. Not realy used. Kept for reference.
"""
def update_DB(stock, eps):
    sqlite_file = common_code.sqliteFile
    conn =sqlite3.connect(sqlite_file)
    c = conn.cursor()

    c.execute('''UPDATE STOCKDATA SET Q1EPS = ? WHERE SYMBOL = ?''', (eps, stock))
    conn.commit()
    conn.close()
    
def DB_Details():
    conn = sqlite3.connect(common_code.sqliteFile)
    c = conn.cursor()
    cursor = c.execute("SELECT symbol,Y1EPS, Y2EPS, Y3EPS, Y4EPS, \
                Y1Name, Y2Name, Y3Name, Y4Name,\
                EPSY1Change, EPSY2Change, EPSY3Change,\
                EBIT, TotAssest, CurLiability, MarketCap,\
                TotDebt, CurrYear, EarningsYield, RoC, \
                reportType from YEARLYSTOCKDATA")

    total_stocks = 0
    yearlyUptodateStocks = 0
    prevYearlyUptodateStocks = 0
    marCap_lessThan100 = marCap_100to500 = marCap_500to1000 = marCap_1000to5000 = marCap_5000to10000 = marCap_10000to20000 = marCap_above20000 = 0
    stmtConsolidated = 0
    
    for row in cursor:
        total_stocks +=1
        if row[common_code.YearlyIndex_Y1Name] == common_code.current_year:
            yearlyUptodateStocks += 1
            
        if row[common_code.YearlyIndex_Y1Name] == common_code.previous_year:
            prevYearlyUptodateStocks += 1

        eV = float(row[common_code.YearlyIndex_MarketCap]) + float(row[common_code.YearlyIndex_TotDebt])
        if eV < 100:
            marCap_lessThan100 += 1
        if eV >= 100 and eV < 500:
            marCap_100to500 +=1
        if eV >= 500 and eV < 1000:
            marCap_500to1000 +=1
        if eV >= 1000 and eV < 5000:
            marCap_1000to5000 +=1
        if eV >= 5000 and eV < 10000:
            marCap_5000to10000 +=1
        if eV >= 10000 and eV < 20000:
            marCap_10000to20000 +=1
        if eV >= 20000:
            marCap_above20000 +=1
            
        if row[common_code.YearlyIndex_reportType] == 'Consolidated':
            stmtConsolidated += 1
    
    print("Yearly stock DB details: \n")
    print("Total stocks                                         = %d" % total_stocks)
    print("Stocks having data updated to year (%s)            = %d" % (common_code.current_year, yearlyUptodateStocks))
    print("Stocks having data updated to year (%s)            = %d" % (common_code.previous_year, prevYearlyUptodateStocks))
    print("No of stocks catagorized w.r.t Enterprise Value")
    print("          Enterprise Value < 100 Cr                  = %d"% marCap_lessThan100)
    print("100    <  Enterprise Value < 500                     = %d"% marCap_100to500)
    print("500    <  Enterprise Value < 1,000                   = %d"% marCap_500to1000)
    print("1,000  <  Enterprise Value < 5,000                   = %d"% marCap_1000to5000)
    print("5,000  <  Enterprise Value < 10,000                  = %d"% marCap_5000to10000)
    print("10,000 <  Enterprise Value < 20,000                  = %d"% marCap_10000to20000)
    print("20,000 <  Enterprise Value                           = %d"% marCap_above20000)
    
    print("Stocks with consolidated report                      = %d"% stmtConsolidated)
    conn.close()
    
    conn = sqlite3.connect(common_code.sqliteFile)
    c = conn.cursor()
    cursor = c.execute("SELECT symbol, EPS_Q1, EPS_Q2, EPS_Q3, EPS_Q4, \
              EPS_Q1YoY, EPS_Q2YoY, EPS_Q3YoY, EPS_Q4YoY,\
              Q1Name, Q2Name, Q3Name, Q4Name,\
              EPSQ1Change, EPSQ2Change, EPSQ3Change, EPSQ4Change,\
              EBIT_Q1, EBIT_Q2, EBIT_Q3, EBIT_Q4,\
              reportType from QUATERLYSTOCKDATA")
              
    stmtConsolidated = totalStocks = 0
    qtrlyUptodateStocks = prevQtrlyUptodateStocks = 0
    
    for row in cursor:
        totalStocks +=1
        if row[common_code.QuaterlyIndex_Q1Name] == common_code.current_qtr:
            qtrlyUptodateStocks +=1
        if row[common_code.QuaterlyIndex_Q1Name] == common_code.previous_qtr:
            prevQtrlyUptodateStocks +=1
        if row[common_code.QuaterlyIndex_reportType] == 'Consolidated':
            stmtConsolidated += 1
    
    print("Quaterly stock DB details: \n")
    print("Total stocks                                    = %d" % total_stocks)
    print("Stocks having data updated to Qtr (%s)    = %d" % (common_code.current_qtr, qtrlyUptodateStocks))
    print("Stocks having data updated to Qtr (%s)    = %d" % (common_code.previous_qtr, prevQtrlyUptodateStocks))
    print("Stocks with consolidated report                 = %d" % stmtConsolidated)
    conn.close()  
    
def print_selected(selected_stock_list, stock_dict_allDetails):
    for each_stock in selected_stock_list:
        symbol , roc = each_stock
        each_dict = stock_dict_allDetails[symbol]
        print "=================="
        print "symbol           = ", each_dict['symbol']
        print "Report Type      = ", each_dict['reportType']
        print "Quarter          = ", each_dict['qtrName']
        print "Yearly           = ", each_dict['curYear']
        print " "
        print "RoC              = ", each_dict['RoC']
        print "Earnings Yield   = ", each_dict['eYield']
        print "Market Cap       = ", each_dict['marCap']
        print "Total Debt       = ", each_dict['totDebt']
        print "Operating Profit = ", each_dict['opProfit']
        print "current Liab     = ", each_dict['currLiab']
        print "Total Assets     = ", each_dict['totAss']


def _get_qtrTTM_EBIT(stockSymbol, stock_dict_perDetails):
    conn =sqlite3.connect(common_code.sqliteFile)
    c = conn.cursor()
    sql_cmd = "SELECT * FROM QUATERLYSTOCKDATA WHERE symbol=?"
    c.execute(sql_cmd, [(stockSymbol)])
    row = c.fetchone()
    total =  row[common_code.QuaterlyIndex_EBIT_Q1] + row[common_code.QuaterlyIndex_EBIT_Q2] + \
                row[common_code.QuaterlyIndex_EBIT_Q3] + row[common_code.QuaterlyIndex_EBIT_Q4]
    #print "TTM QTR EBIT ", stockSymbol, total
    stock_dict_perDetails['qtrName'] = row[common_code.QuaterlyIndex_Q1Name]
    stock_dict_perDetails['opProfit'] = total
    conn.close()
    return total

def filterStocksDB_Beat(min_eV = 0, max_ev = 100000000):
    use_qtr_EBIT = True
    conn = sqlite3.connect(common_code.sqliteFile)
    c = conn.cursor()
    cursor_yearly = c.execute("SELECT symbol,Y1EPS, Y2EPS, Y3EPS, Y4EPS, \
                Y1Name, Y2Name, Y3Name, Y4Name,\
                EPSY1Change, EPSY2Change, EPSY3Change,\
                EBIT, TotAssest, CurLiability, MarketCap,\
                TotDebt, CurrYear, EarningsYield, RoC, \
                reportType from YEARLYSTOCKDATA")

    stock_dict_RoC = {}
    stock_dict_eYield = {}
    total_stocks = 0
    """ 
    This is a dictonary of dictonary.
    stock_dict_allDetails ={
        'IBM': {'symbol': 'IBM', 'currLiab' : 234234, 'totAss' : 45454,.... }
        'TCS': {'symbol': 'TCS', 'currLiab' : 123214, 'totAss' : 71267,.... }
        }
    """
    stock_dict_allDetails = {}
        
    print "Parsing Yearly database and populating dictionary...."
    for row in cursor_yearly:
        total_stocks +=1
                
        eV = float(row[common_code.YearlyIndex_MarketCap]) + float(row[common_code.YearlyIndex_TotDebt])
        if (eV < min_eV) or (eV > max_ev):
            continue
       
        stock_dict_RoC[row[common_code.YearlyIndex_symbol]] = row[common_code.YearlyIndex_RoC]
        stock_dict_eYield[row[common_code.YearlyIndex_symbol]] = row[common_code.YearlyIndex_EarningsYield]
        """ This declartion should be inside the for loop to create different instance of stock_dict_perDetais"""
        stock_dict_perDetails = {}
        stock_dict_perDetails['symbol'] = row[common_code.YearlyIndex_symbol]
        stock_dict_perDetails['currLiab'] = row[common_code.YearlyIndex_CurLiability]
        stock_dict_perDetails['totAss'] = row[common_code.YearlyIndex_TotAssest]
        """
        if EBIT is quaterly, we can read it now. If we did it will break this for loop.
        If use_qtr_EBIT is true, opProfit will be filled after this for loop.
        """
        if use_qtr_EBIT == False:
            stock_dict_perDetails['opProfit'] = row[common_code.YearlyIndex_EBIT]
        stock_dict_perDetails['RoC'] = row[common_code.YearlyIndex_RoC]
        stock_dict_perDetails['marCap'] = row[common_code.YearlyIndex_MarketCap]
        stock_dict_perDetails['totDebt'] = row[common_code.YearlyIndex_TotDebt]
        stock_dict_perDetails['curYear'] = row[common_code.YearlyIndex_CurrYear]
        stock_dict_perDetails['eYield'] = row[common_code.YearlyIndex_EarningsYield]
        stock_dict_perDetails['reportType'] = row[common_code.YearlyIndex_reportType]
        
        stock_dict_allDetails[row[common_code.YearlyIndex_symbol]] = stock_dict_perDetails
        
        sort_list_roc = [(k,v) for v,k in sorted(
                    [(v,k) for k,v in stock_dict_RoC.items()], reverse=True)]
        sort_list_eY = [(k,v) for v,k in sorted(
                    [(v,k) for k,v in stock_dict_eYield.items()], reverse=True)]
                    
    conn.close()

    if use_qtr_EBIT == True:
        print "Parsing Quarterly database and populating dictionary...."
        for item in stock_dict_allDetails:
            stock_dict_perDetails = stock_dict_allDetails[item]
            stock_dict_perDetails['opProfit'] = _get_qtrTTM_EBIT(item, stock_dict_perDetails)
    
    """
    we need to create a dict of ranks
    sotck_dict_ranks = {
        'IBM': {'eYRank': 32, 'RoCRank' : 65, 'netRank', 97}
        'TCS': {'eYRank': 102, 'RoCRank' : 5, 'netRank', 107}
        }
    """
  
    print "Ranking stocks w.r.t RoC..."
    allStock_dict_ranks = {}
    index = 0
    for stock in sort_list_roc:
        stock_dict_ranks = {}
        stock_dict_ranks['RoCRank'] = index
        allStock_dict_ranks[stock[0]] = stock_dict_ranks
        index += 1
    
    print "Ranking stocks w.r.t EarningsYield..."
    index = 0
    stock_dict_netRank = {}
    for stock in sort_list_eY:
        stock_dict_ranks = allStock_dict_ranks[stock[0]]
        stock_dict_ranks['eYRank'] = index
        stock_dict_ranks['netRank'] = stock_dict_ranks['RoCRank'] + stock_dict_ranks['eYRank']
        stock_dict_netRank[stock[0]] = stock_dict_ranks['netRank']
        sort_list_netRank = [(k,v) for v,k in sorted(
                    [(v,k) for k,v in stock_dict_netRank.items()], reverse=False)]
        index += 1 
        
    #print allStock_dict_ranks
    print "======================="
    #print sort_list_netRank[:30]
    print_selected(sort_list_netRank[:30], stock_dict_allDetails)
    #print_selected(sort_list_roc[:30], stock_dict_allDetails)
    return

"""
This function updates both yearly and quarterly results from bussiness standard website.
Stocks who has matching Yearly and quarterly with common_code(current_year, current_qtr) will not be fetched.
"""
def updateDB():
    googleSceernerData = google_json_extract.google_sceerner_json_DataExtract()
    googleSceernerData.retrieve_stock_data()
    googleSceernerData.result_df.to_csv(r'google-data.csv', index=False)
    
    common_code.DB_updateRunning = 1
    continue_from_here = common_code.update_start_index
    index = continue_from_here

    totalSymbols = len(googleSceernerData.result_df['SYMBOL'])
    failed_stocks = []
    
    if continue_from_here != 0:
        googleSceernerData.result_df['SYMBOL'] = googleSceernerData.result_df['SYMBOL'].tail(totalSymbols - continue_from_here)
        dataFrame = googleSceernerData.result_df[pandas.notnull(googleSceernerData.result_df['SYMBOL'])]
    else:
        dataFrame = googleSceernerData.result_df 
        
    for stockSymbol in dataFrame['SYMBOL']:
        print "======================================"
        print("Processing stock %s, index = %d out of %d" %  (stockSymbol, index, totalSymbols))
        #import time
        #time.sleep(2)
        if stockSymbol == 0:
            continue
        if common_code.is_stock_blacklisted(stockSymbol):
            print stockSymbol, " Blacklisted stock"
            index +=1
            continue

        cf = BS_json_extract.compFormat_bussinesStd(stockSymbol)
        cf.get_compFormat()
        if cf.result == 'NODATA':
            print 'No Data for: ' + stockSymbol
            index +=1
            continue

        report = BS_get_and_decode_webpage.getData_bussinesStd(cf.result, stockSymbol)
        if report.updateCompleteDataBase() == False:
            print stockSymbol + ' error fetching data'
            failed_stocks.append(stockSymbol)
        index +=1
        del cf
        
    print "Failed stocks..... few can be blacklisted"
    print failed_stocks
    del googleSceernerData

"""
Function written to test the updateAllDB().
This funciton allows to use updateCompleteDataBase for a particular stock.
"""
def updateSingleStockDB():
    
    stockSymbol = 'BFINVEST'
    cf = BS_json_extract.compFormat_bussinesStd(stockSymbol)
    cf.get_compFormat()
    if cf.result == 'NODATA':
        print 'No Data for: ' + stockSymbol
        return
    print "processing stock...", stockSymbol
    if common_code.is_stock_blacklisted(stockSymbol):
        print stockSymbol, " Blacklisted stock"
        return
    report = BS_get_and_decode_webpage.getData_bussinesStd(cf.result, stockSymbol)
    if report.updateCompleteDataBase() == False:
        print stockSymbol + ' error fetching data'
    del cf