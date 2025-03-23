from venv import create
import pyodbc
import pandas as pd
import time
import datetime
import os.path
conn = pyodbc.connect('Driver={SQL Server};Server=LAPTOP-C2QFIL9D;Database=Logs;Trusted_Connection=yes;')

cursor = conn.cursor()

result = ""
def response (log,a,b):
    cursor.execute('Select TaskA,TaskB, a.caseid FROM '+ log +' a , (SELECT a.[event] AS TaskA , b.[event] AS TaskB FROM '+ log+ ' a , '+ log+' b WHERE a.[event] = \''+a+'\' and a.[event] != b.[event] and b.[event] = \''+b+'\' GROUP BY a.[event] , b.[event]) x WHERE a.[event] = \''+a+'\' AND (EXISTS (SELECT * FROM '+log+' b WHERE b.[event] = \''+b+'\' and b.caseid = a.caseid and b.startTime < a.startTime) or Not EXISTS(SELECT * FROM '+log+' b  WHERE b.[event] = \''+b+'\' and b.caseid = a.caseid)) GROUP BY x.TaskA , x.TaskB, a.caseid')

    return cursor.fetchall()

def response_without (log,a,b):
    cursor.execute('Select TaskA,TaskB, a.caseid FROM '+ log +' a , (SELECT a.[event] AS TaskA , b.[event] AS TaskB FROM '+ log+ ' a , '+ log+' b WHERE a.[event] = \''+a+'\' and a.[event] != b.[event] and b.[event] = \''+b+'\' GROUP BY a.[event] , b.[event]) x WHERE a.[event] = \''+a+'\' AND (EXISTS (SELECT * FROM '+log+' b WHERE b.[event] = \''+b+'\' and b.caseid = a.caseid and b.position > a.position)) GROUP BY x.TaskA , x.TaskB, a.caseid')

    return cursor.fetchall()

def response_after (log,a,b,after):
    cursor.execute('Select TaskA,TaskB, a.caseid FROM '+ log +' a , (SELECT a.[event] AS TaskA , b.[event] AS TaskB FROM '+ log+ ' a , '+ log+' b WHERE a.[event] = \''+a+'\' and a.[event] != b.[event] and b.[event] = \''+b+'\' GROUP BY a.[event] , b.[event]) x WHERE a.[event] = \''+a+'\' AND (EXISTS (SELECT * FROM '+log+' b WHERE b.[event] = \''+b+'\' and b.caseid = a.caseid and b.startTime > a.startTime and ((b.sT - a.sT)/3600)*60 > ? ) or Not EXISTS(SELECT * FROM '+log+' b  WHERE b.[event] = \''+b+'\' and b.caseid = a.caseid)) GROUP BY x.TaskA , x.TaskB, a.caseid',after)

    return cursor.fetchall()

def response_within (log,a,b,within):
    cursor.execute('Select TaskA,TaskB, a.caseid FROM '+ log +' a , (SELECT a.[event] AS TaskA , b.[event] AS TaskB FROM '+ log+ ' a , '+ log+' b WHERE a.[event] = \''+a+'\' and a.[event] != b.[event] and b.[event] = \''+b+'\' GROUP BY a.[event] , b.[event]) x WHERE a.[event] = \''+a+'\' AND (EXISTS (SELECT * FROM '+log+' b WHERE b.[event] = \''+b+'\' and b.caseid = a.caseid and b.startTime > a.startTime and ((b.sT - a.sT)/3600)*60 < ?) or Not EXISTS(SELECT * FROM '+log+' b  WHERE b.[event] = \''+b+'\' and b.caseid = a.caseid)) GROUP BY x.TaskA , x.TaskB, a.caseid',within)

    return cursor.fetchall()


