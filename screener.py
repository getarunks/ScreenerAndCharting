import google_json_extract
import BS_json_extract
import BS_get_and_decode_webpage
import DB_api
import common_code

def getReportType(consolidated):
    if consolidated == 0:
        reportType = 'Standalone'
    else:
        reportType = 'Consolidated'
    return reportType

##### All command line function below

 #Add stock list here to run Beat command
stockListBeat = ["LUMAXAUTO", "PUNJABCHEM" ]

class EPSData:
    def __init__(self):
        self.yearName = []
        self.annualEPS = []
        self.yearChange = []
        self.qtrName= []
        self.qtrEPS = []
        self.qtrYoYEPS = []
        self.qtrChange = []

def compFormatFailed(stockSymbol):
    if common_code.completeReportRunning == 0:
        return input('Please enter Bussiness std stock ID for %s \' \': ' % (stockSymbol))
    else:
        return False

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
    common_code.mySleep(1)
    epsData_array = [EPSData() for i in range(length+1)]

    count = index = 0
    for stock in stockListBeat:
        print ("Analysing %s index = %d filtered so far = %d" % (stock, count, index))
        cf = BS_json_extract.compFormat_bussinesStd(stock)
        cf.get_compFormat()
        if cf.result == 'NODATA':
            print 'No Data for: ' + stock
            del cf
            return

        reportType = getReportType(0)
        BSdata = BS_get_and_decode_webpage.getData_bussinesStd(cf.result, stock, reportType)
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
        EPS = BSdata.result_dict['EPS_Q1'] +  BSdata.result_dict['EPS_Q2'] + \
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
        cf = BS_json_extract.compFormat_bussinesStd(n[0])
        cf.get_compFormat()
        if cf.result == 'NODATA':
            print 'No Data for: ' + stock
            cf.result = compFormatFailed(stock)
            if cf.result == False:
                del cf
                return False

        reportType = getReportType(0)
        BSdata = BS_get_and_decode_webpage.getData_bussinesStd(cf.result, stock,  reportType)

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
        textFile.write("Symbol: %s \tTTM EPS: %s \tAv. EPS growth(last 2 Qtrs): %d%s\n" % \
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

def getCashFlow(stockSymbol, consolidated):
    cf = BS_json_extract.compFormat_bussinesStd(stockSymbol)
    cf.get_compFormat()
    if cf.result == 'NODATA':
        print 'No Data for: ' + stockSymbol
        cf.result = compFormatFailed(stockSymbol)
        if cf.result == False:
            del cf
            return False

    reportType = getReportType(consolidated)
    report = BS_get_and_decode_webpage.getData_bussinesStd(cf.result, stockSymbol, reportType)
    if report.getCashFlowData() == False:
        print stockSymbol + ' error fetching data'
        del cf
        return
    del cf, report

def getPH(stockSymbol):
    cf = BS_json_extract.compFormat_bussinesStd(stockSymbol)
    cf.get_compFormat()
    if cf.result == 'NODATA':
        print 'No Data for: ' + stockSymbol
        cf.result = compFormatFailed(stockSymbol)
        if cf.result == False:
            del cf
            return False

    report = BS_get_and_decode_webpage.getData_bussinesStd(cf.result, stockSymbol, 'doesntmatter')
    if report.getPromotorHoldings() == False:
        print stockSymbol + ' error fetching data'
        del cf
        return
    del cf, report

def getRatios(stockSymbol, consolidated):
    cf = BS_json_extract.compFormat_bussinesStd(stockSymbol)
    cf.get_compFormat()
    if cf.result == 'NODATA':
        print 'No Data for: ' + stockSymbol
        cf.result = compFormatFailed(stockSymbol)
        if cf.result == False:
            del cf
            return False

    reportType = getReportType(consolidated)
    report = BS_get_and_decode_webpage.getData_bussinesStd(cf.result, stockSymbol, reportType)
    if report.getRatios() == False:
        print stockSymbol + ' error fetching data'
        del cf
    #del cf, report

def getEPSG(stockSymbol, consolidated):
    reportType = getReportType(consolidated)
    cf = BS_json_extract.compFormat_bussinesStd(stockSymbol)
    cf.get_compFormat()
    if cf.result == 'NODATA':
        print 'No Data for: ' + stockSymbol
        cf.result = compFormatFailed(stockSymbol)
        if cf.result == False:
            del cf
            return False

    reportType = getReportType(consolidated)
    report = BS_get_and_decode_webpage.getData_bussinesStd(cf.result, stockSymbol, reportType)
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
    googleSceernerData = google_json_extract.google_sceerner_json_DataExtract()
    googleSceernerData.retrieve_stock_data()
    googleSceernerData.result_df.to_csv(r'google-data.csv', index=False)

    textFile = open("FirstReport.txt", "w")

    metStocks_CANSLIM = []
    metStocks_4qtrs = []
    metStocks_3qtrs = []
    metStocks_2qtrs = []
    failedStocks = []

    common_code.completeReportRunning = 1
    index = 0
    condMetOnce = 0
    for stockSymbol in googleSceernerData.result_df['SYMBOL']:
        print("Processing stock %s, index = %d out of %d\n" %  (stockSymbol, index, (len(googleSceernerData.result_df['SYMBOL']))))
        report = getEPSG(stockSymbol, 0)
        if report == False:
            failedStocks.append(stockSymbol)
            index +=1
            continue
        #ignore negative EPS stocks
        elif report.result_dict['EPS_Q1'] < 0:
            index +=1
            continue
        elif report.result_dict['EPSQ1Change'] >= float(EPSQtrAlone) and\
            report.result_dict['EPSQ2Change'] >= float(EPSQtrAlone) and\
            report.result_dict['EPSQ3Change'] >= float(EPSQtrAlone) and\
            report.result_dict['EPSQ4Change'] >= float(EPSQtrAlone):
            textFile.write("%s meets your stringent 4 qtr EPSG requirement\n" % (stockSymbol))
            textFile.flush()
            metStocks_4qtrs.append(stockSymbol)
            print "meets requirement"
            condMetOnce = 1
        elif report.result_dict['EPSQ1Change'] >= float(EPSQtrAlone) and\
            report.result_dict['EPSQ2Change'] >= float(EPSQtrAlone) and\
            report.result_dict['EPSQ3Change'] >= float(EPSQtrAlone):
            textFile.write("%s meets your stringent 3 qtr EPSG requirement\n" % (stockSymbol))
            metStocks_3qtrs.append(stockSymbol)
            condMetOnce = 1
        elif report.result_dict['EPSQ1Change'] >= float(EPSQtrAlone) and\
            report.result_dict['EPSQ2Change'] >= float(EPSQtrAlone):
            textFile.write("%s meets your stringent 2 qtr EPSG requirement\n" % (stockSymbol))
            metStocks_2qtrs.append(stockSymbol)
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
    print("%d stocks meets 2 qtr criteria\n" % len(metStocks_2qtrs))
    print metStocks_2qtrs
    print("%d stocks meets CANSLIM criteria\n" % len(metStocks_CANSLIM))
    print metStocks_CANSLIM
    print ("%d stocks failed to find in Bussiness std\n" % len(failedStocks))
    print failedStocks

    textFile.write("Following stocks have %s growth for last 4 quaters:\n" % (EPSQtrAlone))
    json.dump(metStocks_4qtrs, textFile)
    textFile.write("\n")
    textFile.write("Following stocks have %s growth for last 3 quaters:\n" % (EPSQtrAlone))
    json.dump(metStocks_3qtrs, textFile)
    textFile.write("\n")
    textFile.write("Following stocks have %s growth for last 2 quaters:\n" % (EPSQtrAlone))
    json.dump(metStocks_2qtrs, textFile)
    textFile.write("\n")
    textFile.write("Following stocks have met CANSLIM Y1: %s, Y2: %s, Y3: %s Cur Qtr %s:\n" % (EPSY1, EPSY2, EPSY3, EPSCurrQtr))
    json.dump(metStocks_CANSLIM, textFile)
    textFile.write("\n")
    textFile.write("Following stocks failed to find in Buss Std\n")
    json.dump(failedStocks, textFile)
    textFile.write("\n")

    print ("dataBase out of outdated stocks = %d, updated = %d\n" % (common_code.dataBase_outdate_stocks, common_code.dataBase_updated_stocks))
    textFile.write("dataBase out of outdated stocks = %d, updated = %d\n" % (common_code.dataBase_outdate_stocks, common_code.dataBase_updated_stocks))
    textFile.close()
    common_code.completeReportRunning = 0
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
