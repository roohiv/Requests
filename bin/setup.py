import genericfunctions as generic
import os, errno, logging
import sys, re
import pip, importlib
import xlwt
import xlrd
import xlutils


def Configuration(filename):
    from ConfigParser import SafeConfigParser
    parser = SafeConfigParser()
    parser.read(filename)
    lister =[]
    #Path Variables
    lister.append(str(parser.get("PathVariables", "refinputjson")))
    lister.append(str(parser.get("PathVariables", "testdatafile")))
    lister.append(str(parser.get("PathVariables", "worksheetname")))
    lister.append(str(parser.get("PathVariables", "eventidentifier")))
    lister.append(str(parser.get("PathVariables", "sleep time between events")))
    lister.append(str(parser.get("PathVariables", "appendflag")))
    #lister.append(str(parser.get("PathVariables", "BaseDir")))
    #Post Variables
    lister.append(str(parser.get("PostVariables", "posturl")))
    lister.append(str(parser.get("PostVariables", "postusername")))
    lister.append(str(parser.get("PostVariables", "postpassword")))
    #Get Variables
    lister.append(str(parser.get("GetVariables", "geturl")))
    lister.append(str(parser.get("GetVariables", "getusername")))
    lister.append(str(parser.get("GetVariables", "getpassword")))
    return lister


def WriteResult(BaseDir, result, cur_col, worksheetname):
    file_result = "log"+".xls"
    path = BaseDir
    path_file = path+file_result
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    if not os.path.exists(path_file):
       try:
        book = xlwt.Workbook()
        sh = book.add_sheet(sheetname=worksheetname, cell_overwrite_ok=True)
        sh.write(0, 0, "Data Sets")
        sh.write(1, 0, "Result Of Column:" + str(cur_col))
        sh.write(0, 1, "Result")
        sh.write(1, 1, result)
        book.save(path_file)
       except :
           log.error("Result excel could not be created", extra={'timestamp': timestamp})
    else:
       try:
        rb = xlrd.open_workbook(path_file, formatting_info=True)
        from xlutils.copy import copy
        wb = copy(rb)
        wsh = wb.get_sheet(0)
        wsh.write(cur_col, 0, "Result Of Column:" + str(cur_col))
        wsh.write(cur_col, 1, result)
        wb.save(path_file)
       except :
           log.error("Result excel could not be written", extra={'timestamp': timestamp})


# logger
def Logger():
    '''path = "log\\"
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    filename = "log.log"
    if not (os.path.exists(path + "/" + filename)):
        f = file(path + "/" + filename, "w")'''
    FORMAT = '%(asctime)s %(name)s.%(funcName)s <line> %(lineno)s: <TS> %(timestamp)s %(levelname)s  [%(thread)d] %(message)s'
    '''logging.basicConfig(level=logging.INFO,
                        format=FORMAT,
                        filename="log/" + "log.log")'''
    logging.basicConfig(level=logging.INFO,
                        format=FORMAT)
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    formatter = logging.Formatter(FORMAT)
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    log = logging.getLogger("fm-test-controller")
    return log


def SaveJson(output, cur_col, filename, refdir, BaseDir, config):
    filename = filename + "_" + config[2] + "_" + cur_col
    path = BaseDir + "Result/" + refdir
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    if not (os.path.exists(path + "/" + filename + "_" + timestamp + ".json")):
        f = file(path + "/" + filename + "_" + timestamp + ".json", "w")
        f.write(str(output))
        return path + "/" + filename + "_" + timestamp + ".json"
    else:
        log.error("file already exists", extra={'timestamp': timestamp})
        return "file already exists"


# Function to read from excel test data and create request
def ReadFromExcel(worksheet, cur_col, uniqueval, tag, startkeyword, endkeyword, appendflag):
        rowEndIndex = worksheet.nrows - 1
        rowStartIndex = 0
        for j in range(0, rowEndIndex - 1):
            if (worksheet.cell_value(j, 0)).strip() == startkeyword.strip():
                rowStartIndex = j + 1
                break
        testdata = {}
        curr_row = rowStartIndex
        x = rowStartIndex
        if cur_col > 0:
            while curr_row <= rowEndIndex:
                execute_flag = worksheet.cell_value(curr_row, 0)
                if endkeyword.strip() in execute_flag:
                    rowEndIndex = curr_row
                    break
                else:
                    curr_row += 1
                    continue
            curr_row = rowStartIndex
            while curr_row < rowEndIndex:
                if isinstance(worksheet.cell(curr_row, cur_col).value, (int)):
                    testdata[str(worksheet.cell(curr_row, 0).value).strip()] = int(worksheet.cell(curr_row, cur_col).value)
                elif isinstance(worksheet.cell(curr_row, cur_col).value, (float)):
                    testdata[str(worksheet.cell(curr_row, 0).value).strip()] = float(worksheet.cell(curr_row, cur_col).value)
                else:
                    if re.search("epochmicro", worksheet.cell(curr_row, cur_col).value):
                        testdata[str(worksheet.cell(curr_row, 0).value).strip()] = generic.GetEpochMicroseconds()
                    elif re.search("epochtime", worksheet.cell(curr_row, cur_col).value):
                        testdata[(worksheet.cell(curr_row, 0).value).strip()] = generic.GetEpochTime()
                    else:
                        testdata[(worksheet.cell(curr_row, 0).value).strip()] = (
                        worksheet.cell(curr_row, cur_col).value).strip()
                curr_row += 1
            if appendflag == "Y":
                for k in testdata.keys():
                    if tag in k:
                        testdata[k] += "testdata_" + uniqueval
                return testdata
            elif appendflag == "N" or appendflag == "":
                return testdata
        else:
            return "Err: Test Column is equal to Keys Column or it is invalid "


def FindTestForExecution(worksheet, col_number):
    i = col_number
    colEndIndex = worksheet.ncols - 1
    rowEndIndex = worksheet.nrows - 1
    row_test = 0
    col_test = 0
    for j in range(0, rowEndIndex-1):
        if worksheet.cell_value(j, 0) == "Execute":
            row_test = j
            break
    #for i in range(i, colEndIndex):
    if str(worksheet.cell_value(row_test, i)) == ("Yes" or "Y" or "y" or "yes"):
            col_test = i
            return "True"
    else:
            col_test = "Err: No Column to Test"
            return col_test


#Flow
#config = Configuration(str(sys.argv[1]))
#BaseDir = "C:/Users/rv692q/PycharmProjects/Automation/PythonCallfinal/HP-Edge/regression/jerichosnmp/"
#BaseDir = str(sys.argv[1])
#config = Configuration(BaseDir+"config.ini")
#worksheet = generic.OpenExcelWorksheet(BaseDir+config[1], config[2])
#worksheet = generic.OpenExcelWorksheet(config[5]+config[1], config[2])
#colcount = generic.GetColumnsCount(worksheet)
timestamp = str(generic.GetEpochTime())
uniqueval = generic.UniqueKeyword()
log = Logger()

