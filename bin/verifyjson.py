import deepdiff
import genericfunctions as generic
import setup as base
import json


#data contains a list of key from input sheet to verify in response output ********
def VerifyChildObject(data, response, value, result):
    if len(data) > 1:
            i = 0
            if isinstance(response, dict):
                if str(data[i]).strip() in response.keys():
                    j = response[str(data[i]).strip()]  # this can be a list or dict
                    if isinstance(j, (list, dict)):
                        key = data[i]
                        del data[i]
                        result = result.join(key + "|"+VerifyChildObject(data, j, value, result))
                        return result
                else:
                    key = data[i]
                    result = result.join(key+"| #@  *V* " + value + " *V*  Key not available")
                    return result
            elif isinstance(response, list):
                data[i] = int(data[i])
                if data[i] < len(response):
                    j = response[data[i]]
                    key = data[i]
                    del data[i]
                    result = result.join("[" + str(key)+"] |" + VerifyChildObject(data, j, value, result))
                    return result
                else:
                    key = data[i]
                    result = result.join("["+str(key)+"] #@ *V* " + value + " *V*  Key not present in response")
                    return result
    elif data[0].strip() in response.keys():
        if response[data[0].strip()] == value:
            key = data[0]
            result = result.join(key+"| #@ "+value+" [Found True ]")
            return result
        elif (response[data[0].strip()]).strip() == "" and value.strip() == "":
            key = data[0]
            result = result.join(key + "| #@ " + value + " [Found True ]")
            return result
        elif "testdata_" in response[data[0].strip()]:
            if value in response[data[0].strip()]:
                key = data[0]
                result = result.join(key + "| #@ " + value + " [Found True ]")
                return result
            else:
                key = data[0]
                v = response[key]
                result = result.join(key + "|#@  *V* " + value + " *V* " + v)
                return result
        else:
            key = data[0]
            v = response[key]
            result = result.join(key + "|#@  *V* " + value + " *V* " + v)
            return result
    else:
        key = data[0]
        result = result.join(key + "| #@  *V* " + value + " *V*  Key not present in response")
        return result


#Actual Output from get command in responseout variable *************************
def VerifyJson(responseout, responsedata):
    result = []
    for k, v in responsedata.iteritems():
        if not str(v) == "NA":
            if "," in k:
                x = ""
                nested_key = k.split(",")
                result.append(VerifyChildObject(nested_key, responseout, str(v), x))
            elif k in responseout.keys():
                if responseout[k] == v:
                    result.append("|"+str(k) + "| #@ " + str(v) + " [Found True ]")
                else:
                    result.append("|" + str(k) + "| #@ *V* " + str(v) + " *V* Key not present in response")
            else:
                result.append("|" + str(k) + "| #@ *V* " + str(v) + " *V*  Key not present in response")
    resultx = []
    resulty = []
    j = 0
    for i in range(0, len(result)):
        if not ("True" in result[i]):
            resultx.insert(j, str(result[i]))
            j += 1
        else:
            resulty.insert(j, str(result[i]))
            j += 1
    if not (len(resultx) > 0):
        print "-----------------------------------------------------------------------------------------------"
        base.log.info("Result : PASS", extra={'timestamp': base.timestamp})
        base.log.info("Values Matched :"+str(resulty), extra={'timestamp': base.timestamp})
        print "-----------------------------------------------------------------------------------------------\n"
        rex = []
        rex.insert(0, "PASS")
        rex.insert(1, resulty)
        return rex
        #return "PASS" + "\n" + str(resulty)
    else:
        print "-----------------------------------------------------------------------------------------------"
        base.log.info("Result : FAIL", extra={'timestamp': base.timestamp})
        base.log.info("Values not found or changed :" + str(resultx), extra={'timestamp': base.timestamp})
        base.log.info("Values Matched :" + str(resulty), extra={'timestamp': base.timestamp})
        y = "Values Matched :" + str(resulty)
        print "-----------------------------------------------------------------------------------------------\n"
        rex = []
        rex.insert(0, "FAIL")
        rex.insert(1, resultx)
        return rex
        #return "FAIL  " + "\n" + str(resultx)


# *** Independent Json Compare **************************************
def compare_json(a, b):
    # t6 = json.loads(generic.ReadFromFile("C:\\Users\\rv692q\\PycharmProjects\\Robot\\Result\\Response\\response_Snmp Trap_isisAttemptToExceedMaxSequence_1509047167c.json"))
    # t5 = json.loads(generic.ReadFromFile("C:\\Users\\rv692q\\PycharmProjects\\Robot\\Result\\Response\\response_Snmp Trap_isisAttemptToExceedMaxSequence_1509047167.json"))
    t7 = json.loads(generic.ReadFromFile(a))
    t8 = json.loads(generic.ReadFromFile(b))
    ddiff = deepdiff.DeepDiff(t7, t8, verbose_level=2)
    return ddiff