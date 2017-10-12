import requests
import xlrd
import random
import time
import json
import xlwt
import HTMLTestRunner
import unittest
import textwrap
import os, errno, logging
import sys, re, pytest

#function to GET response
def GetResponse(url, username, password, uniqueval):
    log.info("In Get", extra={'timestamp': timestamp})
    #url = url + "/" +"rv"+uniqueval+"/"+uniqueval
    #log.info(url, extra={'timestamp': timestamp})
    flag_g = 0
    while flag_g <= 2:
        try:
            if username == "":
                time.sleep(10)
                response = requests.get(url, verify=False)
                flag_g += 1
            else:
                time.sleep(10)
                if flag_g == 0:
                    log.info("Try " + str(flag_g) + " :To Get your unique Json", extra={'timestamp': timestamp})
                #response = requests.get(url, auth=(username, password))
                response = requests.get(url, auth=(username, password), verify=False, timeout=60)
                flag_g += 1
            testrespose = response.content
            testrespose = json.loads(testrespose)
            t = {}
            flag = 0
            response = ""
            for s in testrespose:
                if ("testdata_"+uniqueval) in s:
                    flag = 1
                    response = response + s
            if flag == 0 and flag_g > 2:
                return "Could not Get your unique json after 3 trials"
            elif flag == 0 and flag_g <= 2:
                log.warning("Try "+str(flag_g)+" :Could not Get your unique json", extra={'timestamp': timestamp})
                continue
            else:
                t = json.loads(response)
                t_for_print = json.dumps(t, ensure_ascii=False)
                #t_for_print = textwrap.fill(str(t_for_print), 70)
                log.info("Found Unique Response on Try : "+str(flag_g)+t_for_print, extra={'timestamp': timestamp})
                return t
        except requests.exceptions.ConnectionError as e:
                #e = textwrap.fill(str(e), 70)
                flag_g += 1
                if flag_g <= 2:
                    log.error("Try "+str(flag_g)+" Error: {}".format(e), extra={'timestamp': timestamp})
                else:
                    log.error("Dmaap not responding try later..", extra={'timestamp': timestamp})
                    return "Err : Dmaap not responding try later.."
        except requests.HTTPError as e:
            #e = textwrap.fill(str(e), 70)
            flag_g += 1
            if flag_g <= 2:
                log.error("Try "+str(flag_g)+" Error: {}".format(e), extra={'timestamp': timestamp})
            else:
                log.error("Dmaap not responding try later..", extra={'timestamp': timestamp})
                return "Err : Dmaap not responding try later.."
        except requests.exceptions.Timeout as e:
            flag_g += 1
            if flag_g <= 2:
                log.error("Try "+str(flag_g)+" Error: {}".format(e), extra={'timestamp': timestamp})
            else:
                log.error("Get Timed Out", extra={'timestamp': timestamp})
                return "Err : Get Timed Out--Could not get response"


def SaveJson(output, cur_col, filename, refdir):
        filename = filename+"_"+config[2]+"_"+cur_col
        path = config[5]+"Result/"+refdir
        if not os.path.exists(path):
           try:
              os.makedirs(path)
           except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
        if not(os.path.exists(path+"/"+filename+"_"+timestamp+".json")):
            f = file(path+"/"+filename+"_"+timestamp+".json", "w")
            f.write(str(output))
        else:
            log.error("file already exists", extra={'timestamp': timestamp})


'''def check_connection(url):
    url = "https://dcae-msrt-mtl1-ftl.homer.att.com:3905"
    try :
        conn = httplib.HTTPConnection(url)
        r = requests.head(url)
        print r.text, r.status_code, r.headers
        #conn.request("HEAD", "/")
        #r = conn.getresponse()
        #print r.status
    except requests.exceptions.ConnectionError as e:
        return "Error: {}".format(e)
    return r'''


