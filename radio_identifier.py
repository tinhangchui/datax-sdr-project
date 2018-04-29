"""
TODO: scan the radio. Use machine learning to identify FM stations.
The UI will use get_radio_list() to get the list of FM stations frequencies.
"""
import os
import subprocess
import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.externals import joblib

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

def conversion_function(df):    
    x=[] # Stores all the frequencies
    y=[] # Stores corresponding power value
    z=[] # Stores is_FM, if 1 then yes, if 0 then no

    # following array contains all BAY AREA FM STATIONS
    arr = [87.9, 88.1, 88.5, 89.1, 89.3, 89.5, 89.7, 89.9, 90.1, 90.3, 90.5, 90.7, 91.1, 91.5, 91.7, 92.1, 92.3, 92.7, 93.3, 94.1, 94.5, 94.9, 95.3, 95.7, 96.1, 96.5, 97.3, 98.1, 98.5, 98.9, 99.7, 100.3, 101.3, 101.7, 102.1, 102.9, 103.3, 103.7, 104.5, 104.9, 105.3, 105.7, 106.1, 106.5, 106.9, 107.7]

    #following code makes 3 lists, x-> freq,y-> power, z-> Is_FM?
    for j in range(0,len(df)):
        for i in range(6,4103):
            y.append(float(df[i][j]))
            r = (df[3][j]-df[2][j])/4096
            temp = df[3][j]+(r*(i-6))
            x.append(temp)
            check = round(temp/100000)
            check = int(check)
            check = float(check/10)
            n=0
            if(check in arr):
                n=1
            z.append(int(n))
    df = pd.DataFrame({"Frequency":x,"Power":y,"Is_FM":z})
    return df

## TO CREATE findingFMstations_trainedmodel.pkl, USE CODE BELOW
#dfs = pd.read_csv("logfile.csv", header=None)
#dfs = conversion_function(dfs)
#X = dfs.drop('Is_FM', axis=1)
#y = dfs['Is_FM']
#knn = KNeighborsClassifier(n_neighbors = 3)
#knn.fit(X, y)
#joblib.dump(knn, 'findingFMstations_trainedmodel.pkl')

def get_radio_list(min, max):
    """
    Scan the radio frequency and return a list of frequency of
    fm stations.
    min: min frequency from user
    max: max frequency from user
    """
    subprocess.run(["rtl_power", "-f", str(min)+"M:"+str(max)+"M:1k", "-g", "20", "-i", "10", "-e", "1m", "logfile.csv"])
    dfs = pd.read_csv("logfile.csv", header=None)
    knn = joblib.load('findingFMstations_trainedmodel.pkl')
    dfs = conv_func(dfs)
    y_predict3 = knn.predict(dfs)
    l3=[]
    for i in range(0,len(y_predict3)):
        num = round(dfs["Frequency"][i]/100000)
        num = int(num)
        num = float(num/10)
        if(y_predict3[i]==1):
            if(not num in l3):
                l3.append(num)
    #BAFMRS = {87.9: 'KSFH', 88.1: ['KAWZ', 'KSRH', 'KECG'], 88.5: 'KQED', 89.1: 'KCEA', 89.3: ['KPFB', 'KOHL', 'KMTG'], 89.5: 'KPOO', 89.7: 'KFJC', 89.9: 'KCRH', 90.1: 'KZSU', 90.3: 'KOSC', 90.5: 'KSJS', 90.7: 'KALX', 91.1: 'KCSM', 91.5: 'KKUP', 91.7: 'KALW', 92.1: 'KKDV', 92.3: 'KSJO', 92.7: 'KREV', 93.3: 'KRZZ', 94.1: 'KPFA', 94.5: 'KBAY', 94.9: 'KYLD', 95.3: 'KRTY', 95.7: 'KGMZ', 96.1: 'KSQQ', 96.5: 'KOIT', 97.3: 'KLLC', 98.1: 'KISQ', 98.5: 'KUFX', 98.9: 'KSOL', 99.7: 'KMVQ', 100.3: 'KBRG', 101.3: 'KIOI', 101.7: 'KKIQ', 102.1: 'KRBQ', 102.9: 'KBLX', 103.3: 'KSCU', 103.7: 'KOSF', 104.5: 'KFOG', 104.9: 'KXSC', 105.3: 'KITS', 105.7: 'KVVF', 106.1: 'KMEL', 106.5: 'KEZR', 106.9: 'KFRC', 107.7: 'KSAN'}
    os.remove("logfile.csv")
    #return list(BAFMRS.keys())
    return l3
