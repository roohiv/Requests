import random
import time
import socket, pip, importlib
import xlrd


#Function to write to a text file
def ReadFromFile(filename):
    read_file = open(filename).read()
    return read_file


#Function to generate random number
def RandomNumber():
    randomnumber = random.randint(0, 100)
    return randomnumber


#Function to create json by appending unique random number
def UniqueKeyword():
    randomnumber = RandomNumber()
    uniqueval = str(randomnumber)
    return uniqueval


def hostname():
    hostname = socket.gethostname()
    return hostname

def createlistrec(r, i, val):
    r.insert(i, str(val))
    return r


def comp(str1, str2):
    str1 = str(str1)
    str2 = str(str2)
    if str2 in str1:
        return "True"
    else:
        return "False"


def OpenExcelWorksheet(filename_excel, worksheet_name):
    workbook = xlrd.open_workbook(filename_excel)
    worksheet = workbook.sheet_by_name(worksheet_name)
    return worksheet


def GetEpochMicroseconds():
    from datetime import datetime
    dt = datetime.now()
    epoch = datetime.utcfromtimestamp(0)
    epochmicrosec = int(round((dt - epoch).total_seconds() * 1000.0))
    # epochmicrosec = int(round(time.time() * 1000))
    #print epochmicrosec
    #epochmicrosec = int(round(time.time() * 1000))
    return epochmicrosec


def listinstance(r):
    if isinstance(r, list):
        return True
    else:
        return False


def gettestcasename(worksheet, i):
    testcasename = worksheet.cell(0, i).value.strip()
    return testcasename



def GetEpochTime():
    epochtime = int(round(time.time()))
    return epochtime


def GetColumnsCount(worksheet):
    cols = worksheet.ncols
    return cols


def GetFlagRow(worksheet):
    for i in range(0, worksheet.nrows-1):
        if "Execute" in worksheet.cell_value(i, 0):
            return i
    return "Execute Flag not Found"