#Function to post request
def PostRequest(url, username, password, payload, i):
    payload = json.loads(payload)
    payload = json.dumps(payload, ensure_ascii=False)
    SaveJson(payload, worksheet.cell(1, i).value, "request", "Request")
    flag = 0
    while flag <= 2:
        try:
            #r = requests.post(url=url, data=payload, auth=(username, password))
            r = requests.post(url=url, data=payload, auth=(username, password), verify=False)
            log.info("Post :"+str(r), extra={'timestamp': timestamp})
            if r.ok:
                log.info("Request: " + payload, extra={'timestamp': timestamp})
                return payload
            else:
                return "Err : Post unsuccessful"+str(r.status_code)
        except requests.exceptions.ConnectionError as e:
            #e = textwrap.fill(str(e), 70)
            flag += 1
            if flag <= 2:
                log.error("Try "+str(flag)+" Error: {}".format(e), extra={'timestamp': timestamp})
            else:
                log.error("Dmaap not responding try later.........", extra={'timestamp': timestamp})
                return "Err : Dmaap not responding try later........."
        except requests.HTTPError as e:
            #e = textwrap.fill(str(e), 70)
            flag += 1
            if flag <= 2:
                log.error("Try "+str(flag)+" Error: {}".format(e), extra={'timestamp': timestamp})
            else:
                log.error("Dmaap not responding try later.........", extra={'timestamp': timestamp})
                return "Err : Dmaap not responding try later........."


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


#data contains a list of key from input sheet to verify in response output
def VerifyChildObject(data, response, value, result):
    if len(data) > 1:
        #for i in range(0, len(data)):
            i = 0
            if isinstance(response, dict):
                if str(data[i]).strip() in response.keys():
                    j = response[str(data[i]).strip()]  # this can be a list or dict
                    if isinstance(j, (list, dict)):
                        key = data[i]
                        del data[i]
                        result = result.join("Key- "+key+" found- " + VerifyChildObject(data, j, value, result))
                        return result
                else:
                    key = data[i]
                    result = result.join("Key - "+key+" not available")
                    return result
            elif isinstance(response, list):
                data[i] = int(data[i])
                if data[i] < len(response):
                #if data[i] <= len(response):
                    j = response[data[i]]
                    key = data[i]
                    del data[i]
                    result = result.join("Listed item at- " + str(key)+" found- " + VerifyChildObject(data, j, value, result))
                    return result
                else:
                    key = data[i]
                    result = result.join("Listed item at- "+str(key)+" is not present in the Response")
                    return result
    elif data[0].strip() in response.keys():
        if response[data[0].strip()] == value:
            key = data[0]
            result = result.join("Key- "+key+" Value- "+value+" found: True")
            return result
        elif (response[data[0].strip()]).strip() == "" and value.strip() == "":
            key = data[0]
            result = result.join("Key- " + key + " Value- " + value + " found: True")
            return result
        elif "testdata_" in response[data[0].strip()]:
            if value in response[data[0].strip()]:
                key = data[0]
                result = result.join("Key- " + key + " Value- " + value + " found: True")
                return result
            else:
                key = data[0]
                v = response[key]
                result = result.join("Key- " + key + " expected value- " + value + " actual value- " + v)
                return result
        else:
            key = data[0]
            v = response[key]
            result = result.join("Key- " + key + " expected value- " + value + " actual value- "+v)
            return result
    else:
        key = data[0]
        result = result.join("Key- " + key + " not present in response")
        return result


def UpdateChildObject(data, parent_json, value):
  length = len(data)
  if len(data) > 1:
    if isinstance(parent_json, dict):
            i = 0
        #for i in range(0, len(data)):
            for each in parent_json:
                if each == data[i]:
                    child_json = parent_json[each]
                    if isinstance(child_json, (list, dict)):
                            del data[i]
                            UpdateChildObject(data, child_json, value)
                            return parent_json
                    else:
                        parent_json[each].update(value)
                        return parent_json
    elif isinstance(parent_json, list):
            if len(parent_json) > 1:
                tag = int(data[0])
                del data[0]
            else:
                tag = 0
            child_json = parent_json[tag]
            parent_json[tag] = UpdateChildObject(data, child_json, value)
  else:
        if isinstance(parent_json, list):
            if len(parent_json) > 1:
                tag = data[0]
                del data[0]
            else:
                tag = 0
            child_json = parent_json[tag]
            parent_json[tag] = UpdateChildObject(data, child_json, value)
        else:
            if data[0] in parent_json:
                   key = str(data[0])
                   parent_json[key] = value
                   return parent_json


