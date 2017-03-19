"""
Set of apis to read the derails of DB.
"""

import sqlite3
import common_code
#http://pythoncentral.io/introduction-to-sqlite-in-python/
def deleteDB():
    sqlite_file = common_code.sqliteFile
    conn =sqlite3.connect(sqlite_file)
    c = conn.cursor()

    c.execute("DROP TABLE BEATSTOCKDATA")
    conn.commit()
    conn.close()

def updateDB(stock, eps):
    sqlite_file = common_code.sqliteFile
    conn =sqlite3.connect(sqlite_file)
    c = conn.cursor()

    c.execute('''UPDATE STOCKDATA SET Q1EPS = ? WHERE SYMBOL = ?''', (eps, stock))
    conn.commit()
    conn.close()

def getDataDB(stock):
    sqlite_file = common_code.sqliteFile
    conn =sqlite3.connect(sqlite_file)
    c = conn.cursor()

    sql = "SELECT * FROM STOCKDATA WHERE symbol=?"

    c.execute(sql, [(stock)])
    row = c.fetchone()
    if row == None:
        print "No data"
        return

    print row[0], row[1]
    conn.close()
    
def BeatDB_Details():
    conn = sqlite3.connect(common_code.sqliteFile)
    c = conn.cursor()
    cursor = c.execute("SELECT symbol, EBIT, TotAssest, CurLiability, MarketCap, \
                TotDebt, CurrYear, EarningsYield, RoC,reportType from BEATSTOCKDATA")
                
    total_stocks = 0
    DB_updated_stocks = 0
    marCap_lessThan100 = marCap_100to500 = marCap_500to1000 = marCap_1000to5000 = marCap_5000to10000 = marCap_10000to20000 = marCap_above20000 = 0
    stmtConsolidated = 0
    
    for row in cursor:
        total_stocks +=1
        if row[common_code.BeatDBindex_currentYear] == common_code.current_year:
            DB_updated_stocks += 1

        eV = float(row[common_code.BeatDBindex_marketCap]) + float(row[common_code.BeatDBindex_totalDebt])
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
            
        if row[common_code.BeatDBindex_reportType] == 'Consolidated':
            stmtConsolidated += 1
    
    print("BEAT stock DB details: \n")
    print("Total stocks                             = %d" % total_stocks)
    print("Updated stocsk to current year (%s)      = %d" % (common_code.current_year, DB_updated_stocks))
    print("No of stocks catagorized w.r.t Enterprise Value")
    print("          Enterprise Value < 100 Cr      = %d"% marCap_lessThan100)
    print("100    <  Enterprise Value < 500         = %d"% marCap_100to500)
    print("500    <  Enterprise Value < 1,000       = %d"% marCap_500to1000)
    print("1,000  <  Enterprise Value < 5,000       = %d"% marCap_1000to5000)
    print("5,000  <  Enterprise Value < 10,000      = %d"% marCap_5000to10000)
    print("10,000 <  Enterprise Value < 20,000      = %d"% marCap_10000to20000)
    print("20,000 <  Enterprise Value               = %d"% marCap_above20000)
    
    print("Stocks with consolidated report          = %d"% stmtConsolidated)
    conn.close()
    
def print_selected(selected_stock_list, stock_dict_allDetails):
    for each_stock in selected_stock_list:
        symbol , roc = each_stock
        each_dict = stock_dict_allDetails[symbol]
        print "=================="
        print "symbol           = ", each_dict['symbol']
        print "RoC              = ", each_dict['RoC']
        print "Earnings Yield   = ", each_dict['eYield']
        print "Market Cap       = ", each_dict['marCap']
        print "Total Debt       = ", each_dict['totDebt']
        print "Operating Profit = ", each_dict['opProfit']
        print "current Liab     = ", each_dict['currLiab']
        print "Total Assets     = ", each_dict['totAss']
        print "Report Type      = ", each_dict['reportType']
        