def precedence (log,a,b):
    cursor.execute('Select TaskA,TaskB, a.caseid FROM '+ log +' a , (SELECT a.[event] AS TaskA , b.[event] AS TaskB FROM '+ log+ ' a , '+ log+' b WHERE a.[event] = \''+a+'\' and a.[event] != b.[event] and b.[event] = \''+b+'\' GROUP BY a.[event] , b.[event]) x WHERE a.[event] = \''+b+'\' AND (EXISTS (SELECT * FROM '+log+' b WHERE b.[event] = \''+a+'\' and b.caseid = a.caseid and b.startTime > a.startTime) or Not EXISTS(SELECT * FROM '+log+' b  WHERE b.[event] = \''+a+'\' and b.caseid = a.caseid)) GROUP BY x.TaskA , x.TaskB, a.caseid')

    return cursor.fetchall()

def precedence_without (log,a,b):
    cursor.execute('Select TaskA,TaskB, a.caseid FROM '+ log +' a , (SELECT a.[event] AS TaskA , b.[event] AS TaskB FROM '+ log+
                   ' a , '+ log+' b WHERE a.[event] = \''+a+'\' and a.[event] != b.[event] and b.[event] = \''+b+'\' GROUP BY a.[event] , b.[event]) x WHERE a.[event] = \''+b+'\' AND (EXISTS (SELECT * FROM '+log+
                   ' b WHERE b.[event] = \''+a+'\' and b.caseid = a.caseid and a.position < b.position) ) GROUP BY x.TaskA , x.TaskB, a.caseid')

    return cursor.fetchall()


def precedence_before (log,a,b,before):
    cursor.execute('Select TaskA,TaskB, a.caseid FROM '+ log +' a , (SELECT a.[event] AS TaskA , b.[event] AS TaskB FROM '+ log+ ' a , '+ log+' b WHERE a.[event] = \''+a+'\' and a.[event] != b.[event] and b.[event] = \''+b+'\' GROUP BY a.[event] , b.[event]) x WHERE a.[event] = \''+b+'\' AND (EXISTS (SELECT * FROM '+log+' b WHERE b.[event] = \''+a+'\' and b.caseid = a.caseid and a.startTime > b.startTime and ((a.sT - b.sT)/3600)*60 > ? ) or Not EXISTS(SELECT * FROM '+log+' b  WHERE b.[event] = \''+a+'\' and b.caseid = a.caseid)) GROUP BY x.TaskA , x.TaskB, a.caseid',before)

    return cursor.fetchall()

def precedence_within (log,a,b,within):
    cursor.execute('Select TaskA,TaskB, a.caseid FROM '+ log +' a , (SELECT a.[event] AS TaskA , b.[event] AS TaskB FROM '+ log+ ' a , '+ log+' b WHERE a.[event] = \''+a+'\' and a.[event] != b.[event] and b.[event] = \''+b+'\' GROUP BY a.[event] , b.[event]) x WHERE a.[event] = \''+b+'\' AND (EXISTS (SELECT * FROM '+log+' b WHERE b.[event] = \''+a+'\' and b.caseid = a.caseid and a.startTime > b.startTime and ((a.sT - b.sT)/3600)*60 < ? ) or Not EXISTS(SELECT * FROM '+log+' b  WHERE b.[event] = \''+a+'\' and b.caseid = a.caseid)) GROUP BY x.TaskA , x.TaskB, a.caseid',within)

    return cursor.fetchall()

# Responded Existence
def RE_pattern (log,a,b):
    cursor.execute('Select TaskA,TaskB, a.caseid FROM '+ log +' a , (SELECT a.[event] AS TaskA , b.[event] AS TaskB '
                                                              'FROM '+ log +' a , '+ log +' b' 
					'WHERE a.[event] != b.[event] and a.event =\''+a+'\' and b.event =\''+b+' \''
                    'GROUP BY a.[event] , b.[event]) x'
                    'WHERE a.[event] = \''+a+'\' AND '
                    '(EXISTS (SELECT * FROM '+ log +' b  WHERE b.[event] = \''+b+'\' and b.caseid = a.caseid and a.position < b.position) )' 
                    'GROUP BY x.TaskA , x.TaskB, a.caseid')
    return cursor.fetchall()