#Actual Output from get command in responseout variable
def VerifyJson(responseout, responsedata):
    result = []
    for k, v in responsedata.iteritems():
        if not str(v) == "NA":
            # print k
            if "," in k:
                x = ""
                nested_key = k.split(",")
                result.append(VerifyChildObject(nested_key, responseout, str(v), x))
                # print responsedata
            elif k in responseout.keys():
                if responseout[k].value == v:
                    result.append("True")
                else:
                    result.append("Key- " + str(k) + " value:" + str(v) + "not present in response ")
            else:
                result.append("Key- " + str(k) + "not present in response ")
    resultx = []
    j = 0
    # print len(result)
    for i in range(0, len(result)):
        if not ("True" in result[i]):
            resultx.insert(j, str(result[i]))
            j += 1
    if not (len(resultx) > 0):
        resultx.insert(0, "PASS")
        return str(resultx)
    else:
        return "FAIL : Values not found or changed : " + str(resultx)


def DeleteUnwantedValuesFromList(v):
    l = []
    j = 0
    for i in range(0, len(v)):
        if isinstance(v[i], dict):
            length1 = len(v[i].keys())
            v[i] = DeleteUnwantedValues(v[i])
            v[i] = json.loads(v[i])
            if len(v[i].keys()) == 0:
                length2 = len(v[i].keys())
                if length1 != length2:
                    l.append(i)
                    j += 1
        elif isinstance(v[i], list):
            DeleteUnwantedValuesFromList(v[i])
    n = len(l)
    any = 0
    if j > 0:
        while any < n:
            a = l[any]
            v.pop(a)
            any += 1
            for k in range(0, n):
                l[k] -= 1
    return v


def DeleteUnwantedValues(payload):
    if not isinstance(payload, dict):
        payload = json.loads(payload)
    p = payload
    for k, v in p.items():
        if isinstance(v, dict):
            DeleteUnwantedValues(v)
        elif isinstance(v, list):
            DeleteUnwantedValuesFromList(v)
        elif str(v).strip() == "NA":
            del payload[k]
        else:
            continue
    payload = json.dumps(payload, ensure_ascii=False)
    return payload


def UpdateJson(json_name, testdata):
     testdata = json.dumps(testdata, ensure_ascii=False)
     testdata = json.loads(testdata)
     tx = ReadFromFile(json_name)
     parent_json = json.loads(tx)
     for k, v in testdata.iteritems():
         #if not str(v) == "NA":
                if "," in k:
                    nested_key = k.split(",")
                    try:
                        parent_json = UpdateChildObject(nested_key, parent_json, v)
                    except IndexError:
                        parent_json = "You have set more parameters than Request Json can accomodate"
                else:
                    parent_json[k] = v
     parent_json = json.dumps(parent_json, ensure_ascii=False)
     return parent_json


def OpenExcelWorksheet(filename_excel, worksheet_name):
    workbook = xlrd.open_workbook(filename_excel)
    worksheet = workbook.sheet_by_name(worksheet_name)
    return worksheet


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


#Function to read from excel test data and create response
def ReadFromExcelRefResp(worksheet, cur_col, uniqueval, tag):
    rowEndIndex = worksheet.nrows - 1
    rowStartIndex = 0
    for j in range(0, rowEndIndex):
        if worksheet.cell_value(j, 0) == "GetResponse":
            rowStartIndex = j
            break
    for k in range(rowStartIndex, rowEndIndex):
        if worksheet.cell_value(k, 0) == "End":
            rowEndIndex = k
            break
    ref_resp = {}
    curr_row = rowStartIndex + 2
    if cur_col > 0:
        while curr_row < rowEndIndex:
            if not (isinstance(worksheet.cell_value(curr_row, cur_col), (int, float))):
                ref_resp[(worksheet.cell_value(curr_row, 0)).strip()] = (
                worksheet.cell_value(curr_row, cur_col)).strip()
                curr_row += 1
            else:
                ref_resp[(worksheet.cell_value(curr_row, 0)).strip()] = worksheet.cell_value(curr_row, cur_col)
                curr_row += 1
        for k in ref_resp.keys():
            if tag in k:
                ref_resp[k] += "testdata_" + uniqueval
        return ref_resp
    else:
        log.error("Err: Test Column is equal to Keys Column or it is invalid ", extra={'timestamp': timestamp})


