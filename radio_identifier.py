"""
TODO: scan the radio. Use machine learning to identify FM stations.
The UI will use get_radio_list() to get the list of FM stations frequencies.
"""
import os
import subprocess
import numpy as np
import pandas as pd
from sklearn.externals import joblib
from sklearn.neighbors import KNeighborsClassifier

#notes: to execute command in python, use subprocess(arg)
#for example, if you want to run "-rtl_power -f 87M:108M:1k -g 20 -i 10 -e 1m logfile.csv", use this:
#subprocess.run(["rtl_power", "-f", "87M:108M:1k", "-g", "20", "-i", "10", "-e", "1m", "logfile.csv"])
#After that, you can read logfile.csv and perform identification.
#finally, to remove the logfile.csv, call
#os.remove("logfile.csv")

def conv_func(df):
    x=[] # Stores all the frequencies
    y=[] # Stores corresponding power value
    
    for j in range(0,len(df)):
        for i in range(6,4103):
            y.append(float(df[i][j]))
            r = (df[3][j]-df[2][j])/4096
            temp = df[3][j]+(r*(i-6))
            x.append(temp)
    df = pd.DataFrame({"Frequency":x,"Power":y})
    return df

def get_radio_list(min, max):
    """
    Scan the radio frequency and return a list of frequency of
    fm stations.
    min: min frequency from user
    max: max frequency from user
    """
    subprocess.run(["rtl_power", "-f", min, "M:", max, "M:1k", "-g", "20", "-i", "10", "-e", "1m", "logfile.csv"])
    dfs = pd.read_csv("logfile.csv", header=None)
    knn = joblib.load('findingFMstations_trainedmodel.pkl') 
    dfs = conv_func(dfs)
    y_predict = knn.predict(dfs)
    l=[]
    for i in range(0,len(y_predict)):
        check = int(round(dfs["Frequency"][i]))
        check = int(round(check/100000))
        check = float(check/10)
        if(y_predict[i]==1):
            if(not check in l):
                l.append(check)
    #BAFMRS = {87.9: 'KSFH', 88.1: ['KAWZ', 'KSRH', 'KECG'], 88.5: 'KQED', 89.1: 'KCEA', 89.3: ['KPFB', 'KOHL', 'KMTG'], 89.5: 'KPOO', 89.7: 'KFJC', 89.9: 'KCRH', 90.1: 'KZSU', 90.3: 'KOSC', 90.5: 'KSJS', 90.7: 'KALX', 91.1: 'KCSM', 91.5: 'KKUP', 91.7: 'KALW', 92.1: 'KKDV', 92.3: 'KSJO', 92.7: 'KREV', 93.3: 'KRZZ', 94.1: 'KPFA', 94.5: 'KBAY', 94.9: 'KYLD', 95.3: 'KRTY', 95.7: 'KGMZ', 96.1: 'KSQQ', 96.5: 'KOIT', 97.3: 'KLLC', 98.1: 'KISQ', 98.5: 'KUFX', 98.9: 'KSOL', 99.7: 'KMVQ', 100.3: 'KBRG', 101.3: 'KIOI', 101.7: 'KKIQ', 102.1: 'KRBQ', 102.9: 'KBLX', 103.3: 'KSCU', 103.7: 'KOSF', 104.5: 'KFOG', 104.9: 'KXSC', 105.3: 'KITS', 105.7: 'KVVF', 106.1: 'KMEL', 106.5: 'KEZR', 106.9: 'KFRC', 107.7: 'KSAN'}
    os.remove("logfile.csv")
    #return list(BAFMRS.keys())
    return l