#Anti Pattern of Responded Existence
def RE (log,a,b):
    cursor.execute('Select TaskA,TaskB, a.caseid FROM '+ log +' a , (SELECT a.[event] AS TaskA , b.[event] AS TaskB '
                                                              'FROM '+ log +' a , '+ log +' b ' 
					'WHERE a.[event] != b.[event] and a.event =\''+a+'\' and b.event =\''+b+' \' '
                    'GROUP BY a.[event] , b.[event]) x '
                    'WHERE a.[event] = \''+a+'\' AND '
                    '(Not EXISTS (SELECT * FROM '+ log +' b  WHERE b.[event] = \''+b+'\' and b.caseid = a.caseid and a.position < b.position) ) ' 
                    'GROUP BY x.TaskA , x.TaskB, a.caseid')
    return cursor.fetchall()

#Chain Precede
def CP_pattern (log,a,b):
    cursor.execute('Select TaskA,TaskB, a.caseid' 
    'FROM bpi1313 a , (SELECT a.[event] AS TaskA , b.[event] AS TaskB' 
					'FROM '+ log +' a , '+ log +' b'
					'WHERE a.[event] != b.[event] and a.event =\''+a+'\' and b.event =\''+b+' \''
					'GROUP BY a.[event] , b.[event]) x'
    'WHERE a.[event] = \''+b+' \' AND EXISTS (SELECT * FROM bpi1313 b'
				   'WHERE b.[event] = \''+a+'\' and b.caseid = a.caseid and a.position > b.position)'
				   'and Not Exists(SELECT * FROM '+ log +' b , '+ log +' c'
				   'WHERE b.[event] = \''+a+'\' and b.caseid = a.caseid and c.caseid = a.caseid and c.position < a.position and c.position > b.position)'
    'GROUP BY x.TaskA , x.TaskB, a.caseid')
    return cursor.fetchall()

#Anti pattern Chain Precede
def CP (log,a,b):
    cursor.execute('Select TaskA,TaskB, a.caseid '
                   'FROM bpi1313 a , (SELECT a.[event] AS TaskA , b.[event] AS TaskB ' 
					'FROM '+ log +' a , '+ log +' b '
					'WHERE a.[event] != b.[event] and a.event =\''+a+'\' and b.event =\''+b+' \' '
					'GROUP BY a.[event] , b.[event]) x '
    'WHERE a.[event] = \''+b+' \' AND EXISTS (SELECT * FROM bpi1313 b '
				   'WHERE b.[event] = \''+a+'\' and b.caseid = a.caseid and a.position > b.position) '
				   'and Exists(SELECT * FROM '+ log +' b , '+ log +' c '
				   'WHERE b.[event] = \''+a+'\' and b.caseid = a.caseid and c.caseid = a.caseid and c.position < a.position and c.position > b.position) '
    'GROUP BY x.TaskA , x.TaskB, a.caseid')
    return cursor.fetchall()

#Alternate Preced
def AP_pattern (log,a,b):
    cursor.execute('Select TaskA,TaskB, a.caseid' 
    'FROM bpi1313 a , (SELECT a.[event] AS TaskA , b.[event] AS TaskB' 
					'FROM '+ log +' a , '+ log +' b'
					'WHERE a.[event] != b.[event] and a.event =\''+a+'\' and b.event =\''+b+' \''
					'GROUP BY a.[event] , b.[event]) x'
    'WHERE a.[event] = \''+b+' \' AND EXISTS (SELECT * FROM bpi1313 b'
				   'WHERE b.[event] = \''+a+'\' and b.caseid = a.caseid and a.position > b.position)'
				   'and Not Exists(SELECT * FROM '+ log +' b , '+ log +' c'
				   'WHERE b.[event] = \''+a+'\' and c.[event] = \''+b+'\' and b.caseid = a.caseid and c.caseid = a.caseid and c.position < a.position and c.position > b.position)'
    'GROUP BY x.TaskA , x.TaskB, a.caseid')
    return cursor.fetchall()

