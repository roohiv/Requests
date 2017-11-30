import setup as base
import json
import pip, time, importlib
import requests
import urllib3
import re, socket, textwrap
import verifyjson as verify
import genericfunctions as generic


#Function to post *
def PostRequest(url, username, password, payload):
    #********check json validity***********************
    try:
        payload = json.loads(payload)
    #*********Converting payload to format readable by requests library*
        payload = json.dumps(payload, ensure_ascii=False)
    except ValueError:
        return "Err : Not a Valid Json for Post"
    except Exception as e:
        return "Err : {}".format(e)
    flag = 0
    #*****Try to post 3 times*******************************************
    while flag <= 2:
        try:
            urllib3.disable_warnings()
            if username == "":
                r = requests.post(url=url, data=payload, verify=False)
            else:
                r = requests.post(url=url, data=payload, auth=(username, password), verify=False)
            base.log.info("Post :"+str(r), extra={'timestamp': base.timestamp})
            #********Return payload if post has been successful**********
            if r.ok:
                base.log.info("Request: " + payload, extra={'timestamp': base.timestamp})
                return payload
            else:
                return "Err : Post unsuccessful"+str(r.status_code)
        except requests.exceptions as e:
            flag += 1
            if flag <= 2:
                base.log.error("Try "+str(flag)+" Error: {}".format(e), extra={'timestamp': base.timestamp})
            else:
                base.log.error("Dmaap not responding.........", extra={'timestamp': base.timestamp})
                return "Err : Dmaap not responding........."
        except Exception as e:
            flag += 1
            if flag <= 2:
                base.log.error("Try " + str(flag) + " Error: {}".format(e), extra={'timestamp': base.timestamp})
            else:
                base.log.error("Dmaap not responding.........", extra={'timestamp': base.timestamp})
                return "Err : Dmaap not responding........."


#* Function to get *
def GetResponse(url, username, password, uniqueval, appendflag, tag, ref_resp):
    base.log.info("In Get", extra={'timestamp': base.timestamp})
    #****Create Consumergroup as hostname***********
    try:
        consumergroup = generic.hostname()
        #***If hostname is blank setting consumer group as some default value
        if consumergroup == "":
            consumergroup = "ab123c"+base.uniqueval
        else:
            consumergroup = consumergroup+base.uniqueval
    except socket.error, exc:
        return "Err : Caught exception socket.error : %s" % exc
    #***  Url for getting ***************************
    url = url + "/" +consumergroup+"/0"
    base.log.info(url, extra={'timestamp': base.timestamp})
    flag_g = 0
    #*** Try get 3 times if unsuccessful ************
    while flag_g <= 2:
        try:
            #***Case for Global Dmaap****************
            if username == "":
                time.sleep(10)
                response = requests.get(url, verify=False, timeout=60)
                flag_g += 1
            #*** General Dmaap **********************
            else:
                time.sleep(10)
                if flag_g == 0:
                    base.log.info("Try " + str(flag_g + 1) + " :To Get unique Json", extra={'timestamp': base.timestamp})
                from urllib3 import warnings
                urllib3.disable_warnings()
                response = requests.get(url, auth=(username, password), verify=False, timeout=60)
                flag_g += 1
            flag = 0
            testrespose = []
            try:
              #*** If get is successful **********************
              if response.status_code == 200:
                base.log.info("Response content"+response.content, extra={'timestamp': base.timestamp})
                #print response.content
                testrespose = response.json()
                #*** Finding particular json as per unique value provided ****************
                if len(testrespose) > 0:
                    for k in ref_resp.keys():
                        if tag in k:
                            uniqueval = ref_resp[k]
                            break
                    for i in range(0, len(testrespose)):
                            if appendflag == "Y":
                                if ("testdata_" + uniqueval) in str(testrespose[i]):
                                    flag = 1
                                    response = testrespose[i]
                                    break
                            elif appendflag == "N" or appendflag == "":
                                if i == 0:
                                    rtest = []
                                    j = 0
                                if str(uniqueval) in str(testrespose[i]):
                                    flag = 1
                                    rtest.insert(j, testrespose[i])
                                    j += 1
                                if len(rtest) > 1:
                                    base.log.error("Received more than one value as per event identifier, cannot get a unique json", extra={'timestamp': base.timestamp})
                                    return "Err : Could not get unique json " + str(rtest)
                                elif len(rtest) == 1 and len(rtest) == len(testrespose):
                                    response = rtest[0]                  #------------------------Unique Response
                                else:
                                    continue
            #***Catch any invalid json***********************
            except ValueError as e:
                base.log.error("Error: {}".format(e), extra={'timestamp': base.timestamp})
                return "Err : Not a valid response " + testrespose.content
            except Exception as e:
                base.log.error("Error: {}".format(e), extra={'timestamp': base.timestamp})
                return "Err :  " + testrespose.content
            if flag == 0 and flag_g > 2:
                return "Err : Could not Get your unique json after 3 trials"
            elif flag == 0 and flag_g <= 2:
                base.log.warning("Try " + str(flag_g) +" failed, Try " + str(flag_g + 1) + "  :To Get unique Json", extra={'timestamp': base.timestamp})
                continue
            else:
                t = json.loads(response)
                t_for_print = json.dumps(t, ensure_ascii=False)
                base.log.info("Found Unique Response on Try : " + str(flag_g) + t_for_print, extra={'timestamp': base.timestamp})
                return t
        except requests.exceptions as e:
            flag_g += 1
            if flag_g <= 2:
                base.log.error("Try " + str(flag_g) + " Error: {}".format(e), extra={'timestamp': base.timestamp})
            else:
                base.log.error("Get Timed Out", extra={'timestamp': base.timestamp})
                return "Err : Get Timed Out--Could not get response"
        except Exception as e:
            base.log.error(" Error: {}".format(e), extra={'timestamp': base.timestamp})
            return "Err : {}".format(e)


def post(payload, config, i, worksheet, BaseDir):
    connstatus = PostRequest(config[6], config[7], config[8], payload)
    if not re.search("Err", connstatus):
        return "Publish Successful"
    else:
        base.log.error("Publish not successful. Try Later " + connstatus, extra={'timestamp': base.timestamp})
        result = "Publish not successful. Try Later " + connstatus
        base.WriteResult(BaseDir, result, i, config[2])
        return result


def getandverifyresponse(worksheet, i, config , BaseDir, uniqueval):
        ref_resp = base.ReadFromExcel(worksheet, i, uniqueval, config[3], "GetResponse", "End", config[5])
        testrespose = GetResponse(config[9], config[10], config[11], uniqueval, config[5], config[3], ref_resp)
        if not("Err" in str(testrespose)):
            testrespose1 = json.dumps(testrespose, ensure_ascii=False)
            responseat=base.SaveJson(testrespose1, worksheet.cell(0, i).value, "response", "Response", BaseDir, config)
            result = verify.VerifyJson(testrespose, ref_resp)
            base.WriteResult(BaseDir, str(result), i, config[2])
            resultat = []
            resultat.insert(0, result)
            resultat.insert(1, responseat)
            return resultat
        else:
            base.log.error("ERROR in GET: " + str(testrespose), extra={'timestamp': base.timestamp})
            result = "ERROR in GET: " + textwrap.fill(str(testrespose), 90)
            base.WriteResult(BaseDir, result, i, config[2])
            return result