#Function to read from excel test data and create request
def ReadFromExcel(worksheet, cur_col, uniqueval, tag, startkeyword, endkeyword):
    rowEndIndex = worksheet.nrows - 1
    rowStartIndex = 0
    for j in range(0, rowEndIndex - 1):
        if (worksheet.cell_value(j, 0)).strip() == startkeyword.strip():
            rowStartIndex = j+1
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
            if isinstance(worksheet.cell(curr_row, cur_col).value, (int, float)):
                testdata[str(worksheet.cell(curr_row, 0).value).strip()] = worksheet.cell(curr_row, cur_col).value
            else:
                if re.search("epochmicro", (worksheet.cell(curr_row, cur_col).value).strip()):
                    testdata[str(worksheet.cell(curr_row, 0).value).strip()] = timemicroseconds
                elif re.search("epochtime", (worksheet.cell(curr_row, cur_col).value).strip()):
                    testdata[(worksheet.cell(curr_row, 0).value).strip()] = timestamp
                else:
                    testdata[(worksheet.cell(curr_row, 0).value).strip()] = (worksheet.cell(curr_row, cur_col).value).strip()
            curr_row += 1
        for k in testdata.keys():
            if tag in k:
                testdata[k] += "testdata_" + uniqueval
        return testdata
    else:
        return "Err: Test Column is equal to Keys Column or it is invalid "


def WriteResult(result, cur_col, worksheetname, itr):
    file_result = "Result"+".xls"
    path = "Result\\"
    path_file = path+file_result
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    if not os.path.exists(path_file):
        book = xlwt.Workbook()
        sh = book.add_sheet(sheetname=worksheetname, cell_overwrite_ok=True)
        sh.write(0, 0, "Data Sets")
        sh.write(1, 0, "Result Of Column:" + str(cur_col))
        sh.write(0, 1, "Result")
        sh.write(1, 1, result)
        book.save(path_file)
    else:
        rb = xlrd.open_workbook(path_file, formatting_info=True)
        from xlutils.copy import copy
        wb = copy(rb)
        wsh = wb.get_sheet(0)
        wsh.write(itr, 0, "Result Of Column:" + str(cur_col))
        wsh.write(itr, 1, result)
        wb.save(path_file)



def GetColumnsCount(worksheet):
    cols = worksheet.ncols
    return cols


def GetFlagRow(worksheet):
    for i in range(0, worksheet.nrows-1):
        if "Execute" in worksheet.cell_value(i, 0):
            return i
    return "Execute Flag not Found"


def Configuration(filename):
    from ConfigParser import SafeConfigParser
    parser = SafeConfigParser()
    parser.read(filename)
    lister =[]
    #Path Variables
    lister.append(str(parser.get("PathVariables", "RefInputJson")))
    lister.append(str(parser.get("PathVariables", "TestdataFile")))
    lister.append(str(parser.get("PathVariables", "Worksheetname")))
    lister.append(str(parser.get("PathVariables", "UniqueIdentifier")))
    lister.append(str(parser.get("PathVariables", "Sleep Time Between Events")))
    lister.append(str(parser.get("PathVariables", "BaseDir")))
    #Post Variables
    lister.append(str(parser.get("PostVariables", "PostUrl")))
    lister.append(str(parser.get("PostVariables", "PostUsername")))
    lister.append(str(parser.get("PostVariables", "PostPassword")))
    #Get Variables
    lister.append(str(parser.get("GetVariables", "GetUrl")))
    lister.append(str(parser.get("GetVariables", "GetUsername")))
    lister.append(str(parser.get("GetVariables", "GetPassword")))
    return lister


def GetEpochMicroseconds():
    epochmicrosec = int(round(time.time() * 1000))
    return epochmicrosec

def GetEpochTime():
    epochtime = int(round(time.time()))
    return epochtime



#Flow
config = Configuration(str(sys.argv[1]))
#config = Configuration("config.ini")
worksheet = OpenExcelWorksheet(config[5]+config[1], config[2])
colcount = GetColumnsCount(worksheet)
timestamp = str(GetEpochTime())
timemicroseconds = str(GetEpochMicroseconds())
j = GetFlagRow(worksheet)
itr = 1