def readDB_Beat(min_eV = 1000.00):
    conn = sqlite3.connect(common_code.sqliteFile)
    c = conn.cursor()
    cursor = c.execute("SELECT symbol, EBIT, TotAssest, CurLiability, MarketCap, \
                TotDebt, CurrYear, EarningsYield, RoC,reportType from BEATSTOCKDATA")

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
    
    for row in cursor:
        total_stocks +=1
                
        eV = float(row[common_code.BeatDBindex_marketCap]) + float(row[common_code.BeatDBindex_totalDebt])
        if eV < min_eV:
            continue
       
        stock_dict_RoC[row[common_code.BeatDBindex_symbol]] = row[common_code.BeatDBindex_RoC]
        stock_dict_eYield[row[common_code.BeatDBindex_symbol]] = row[common_code.BeatDBindex_earningsYield]
        """ This declartion should be inside the for loop to create different instance of stock_dict_perDetais"""
        stock_dict_perDetails = {}
        stock_dict_perDetails['symbol'] = row[common_code.BeatDBindex_symbol]
        stock_dict_perDetails['currLiab'] = row[common_code.BeatDBindex_currentLiabilites]
        stock_dict_perDetails['totAss'] = row[common_code.BeatDBindex_totalAssets]
        stock_dict_perDetails['opProfit'] = row[common_code.BeatDBindex_operatingProfit]
        stock_dict_perDetails['RoC'] = row[common_code.BeatDBindex_RoC]
        stock_dict_perDetails['marCap'] = row[common_code.BeatDBindex_marketCap]
        stock_dict_perDetails['totDebt'] = row[common_code.BeatDBindex_totalDebt]
        stock_dict_perDetails['curYear'] = row[common_code.BeatDBindex_currentYear]
        stock_dict_perDetails['eYield'] = row[common_code.BeatDBindex_earningsYield]
        stock_dict_perDetails['reportType'] = row[common_code.BeatDBindex_reportType]
        
        print "Adding symbol = ", row[common_code.BeatDBindex_symbol]
        
        stock_dict_allDetails[row[common_code.BeatDBindex_symbol]] = stock_dict_perDetails
        
        sort_list_roc = [(k,v) for v,k in sorted(
                    [(v,k) for k,v in stock_dict_RoC.items()], reverse=True)]
        sort_list_eY = [(k,v) for v,k in sorted(
                    [(v,k) for k,v in stock_dict_eYield.items()], reverse=True)]
    """
    we need to create a dict of ranks
    sotck_dict_ranks = {
        'IBM': {'eYRank': 32, 'RoCRank' : 65, 'netRank', 97}
        'TCS': {'eYRank': 102, 'RoCRank' : 5, 'netRank', 107}
        }
    """
  
    allStock_dict_ranks = {}
    index = 0
    for stock in sort_list_roc:
        stock_dict_ranks = {}
        stock_dict_ranks['RoCRank'] = index
        allStock_dict_ranks[stock[0]] = stock_dict_ranks
        index += 1
    
    index = 0
    stock_dict_netRank = {}
    for stock in sort_list_eY:
        stock_dict_ranks = allStock_dict_ranks[stock[0]]
        stock_dict_ranks['eYRank'] = index
        stock_dict_ranks['netRank'] = stock_dict_ranks['RoCRank'] + index
        stock_dict_netRank[stock[0]] = stock_dict_ranks['netRank']
        sort_list_netRank = [(k,v) for v,k in sorted(
                    [(v,k) for k,v in stock_dict_netRank.items()], reverse=False)]
        index += 1    
        
    print allStock_dict_ranks
    print "======================="
    print sort_list_netRank[:30]
    print_selected(sort_list_netRank[:30], stock_dict_allDetails)
    conn.close()
    return
    
def readDB(qtrName=None):
    sqlite_file = common_code.sqliteFile
    stocks_with_latest = 0
    total_stocks = 0
    verbose = 0

    conn =sqlite3.connect(sqlite_file)
    c = conn.cursor()
    cursor = c.execute("SELECT symbol, EPS_Q1, EPS_Q2, EPS_Q3, EPS_Q4, \
              EPS_Q1YoY, EPS_Q2YoY, EPS_Q3YoY, EPS_Q4YoY,\
              Q1Name, Q2Name, Q3Name, Q4Name,\
              EPSQ1Change, EPSQ2Change, EPSQ3Change, EPSQ4Change,\
              Y1Name, Y2Name, Y3Name, Y4Name,\
              EPS_Y1, EPS_Y2, EPS_Y3, EPS_Y4,\
              EPSY1Change, EPSY2Change, EPSY3Change \
              from STOCKDATA")
    for row in cursor:
        total_stocks += 1
        if verbose != False:
            print "Symbol = " , row[0], "EPS_Q1 = ", row[1], "EPS_Q2 = ", row[2], "EPS_Q3 = ", row[3], "EPS_Q4 = ", row[4]
            print "EPS_Q1YoY = ", row[5], "EPS_Q2YoY = ", row[6], "EPS_Q3YoY = ", row[7], "EPS_Q4YoY = ", row[8]
            print "Q1Name= ", row[9], "Q2Name= ", row[10], "Q3Name= ", row[11], "Q4Name= ", row[12]
            print "EPSQ1Change = ", row[13], "EPSQ2Change = ", row[14], "EPSQ3Change = ", row[15], "EPSQ4Change = ", row[16]
            print "Y1Name = ", row[17], "Y2Name = ", row[18], "Y3Name = ", row[19], "Y4Name = ", row[20]
            print "EPS_Y1 = ", row[21], "EPS_Y2 = ", row[22], "EPS_Y3 = ", row[23], "EPS_Y4 = ", row[24]
            print "EPSY1Change = ", row[25], "EPSY2Change = ", row[26],  "EPSY3Change = ", row[27]

        if qtrName != None and row[9] == qtrName:
            stocks_with_latest += 1
    conn.close()
    print "stocks with latest info: ", stocks_with_latest, "\ntotal stocks: ", total_stocks

