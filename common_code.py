import time

def mySleep(t):
#    print("sleeping %d seconds" % t)
    print("")
#    time.sleep(t)

"""
continue DB update from here
"""
update_start_index = 0
"""
Enter the lable show in BS website for latest quater
"""
current_qtr = 'Dec-2016'
previous_qtr = 'Sep-2016'

"""
Sqlite File name
"""
sqliteFile = 'stock_db.sqlite'

"""
BS data base json file name
"""
BS_json_file = 'data_BS.json'

"""
Google Screener json file name
"""
google_json_file = 'NIFTYAllStocks.txt'
#google_json_file = 'EPS5yearGreaterThanZeroNSE.txt'

"""
Use website to pick data. If false only DB data is used.
"""
use_web = False

BS_BlacklistStocks = [u'3RDROCK', u'ALSTOMTx26D', u'APOLSINHOT', u'AXISGOLD', u'AYMSYNTEX', u'ADANITRANS', u'ABCIL', u'ABFRL', u'SMAHIMSA', u'ALFALAVAL', u'ALKEM', u'BDR', u'BANKBEES', u'SHARIABEES', u'BHALCHANDR', u'BSLGOLDETF', u'BSLNIFTY', u'BELLCERATL', u'CRMFGETF', u'CAPCO', u'CMC', u'CMMINFRA', u'DEFTY', u'CAROLINFO', u'CASTROL', u'CHEMPLAST', u'CHESLINTEX', u'CHETTINAD', u'COXx26KINGS', u'DTIL', u'DENSO', u'LALPATHLAB', u'EBANK', u'NIFTYEES', u'ELITE', u'EONELECT', u'SMEMKAYTOOLS', u'ESSAROIL', u'FROGCELL', u'FRLDVR', u'FAME', u'SMFOURTHDIM', u'FTCPOF5YGR', u'FTCPOF5YDV', u'FTCSF5YGRO', u'FTCSF5YDIV', u'FKONCO', u'GENUSPAPER', u'GIRRESORTS', u'GOLDBEES', u'HNGSNGBEES', u'INFRABEES', u'LIQUIDBEES', u'CPSEETF', u'PSUBNKBEES', u'GUJGASLTD', u'GUJNREDVR', u'GRABALALK', u'GREENLAM', u'GUJRATGAS', u'HDFCMFGETF', u'HDFCNIFETF', u'HECINFRA', u'HUSYS', u'HIRAFERRO', u'HYDROSx26S', u'IGOLD', u'ICNX100', u'ISENSEX', u'INIFTY', u'IDBIGOLD', u'IDFCBANK', u'ILx26FSTRANS', u'IIFLNIFTY', u'INDIAVIX', u'INFOBEANS', u'INGVYSYABK', u'IVRCLAH', u'ILx26FSENGG', u'INDIABULLS', u'INTELLECT', u'INDIGO', u'JISLDVREQS', u'JSWISPAT', u'P1JSWSTEEL', u'Jx26KBANK', u'JEYPORE', u'JSLHISAR', u'KAWIRES', u'KNDENGTECH', u'KOTAKGOLD', u'KOTAKNIFTY', u'KOTAKPSUBK', u'KOTAKBKETF', u'KOTAKNV20', u'KAYA', u'KINETICMOT', u'KBIL', u'Lx26TFH', u'LICNETFN50', u'LICNETFSEN', u'LICNETFGSC', u'LUXIND', u'MRO', u'MCSL', u'MANAKALUCO', u'MANAKCOAT', u'MANAKSTEEL', u'MMNL', u'SMMITCON', u'MOHINI', u'M100', u'N100', u'M50', u'MGOLD', u'Mx26MFIN', u'Mx26M', u'MAHINDUGIN', u'MAJESCO', u'MANJUSHREE', u'MAKE', u'SMMOMAI', u'MORARJETEX', u'NEO', u'CNX100', u'NIFTY', u'CNX500', u'BANKNIFTY', u'NIFTYBEES', u'CNXENERGY', u'CNXFMCG', u'CNXINFRA', u'CNXIT', u'JUNIORBEES', u'CNXMIDCAP', u'NIFTYMIDCAP50', u'CNXMNC', u'NIFTYJR', u'CNXPHARMA', u'CNXPSE', u'CNXPSUBANK', u'CNXREALTY', u'CNXSERVICE', u'NIFTYDIVIDEND', u'NIFTYPR1XINV', u'NIFTYPR2XLEV', u'NIFTYTR1XINV', u'NIFTYTR2XLEV', u'NV20', u'NIRVIKARA', u'QVC', u'NAGARFERT', u'NOVOPANIND', u'SMOPAL', u'OCCL', u'PNEUMATIC', u'PALRED', u'PANASONIC', u'PENPEBS', u'SMPERFECT', u'PIRGLASS', u'POWERMECH', u'PRABHAT', u'PRECAM', u'QGOLDHALF', u'QNIFTY', u'QUICKHEAL', u'RATNAINFRA', u'RELNV20', u'RELBANK', u'RELGOLD', u'RELNIFTY', u'RELCONS', u'RELDIVOPP', u'RELCNX100', u'RELIGAREGO', u'RELGRNIFTY', u'RANBAXY', u'RANKLIN', u'RBN', u'RELMEDIA', u'SHK', u'UTISUNDER', u'Sx26SPOWER', u'SATIN', u'SETFGOLD', u'SETFNIF50', u'SETFNIFBK', u'SETFNN50', u'SBx26TINTL', u'SMSHAIVAL', u'SHYAMCENT', u'SMZSCHEM', u'SURAJCROP', u'SABERORGAN', u'SADBHIN', u'SMSANCO', u'SATYAMCOMP', u'SHASUNPHAR', u'SHREEPUSHK', u'SIMBHSUGAR', u'SOUNDCRAFT', u'DRSTAN', u'STER', u'SMSIIL', u'SURANATx26P', u'TATAMTRDVR', u'TAKSHEEL', u'TEAMLEASE', u'ANANDAMRUB', u'SMTHEJO', u'GOLDSHARE', u'UTINIFTETF', u'UTISENSETF', u'UTVSOF', u'VETO', u'WELENTRP', u'WELGLOB', u'WYETH', u'PATNI']
def is_stock_blacklisted(stock):
    return stock in BS_BlacklistStocks

dataBase_updated_stocks = 0
dataBase_outdate_stocks = 0
DB_updateRunning = 0

"""
index of variables in a row of SQL DB
"""
DBindex_symbol = 0
DBindex_EPS_Q1 = 1
DBindex_EPS_Q2 = 2
DBindex_EPS_Q3 = 3
DBindex_EPS_Q4 = 4
DBindex_EPS_Q1YoY = 5
DBindex_EPS_Q2YoY = 6
DBindex_EPS_Q3YoY = 7
DBindex_EPS_Q4YoY = 8
DBindex_Q1Name = 9
DBindex_Q2Name = 10
DBindex_Q3Name = 11
DBindex_Q4Name = 12
DBindex_EPSQ1Change = 13
DBindex_EPSQ2Change = 14
DBindex_EPSQ3Change = 15
DBindex_EPSQ4Change = 16
DBindex_Y1Name = 17
DBindex_Y2Name = 18
DBindex_Y3Name = 19
DBindex_Y4Name = 20
DBindex_EPS_Y1 = 21
DBindex_EPS_Y2 = 22
DBindex_EPS_Y3 = 23
DBindex_EPS_Y4 = 24
DBindex_EPSY1Change = 25
DBindex_EPSY2Change = 26
DBindex_EPSY3Change = 27