#logger
def Logger():
    path = config[5] + "Result"
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    filename = "log.log"
    if not (os.path.exists(path + "/" + filename)):
        f = file(path + "/" + filename, "w")
    FORMAT = '%(asctime)s %(name)s.%(funcName)s <line> %(lineno)s: <TS> %(timestamp)s %(levelname)s  [%(thread)d] %(message)s'
    logging.basicConfig(level=logging.INFO,
                        format=FORMAT,
                        filename=config[5]+"Result/"+"log.log")
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    formatter = logging.Formatter(FORMAT)
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    log = logging.getLogger(config[2])
    return log


#def main(i, itr, worksheet, posturl, postusername, postpassword, geturl, getusername, getpassword, colcount, config):
def main(i, itr, worksheet, colcount, config):
    col_num = FindTestForExecution(worksheet, i)
    if col_num == "True":
        log.info("Iteration: " + str(itr), extra={'timestamp': timestamp})
    #if ("Yes" or "Y") in worksheet.cell_value(j, i):
        if not(i == 1):
            time.sleep(int(config[4]))
        uniqueval = UniqueKeyword()
        testdata = ReadFromExcel(worksheet, i, uniqueval, config[3], "Post Request", "Execute")
        payload = UpdateJson(config[5]+config[0], testdata)
        if not re.search("You have set more parameters than Request Json can accomodate", payload):
            payload = DeleteUnwantedValues(payload)
            connstatus = PostRequest(config[6], config[7], config[8], payload, i)
            if not re.search("Err", connstatus):
                ref_resp = ReadFromExcel(worksheet,i, uniqueval, config[3], "GetResponse","End")
                #ref_resp = ReadFromExcelRefResp(worksheet, i, uniqueval, config[3])
                testrespose = GetResponse(config[9], config[10], config[11], uniqueval)
                testrespose1 = json.dumps(testrespose, ensure_ascii=False)
                if not (re.search("Could not Get your unique json", testrespose1) or re.search("Err", testrespose1)):
                    SaveJson(testrespose1, worksheet.cell(1, i).value, "response", "Response")
                    #ref_resp = ReadFromExcelRefResp(worksheet, i, uniqueval, config[3])
                    result = VerifyJson(testrespose, ref_resp)
                    WriteResult(result, i, config[2], itr)
                    return result
                else:
                    log.error("Error in GET: "+str(testrespose), extra={'timestamp': timestamp})
                    result = "Error in GET: "+str(testrespose)
                    WriteResult(result, i, config[2], itr)
                    return result
            else:
                log.error("Publish not successful. Try Later " + connstatus, extra={'timestamp': timestamp})
                result = "Publish not successful. Try Later " + connstatus
                WriteResult(result, i, config[2], itr)
                return result
        else:
            log.error("Err : You have set more parameters than Request Json can accomodate", extra={'timestamp': timestamp})
            result = "Err : You have set more parameters than Request Json can accomodate"
            WriteResult(result, i, config[2], itr)
            return result
    else:
        result = "You've set No to execute this data"
        WriteResult(result, i, config[2], itr)
        return result


class SuiteReport(unittest.TestCase):
    message = True


def CreateTestCase(testcaseresult, param3):
    def test(self):
        if "PASS" in testcaseresult:
            pass
        else:
            result = "\n \n Iteration " + str(param3) + "\n" + "\n " + testcaseresult
            self.fail(result)
    return test

if __name__ == '__main__':
    log = Logger()
    for i in range(1, colcount):
        #result = main(i, i, worksheet, posturl, postusername, postpassword, geturl, getusername, getpassword, colcount, config)
        result = main(i, i, worksheet, colcount, config)
        result1 = textwrap.fill(str(result), 70)
        if not str(result).strip() == "You've set No to execute this data":
            testcase_name = worksheet.cell(1, i).value
            check_function = CreateTestCase(result1, i)
            check_function.__name__ = 'test_expected_%d' % i
            setattr(SuiteReport, 'test_{0}'.format(testcase_name), check_function)
    fp = open(config[5]+"Result/"+config[2]+'_Suite_Result.html', 'wb')
    runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title='Suite Report', verbosity=3, description='Report of Tests in Suite '+config[2])
    del sys.argv[1:]
    unittest.main(testRunner=runner)








