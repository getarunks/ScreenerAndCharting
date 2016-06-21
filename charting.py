# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 12:37:25 2016

@author: arunks

candlestick was not found error

type the follwing commands to see the exact keyword.
import matplotlib
dir(matplotlib.finance)

it was candlestick_ochl

"""
import urllib2
import time
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import matplotlib
from matplotlib.finance import candlestick_ochl
from urllib2 import urlopen
import pickle
import pandas as pd
matplotlib.rcParams.update({'font.size':9})

slowMA = '#5a6de3'
fastMA = '#b93904'
blackThemeColorUp = '#9eff15'
blackThemeColorDown = '#ff1717'
blackThemeBG = '#07000d'
spinesColor = "#5998ff"
epsBarColor = '#5a6de3'
MA1 = 0
MA2 = 0

def expMovingAverage(values, window):
    weights = np.exp(np.linspace(-1., 0., window))
    weights /= weights.sum()
    a = np.convolve(values, weights, mode='full')[:len(values)]
    a[:window] = a[window]
    return a

"""
def movingAverage(values,window):
    weights = np.repeat(1.0, window)/window    
    smas = np.convolve(values, weights, 'valid')
    return smas
"""

def movingAverage(value, period):
    return pd.rolling_mean(value, period)
    
def setAllSpineColor(ax, spineColor):
    ax.spines['bottom'].set_color(spineColor)
    ax.spines['top'].set_color(spineColor)
    ax.spines['left'].set_color(spineColor)
    ax.spines['right'].set_color(spineColor)

def sliceEntries(dateNifty, closepNifty, maxDate):
    print 'entries in stocks: ', maxDate
    startDate = len(dateNifty) - maxDate
    newdate = mdates.num2date(dateNifty[0])
    newdate = format(newdate.strftime('%Y-%m-%d'))
    print 'first', newdate            
    print 'before slicing len(dateNifty)',len(dateNifty)
    # slice nifty data to avoid unwanted entries in x axis
    dateNifty = dateNifty[startDate:]            
    closepNifty = closepNifty[startDate:]            
    print 'after slicing len(dateNifty)',len(dateNifty)

def sliceEntriesXY(data, start, length):
    return data[start:length]
    
def num2date(tmpDate):
    newDate = mdates.num2date(tmpDate)
    newDate = format(newDate.strftime('%Y-%m-%d'))
    return newDate
    
def plotNiftyOverlay(mainChart):
    try:     
        niftyFile = 'data/nsei.txt'
        dateNifty, openpNifty, highpNifty, lowpNifty, closepNifty, volumeNifty, adjclosep = np.loadtxt(niftyFile,delimiter=',',unpack=True,
                                                                  converters={0: mdates.strpdate2num('%Y-%m-%d')})            
        mainChartNifty = mainChart.twinx()
        mainChartNifty.plot(dateNifty, closepNifty, 'w', label='NIFTY')
        mainChartNifty.yaxis.label.set_color("w")
        setAllSpineColor(mainChartNifty, spinesColor)
        mainChartNifty.tick_params(axis='y', colors='w')
        plt.legend(loc=4, prop={'size':7}, fancybox=True)
        plt.ylabel('NIFTY')        
        maLeg = plt.legend(loc=4, ncol=1, prop={'size':7}, fancybox=True, borderaxespad=0.)
        maLeg.get_frame().set_alpha(0.4)
    except Exception, e:
        print 'failed in plotNiftyOverlay', str(e)    
    
def plotVolume(mainChart, date, volume):
    try: 
        print 'Drawing volume chart...'
        volumeChart = plt.subplot2grid((7,4), (6,0), sharex=mainChart, rowspan=1, colspan=4, axisbg=blackThemeBG)
        volumeChart.bar(date, volume, color='yellow')
        """
        comment out below if you want to see volume values
        """
        volumeChart.axes.yaxis.set_ticklabels([])
        volumeMA = 30
        skipMA = False
        if volumeMA > len(date):
            skipMA = True
        if skipMA == False:
            volumeMAData = movingAverage(volume, volumeMA)
            volumeSP = len(date[volumeMA-1:])
            date1 = sorted(date)
            volumeMAData = sorted(volumeMAData)            
            volumeChart.plot(date1[-volumeSP:], volumeMAData[-volumeSP:], 'w', label='volumeMA(30)')            
        volumeChart.grid(True, color='w')
        setAllSpineColor(volumeChart, spinesColor)
        volumeChart.tick_params(axis='x', colors='w')
        volumeChart.tick_params(axis='y', colors='w')
        plt.ylabel('Volume', color='w')
        plt.legend(loc=4, prop={'size':7}, fancybox=True)
        if skipMA == True:
            maLeg = plt.legend(loc=3, ncol=1, prop={'size':7}, fancybox=True, borderaxespad=0.)
            #FIXME: enabling below causes error
            #maLeg.get_frame().set_alpha(0.4)            
        for label in volumeChart.xaxis.get_ticklabels():
                label.set_rotation(45)
        print 'Drawing volume chart... Done'
    except Exception, e:
        print 'failed in plotVolume', str(e)
    
def fetchYahooData(stock, m1, d1, y1, m2, d2, y2):
    print("Fetching %s data from yahoo finance: %2d:%2d:%s till %2d:%2d:%s" % (stock, int(d1), int(m1)+1, y1, int(d2), int(m2)+1, y2))
    link = 'http://real-chart.finance.yahoo.com/table.csv?s='+stock+'&a='+m1+'&b='+d1+'&c='+y1+'&d='+m2+'&e='+d2+'&f='+y2+'&g=d&ignore=.csv'
    source = urlopen(link).read()
    splitSource = source.split('\n')
    
    if stock == '%5ENSEI':
        textFile = open("data/nsei.txt", "w")
    else:
        fileToOpen = 'data/'+stock+'.txt'
        textFile = open(fileToOpen, "w")

    for idx, eachLine in enumerate(splitSource):
        if idx==0:
            print 'ignoring ', eachLine
            continue
        else:
            linetoWrite = eachLine+'\n'
            textFile.write(linetoWrite)        
    textFile.close()    
            
def graphData(stock, plotStock, dataDict):
    try:
        stockFile = 'data/'+stock+'.txt'                
        date, openp, highp, lowp, closep, volume, adjclose = np.loadtxt(stockFile,delimiter=',',unpack=True,
                                                              converters={0: mdates.strpdate2num('%Y-%m-%d')})
        niftyFile = 'data/nsei.txt'
        dateNifty, openpNifty, highpNifty, lowpNifty, closepNifty, volumeNifty, adjclosep = np.loadtxt(niftyFile,delimiter=',',unpack=True,
                                                                  converters={0: mdates.strpdate2num('%Y-%m-%d')})
        date = np.flipud(date)
        openp = np.flipud(openp)
        highp = np.flipud(highp)
        lowp = np.flipud(lowp)
        closep = np.flipud(closep)
        volume = np.flipud(volume)
        dateNifty = np.flipud(dateNifty)
        closepNifty = np.flipud(closepNifty)

        print 'Drawing main chart...'        
        x = 0
        numOfDates = len(date)
        print "no of Dates: ", numOfDates
        numOfDatesNifty = len(dateNifty)
        print "no of Dates in Nifty: ", numOfDatesNifty
        candleArray = []
        otherDataList = np.repeat(0.0, numOfDates)
        print "len of candleArray", len(candleArray)

        while x < numOfDatesNifty:
            if plotStock == False:
                # create otherDataList for FII
                key = num2date(date[x])
                try:
                    otherDataList[x] = dataDict[key]
                except Exception, e:
                    #suppress this message if we are ploting stock because EPS date is very limited
                    if plotStock == False:
                        print 'No FII data for date: ' , str(e)
                        otherDataList[x] = 0
            else:
                #in most of the cases, reduntant data is present in stocks from yahoo. Delete stock data not present
                #in nifty
                if date[x] != dateNifty[x]:
                    print num2date(date[x]), num2date(dateNifty[x])
                    date = np.delete(date, x)
                    openp = np.delete(openp, x)
                    highp = np.delete(highp, x)
                    lowp = np.delete(lowp, x)
                    closep = np.delete(closep, x)
                    volume = np.delete(volume, x)
                    otherDataList = np.delete(otherDataList, x)
                    continue
                else:
                    otherDataList[x] = closep[x]/closepNifty[x]*100
            #create candlArray in expected order for candlestic_ochl
            #maintain the below order of variables
            appendLine = date[x],openp[x],closep[x],highp[x],lowp[x]
            candleArray.append(appendLine)
            x+=1

        print "len of candleArray", len(candleArray)
        print 'len of otherdata', len(otherDataList)
        #print candleArray
        global MA1
        global MA2
        
        if len(date) > MA2:
            draw_MA = 1
            label1 = str(MA1)+' SMA'
            label2 = str(MA2)+' SMA'
        else:
            #skip MA ploting if no of candles are less than the bigger MA
            draw_MA = 0
            print 'skip MA'
           
        if draw_MA==1:
            Av1 = movingAverage(closep, MA1)
            Av2 = movingAverage(closep, MA2)
            
        fig = plt.figure(facecolor=blackThemeBG)
        mainChart = plt.subplot2grid((7,4), (0,0), rowspan=5, colspan=4, axisbg=blackThemeBG)
        candlestick_ochl(mainChart, candleArray, width=.75, colorup=blackThemeColorUp, colordown=blackThemeColorDown)
         
        if draw_MA==1:                     
            mainChart.plot(date[MA1:], Av1[MA1:], fastMA, label=label1, linewidth=1.5)  
            mainChart.plot(date[MA2:], Av2[MA2:], slowMA, label=label2, linewidth=1.5)
 
        mainChart.grid(True, color='w')
        mainChart.xaxis.set_major_locator(mticker.MaxNLocator(10))
        mainChart.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        mainChart.yaxis.label.set_color("w")
        setAllSpineColor(mainChart, spinesColor)
        mainChart.tick_params(axis='y', colors='w')
        plt.ylabel('Stock Price')

        if draw_MA==1:
            plt.legend(loc=3, prop={'size':7}, fancybox=True)
            maLeg = plt.legend(loc=3, ncol=1, prop={'size':7}, fancybox=True, borderaxespad=0.)
            maLeg.get_frame().set_alpha(0.4)
        
        if plotStock == 1:
            plotNiftyOverlay(mainChart)

        print 'Drawing main chart... Done'
        if plotStock == 1:
            plotVolume(mainChart, date, volume)        
        
        print 'Drawing EPS/FII chart...'
        if plotStock == True:
            epsChart= plt.subplot2grid((7,4), (5,0), sharex=mainChart, rowspan=1, colspan=4, axisbg=blackThemeBG)
            epsChart.xaxis.set_visible(False)
        else:
            epsChart= plt.subplot2grid((7,4), (5,0), sharex=mainChart, rowspan=2, colspan=4, axisbg=blackThemeBG)
            epsChart.xaxis.set_visible(True)

        setAllSpineColor(epsChart, spinesColor)
        epsChart.tick_params(axis='y', colors='w')
        epsChart.tick_params(axis='x', colors='w')
        epsChart.yaxis.label.set_color("w")        
        epsChart.grid(True, color='w')
        
        if plotStock == True:
            plt.ylabel('Relative Strength')
        else:
            plt.ylabel('FII Data')
            epsChart.bar(date, otherDataList, color=epsBarColor, linewidth=0)
        
        #enable if you want lable pad to move further
        #epsChart.yaxis.labelpad = 20

        if plotStock == True:
            RS_MA = 200
            RS_AV = movingAverage(otherDataList, RS_MA)
            TypeMansfield = True

            """
            MRP = (( RP(today) / sma(RP(today), n)) - 1 ) * 100
            Full details can be found in below link,
            http://www.trade2win.com/boards/technical-analysis/134944-stan-weinsteins-stage-analysis-97.html#post2137398
            """
            MansfieldRPI = np.repeat(0.0, numOfDatesNifty)
            x = 0
            while x < numOfDatesNifty:
                MansfieldRPI[x] = (otherDataList[x]/RS_AV[x] - 1)*100
                x +=1

            if TypeMansfield == True:
                epsChart.plot(date[RS_MA:], MansfieldRPI[RS_MA:], "#FFFF00", linewidth=1.5)
                #Draw a horizontal line --- on 0
                epsChart.plot([min(date),max(date)], [0, 0], '--', color='w')
            else:
                epsChart.plot(date, otherDataList, '#b93904', linewidth=1.5)
                epsChart.plot(date[RS_MA:], RS_AV[RS_MA:], slowMA, linewidth=1.5)

        epsChart.tick_params(axis='x', colors='w')
        epsChart.tick_params(axis='y', colors='w')
        print 'Drawing EPS chart.. Done'
            
        for label in mainChart.xaxis.get_ticklabels():
            label.set_rotation(90)
        
        if plotStock == 0:
            for label in epsChart.xaxis.get_ticklabels():
                label.set_rotation(45)
                    
        plt.xlabel('Date', color='w')
        plt.suptitle(stock+' Stock Price', color='w')        
        plt.setp(mainChart.get_xticklabels(), visible=False)
        plt.subplots_adjust(left=.09, bottom=.18, right=.94, top=.94, wspace=.20, hspace=0)
        plt.show()            
        fig.savefig('example.png', facecolor=fig.get_facecolor())
        matplotlib.rcParams.update({'savefig.facecolor':fig.get_facecolor()})
        
    except Exception, e:
        print 'failed in graphData loop', str(e)

from Tkinter import Tk, Label, Button, Entry

class readInputDates:
    def __init__(self, master):
        self.master = master
        master.title("Enter Date Range:")

        self.label_month = Label(master, text="Month")
        self.label_date = Label(master, text="Date")
        self.label_year = Label(master, text="Year")
        self.label_startDate = Label(master, text="Start Date:")
        self.label_endDate = Label(master, text="End Date:")
        self.label_stock = Label(master, text="Stock:")
        self.label_slowMA = Label(master, text="Slow MA:")
        self.label_fastMA = Label(master, text="Fast MA:")
        self.entry_stock = Entry(master)
        vcmd = master.register(self.validate)
        self.entry_d1 = Entry(master, validate="key", validatecommand=(vcmd, '%P', 'd1'), text = 1)        
        self.entry_d2 = Entry(master, validate="key", validatecommand=(vcmd, '%P', 'd2'))
        self.entry_m1 = Entry(master, validate="key", validatecommand=(vcmd, '%P', 'm1'))
        self.entry_m2 = Entry(master, validate="key", validatecommand=(vcmd, '%P', 'm2'))
        self.entry_y1 = Entry(master, validate="key", validatecommand=(vcmd, '%P', 'y1'))
        self.entry_y2 = Entry(master, validate="key", validatecommand=(vcmd, '%P', 'y2'))
        self.entry_slowMA = Entry(master, validate="key", validatecommand=(vcmd, '%P', 'slowMA'))
        self.entry_fastMA = Entry(master, validate="key", validatecommand=(vcmd, '%P', 'fastMA'))
        self.plot_button = Button(master, text="Plot", command=lambda: self.plot())
        
        # Layout
        self.label_stock.grid(row=1, column=1)
        self.entry_stock.grid(row=1, column=2)
        self.label_month.grid(row=2, column=2)
        self.label_date.grid(row=2, column=3)
        self.label_year.grid(row=2, column=4)
        self.label_endDate.grid(row=4, column=1)        
        self.label_startDate.grid(row=3, column=1)        
        self.plot_button.grid(row=1, column=4)        
        self.entry_m1.grid(row=3, column=2)
        self.entry_m2.grid(row=4, column=2)        
        self.entry_d1.grid(row=3, column=3)
        self.entry_d2.grid(row=4, column=3)        
        self.entry_y1.grid(row=3, column=4)
        self.entry_y2.grid(row=4, column=4)
        self.label_slowMA.grid(row=5, column=1)
        self.entry_slowMA.grid(row=5, column=2)
        self.label_fastMA.grid(row=5, column=3)
        self.entry_fastMA.grid(row=5, column=4)
        
        # set some default values
        self.entry_stock.insert(0, 'ASHOKLEY.NS')
        self.entry_d1.insert(0, 20)
        self.entry_m1.insert(0, 5)
        self.entry_y1.insert(0, 2013)
        self.entry_d2.insert(0, 19)
        self.entry_m2.insert(0, 6)
        self.entry_y2.insert(0, 2016)
        self.entry_slowMA.insert(0, 30)
        self.entry_fastMA.insert(0, 150)

    def validate(self, new_text, entry):        
        if not new_text: # the field is being cleared
            if entry == 'd1':
                self.entry_d1 = 0
            elif entry == 'd2':            
                self.entry_d2 = 0
            elif entry == 'm1':
                self.entry_m1 = 0
            elif entry == 'm2':
                self.entry_m2 = 0
            elif entry == 'y1':
                self.entry_y1 = 0
            elif entry == 'y2':
                self.entry_y2 = 0
            elif entry == 'slowMA':
                self.entry_slowMA = 0
            elif entry == 'fastMA':
                self.entry_fastMA = 0
            return True
        try:            
            if entry == 'd1':
                self.entry_d1 = int(new_text)
            elif entry == 'd2':            
                self.entry_d2 = int(new_text)
            elif entry == 'm1':
                self.entry_m1 = int(new_text)
                #substrace month -1. thats how they formated in yahoo api data
                self.entry_m1 -= 1
            elif entry == 'm2':
                self.entry_m2 = int(new_text)
                #substrace month -1. thats how they formated in yahoo api data
                self.entry_m2 -= 1
            elif entry == 'y1':
                self.entry_y1 = int(new_text)
            elif entry == 'y2':
                self.entry_y2 = int(new_text)
            elif entry == 'slowMA':
                self.entry_slowMA = int(new_text)
            elif entry == 'fastMA':
                self.entry_fastMA = int(new_text)
            return True
        except ValueError:
            return False
    def plot(self):
        global MA1, MA2
        
        MA1 = self.entry_slowMA
        MA2 = self.entry_fastMA
        EPSDataDict = {'2016-01-04': 47,'2015-10-01':32, '2015-07-01':27, '2015-04-01':26 }
        
        #stock = '%5ENSEI'
        is_index = 0
        stock = self.entry_stock.get()
        if stock == 'NIFTY':
            is_index=1
        
        print 'is_index ', is_index
        if is_index ==1:     
            dataDict = pickle.load(open("data/FIIDATA.txt", "r"))
        print self.entry_d1, self.entry_d2, self.entry_m1, self.entry_m2, self.entry_y1, self.entry_y2     
        
        d1 = str(self.entry_d1)
        m1 = str(self.entry_m1)
        y1 = str(self.entry_y1)
        
        d2 = str(self.entry_d2)
        m2 = str(self.entry_m2)
        y2 = str(self.entry_y2)
        
        if is_index == 0:
            fetchYahooData(stock, m1, d1, y1, m2, d2, y2)
        #fetch Nifty data in both cases
        fetchYahooData('%5ENSEI', m1, d1, y1, m2, d2, y2)

        if is_index == 1:
            graphData('nsei', False, dataDict)
        else:
            graphData(stock, True, EPSDataDict)

"""
User called function defined below
"""
def plotNifty():
    root = Tk()
    my_gui = readInputDates(root)        
    root.mainloop()

def plotStock(stock):
    EPSdateList = ['2016-01-04', '2015-10-01', '2015-07-01', '2015-04-01']
    EPSdataList = [47, 32, 27, 26] 
    graphData(stock, 0, EPSdataList, EPSdateList)

def pullData(stock, duration):
    try:
        print 'Currently pulling ', stock
        print str(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
        
        fileLine = 'data/'+stock+'.txt'
        urlToVisit = 'http://chartapi.finance.yahoo.com/instrument/1.0/'+stock+'/chartdata;type=quote;range='+duration+'/csv'
        try:
            sourceCode = urllib2.urlopen(urlToVisit).read()
        except Exception,e:
            print 'opening failed.. retry once', str(e)
            sourceCode = urllib2.urlopen(urlToVisit).read()
        splitSource = sourceCode.split('\n')
        
        saveFile = open(fileLine, 'w')
        for eachLine in splitSource:
            splitLine = eachLine.split(',')
            if len(splitLine)==6:
                if 'values' not in eachLine:                    
                    lineToWrite = eachLine+'\n'
                    saveFile.write(lineToWrite)
                else:
                    print eachLine
            else:
                print splitLine
        saveFile.close()
        print 'Pulled',stock
        print 'sleeping'
        #time.sleep(5)
        
    except Exception,e:
        print 'main loop', str(e)        

    
def pullFIIData():
    try:
        startYear = 2007
        endYear = 2016
        endMonth = 1
        monthLinkList = []
        
        """ create list of months like sel_month=200811 """
        startY = startYear
        startM = 1
        
        while 1:
            if startY == endYear and startM == endMonth+1:
                break
            
            monthLinkList.append(str(startY)+"%02d" % startM)
            startM += 1
            if startM == 13:
                startM = 1
                startY += 1
        
        print monthLinkList        
        #pickle.dump(monthLinkList, open("monthLinkList.txt", "w"))
        
        data = []
        date = []
        fiiData = {}
        
        for eachMonth in monthLinkList:
            print 'fecthing data for month', eachMonth
            fiiDataLink = 'http://www.moneycontrol.com/stocks/marketstats/fii_dii_activity/index.php?sel_month='+str(eachMonth)
            source = urlopen(fiiDataLink).read()
            
            string = '<table width="100%" border="0" cellspacing="0" cellpadding="0" class="tblfund2">'
            arr =  source.split(string)
            length = len(arr)
            print length
            
            for idx, item in enumerate(arr):
                if idx ==0 or idx == length-1:#skip 0th and last item               
                    print 'continue',idx
                    continue
                tmpDate =  item.split('">')[1].split('</td>')[0]            
                tmpDate = time.strptime(tmpDate, "%d-%b-%Y")                        
                tmpDate = time.strftime('%Y-%m-%d', tmpDate)
                fiiActivity = item.split('</td>')[3].split('">')[1]
                #print date, tmpDate, fiiActivity
                print tmpDate
                date.append(tmpDate)
                data.append(fiiActivity.replace(',',''))
                fiiData.update({tmpDate:fiiActivity.replace(',','')})
            time.sleep(1)
                
        print date
        print data
        pickle.dump(date, open("data/FII_date.txt", "w"))
        pickle.dump(data, open("data/FII_data.txt", "w")) 
        pickle.dump(fiiData, open("data/FIIDATA.txt", "w"))
            
    except Exception, e:
        print 'pullFIIData', str(e)
def test():
    dateList = pickle.load(open("data/FIIDATA.txt", "r"))
    print dateList
    for key in sorted(dateList, reverse=True):
        print key,dateList[key]
#pullData(stockToPull)
#plotStock('BAJFINANCE.NS')
plotNifty()