def createDB():
    sqlite_file = common_code.sqliteFile
    epsdata = []
    epsdata.append(2.3)
    epsdata.append(3.4)

    conn =sqlite3.connect(sqlite_file)
    c = conn.cursor()

    c.execute("CREATE TABLE STOCKDATA \
              (symbol, EPS_Q1, EPS_Q2, EPS_Q3, EPS_Q4, \
              EPS_Q1YoY, EPS_Q2YoY, EPS_Q3YoY, EPS_Q4YoY,\
              Q1Name, Q2Name, Q3Name, Q4Name,\
              EPSQ1Change, EPSQ2Change, EPSQ3Change, EPSQ4Change,\
              Y1Name, Y2Name, Y3Name, Y4Name,\
              EPS_Y1, EPS_Y2, EPS_Y3, EPS_Y4,\
              EPSY1Change, EPSY2Change, EPSY3Change,\
              TTMEPS)")

    """
    c.execute("INSERT INTO STOCKDATA (symbol, Q1EPS)\
                VALUES(?)",epsdata[1])
    conn.commit()
    conn.close()
    return
    """

    for stock in stockListBeat:
        cf = compFormat_bussinesStd(stock)
        cf.get_compFormat()
        if cf.result == 'NODATA':
            print 'No Data for: ' + stock
            del cf
            return

        reportType = getReportType(0)
        BSdata = getData_bussinesStd(cf.result, stock, reportType)
        if BSdata.getEPSdata() == False:
            print 'get_averageEPS returned False'
            return

        """ Add EPS for last four quaters
        """
        TTMEPS = BSdata.result_dict['EPS_Q1'] +  BSdata.result_dict['EPS_Q1'] + \
                BSdata.result_dict['EPS_Q3'] +  BSdata.result_dict['EPS_Q4']

        c.execute('''INSERT INTO STOCKDATA(symbol, EPS_Q1, EPS_Q2, EPS_Q3, EPS_Q4, \
              EPS_Q1YoY, EPS_Q2YoY, EPS_Q3YoY, EPS_Q4YoY,\
              Q1Name, Q2Name, Q3Name, Q4Name,\
              EPSQ1Change, EPSQ2Change, EPSQ3Change, EPSQ4Change,\
              Y1Name, Y2Name, Y3Name, Y4Name,\
              EPS_Y1, EPS_Y2, EPS_Y3, EPS_Y4,\
              EPSY1Change, EPSY2Change, EPSY3Change,\
              TTMEPS)\
              values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
              (stock, BSdata.result_dict['EPS_Q1'],  BSdata.result_dict['EPS_Q2'],  BSdata.result_dict['EPS_Q3'],  BSdata.result_dict['EPS_Q4'],
              BSdata.result_dict['EPS_Q1YoY'],BSdata.result_dict['EPS_Q2YoY'], BSdata.result_dict['EPS_Q3YoY'], BSdata.result_dict['EPS_Q4YoY'],
              BSdata.result_dict['Q1Name'], BSdata.result_dict['Q2Name'], BSdata.result_dict['Q3Name'], BSdata.result_dict['Q4Name'],
              BSdata.result_dict['EPSQ1Change'], BSdata.result_dict['EPSQ2Change'], BSdata.result_dict['EPSQ3Change'], BSdata.result_dict['EPSQ4Change'],
              BSdata.result_dict['Y1Name'], BSdata.result_dict['Y2Name'], BSdata.result_dict['Y3Name'], BSdata.result_dict['Y4Name'],
              BSdata.result_dict['EPS_Y1'], BSdata.result_dict['EPS_Y2'], BSdata.result_dict['EPS_Y3'], BSdata.result_dict['EPS_Y4'],
              BSdata.result_dict['EPSY1Change'], BSdata.result_dict['EPSY2Change'], BSdata.result_dict['EPSY3Change'],
              TTMEPS))

    #http://stackoverflow.com/questions/7026911/sqlite-no-return-type-in-python
    conn.commit()
    conn.close()
