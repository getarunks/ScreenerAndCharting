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

    c.execute("DROP TABLE STOCKDATA")
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

def readDB_Beat():
    
    conn = sqlite3.connect(common_code.sqliteFile)
    c = conn.cursor()
    cursor = c.execute("SELECT symbol, EBIT, TotAssest, CurLiability, MarketCap, \
                TotDebt, CurrYear, EarningsYield, RoC from BEATSTOCKDATA")
    
    stock_dict_RoC = {}
    total_stocks = 0
    for row in cursor:
        total_stocks +=1
        print row

        stock_dict_RoC[row[common_code.BeatDBindex_symbol]] = row[common_code.BeatDBindex_RoC]
        sort_list = [(k,v) for v,k in sorted(
                    [(v,k) for k,v in stock_dict_RoC.items()], reverse=True)]
    print sort_list
    conn.close()
    
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