#Anti Pattern
def AP (log,a,b):
    cursor.execute('Select TaskA,TaskB, a.caseid ' 
    'FROM bpi1313 a , (SELECT a.[event] AS TaskA , b.[event] AS TaskB ' 
					'FROM '+ log +' a , '+ log +' b '
					'WHERE a.[event] != b.[event] and a.event =\''+a+'\' and b.event =\''+b+' \' '
					'GROUP BY a.[event] , b.[event]) x '
    'WHERE a.[event] = \''+b+' \' AND EXISTS (SELECT * FROM bpi1313 b '
				   'WHERE b.[event] = \''+a+'\' and b.caseid = a.caseid and a.position > b.position) '
				   'and Exists(SELECT * FROM '+ log +' b , '+ log +' c '
				   'WHERE b.[event] = \''+a+'\' and c.[event] = \''+b+'\' and b.caseid = a.caseid and c.caseid = a.caseid and c.position < a.position and c.position > b.position) '
    'GROUP BY x.TaskA , x.TaskB, a.caseid')
    return cursor.fetchall()
# read from file
'''file_exists = os.path.isfile('SQLMinerResult_AntiPattern.csv')
val = input('Do you want to create a graph, Yes/NO')'''
cont=True
file_exists = os.path.isfile('Executiontime_sqlminer_antipatterns.csv')
openfile = input('File name.txt: ')
db = input("dbname : ")
while cont:
    with open(str(openfile), "r") as file:
        # val = input("Maxp-ep or Maxp or Minp-ep or Minp or Max-ep or Max or Min-ep or Min or Res-without or Prec-without")
        val = input("1-Chain Preced , 2- Responded Existence , 3- Alternate Precede")

        for line in file:
            x = []
            y = []
            z = []
            m = []
            type = ""
            mylist = []
            # reading each word
            for word in line.split("\""):
                # displaying the words
                mylist.append(word)
            # took every word in specific attribute
            # logname  = 'BPI20151'
            acta = mylist[1]
            actb = mylist[3]
            # actc = mylist[3]
            # max = mylist[4]
            print(acta + ' ' + actb)
            # input from user:
            if val == "1":
                strtime = time.time()
                data = CP(db, acta, actb)
                print(len(data))
                end = time.time()
                type = "Chain Preced " + db
            elif val == "2":
                strtime = time.time()
                data = RE(db, acta, actb)
                print(len(data))
                end = time.time()
                type = "Responded Existence " + db
            elif val == "3":
                strtime = time.time()
                data = AP(db, acta, actb)
                print(len(data))
                end = time.time()
                type = "Alternate Preced " + db

            x.append(str((end - strtime)))
            y.append(len(data))
            z.append(val)
            m.append(type)
            strtime = 0
            end = 0
            # then add it to dataframe
            d = {'Timestamp': x, 'data': y, 'Method': z, 'type': m}
            # d = {'Timestamp': x}
            dataframe = pd.DataFrame(d)
            if not file_exists:
                dataframe.to_csv('Executiontime_sqlminer_antipatterns.csv', mode='a', index=False,
                                 header=['Timestamp', 'data', 'Method', 'type'])
                file_exists = True
            else:
                dataframe.to_csv('Executiontime_sqlminer_antipatterns.csv', mode='a', index=False, header=False)
    answer = (input("Would you like to choose another method?: "))
    if str(answer) == 'yes':
        cont = True
    else:
        cont = False
'''openfile = input("Enter file.txt ")
#type =  input("time or without or minmax")
activities = []
logname=[]
lgname = ""
constraint = ""
contType= []
totaltime =0
strtime =0
end = 0
acta=""
actb=""
aftbef="" #after or before
with open(str(openfile), "r") as file:
    val = input(
        "response or precede")
    db = input("enter database name: ")

    for line in file:
        x = []
        y = []
        z = []
        m = []
        type = ""
        mylist = []
        # reading each word
        for word in line.split("\""):
            mylist.append(word)
        acta = mylist[1]
        actb = mylist[3]
        max = mylist[4]  # ,float(max)
        
        if val == "response":
            # start
            strtime = time.time()
            data = response_without(db,acta,actb)
            end = time.time()
            totaltime += (end - strtime);
            print("totaltime:  ")
            print(totaltime);
            type = "response " + db
        elif val == "precede":
            strtime = time.time()
            data = precedence_without(db,acta,actb)
            end = time.time()
            totaltime += (end-strtime);
            print(totaltime)
            type = "precede " + db


        logname = []
        contType = []
        activities.clear()'''