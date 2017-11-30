import genericfunctions as generic
import setup as base
import json
import re, time


# *** Create json from variables **************
def UpdateJson(json_name, testdata):
    testdata = json.dumps(testdata, ensure_ascii=False)
    testdata = json.loads(testdata)
    tx = generic.ReadFromFile(json_name)
    parent_json = json.loads(tx)
    for k, v in testdata.iteritems():
        # if not str(v) == "NA":
        if "," in k:
            nested_key = k.split(",")
            try:
                parent_json = UpdateChildObject(nested_key, parent_json, v)
            except IndexError as e:
                base.log.error("Error: {}".format(e), extra={'timestamp': base.timestamp})
                parent_json = "You have set more parameters than Request Json can accommodate"
                return parent_json
            except Exception as e:
                base.log.error("Error: {}".format(e), extra={'timestamp': base.timestamp})
                return "Error: {}".format(e)
        else:
            parent_json[k] = v
    parent_json = json.dumps(parent_json, ensure_ascii=False)
    return parent_json


# *** Updating child objects ********************
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


# *** Deleting values set as NA from list ******
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


# *** Deleting values set as NA *************
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


def createjsonrequestforexecutable(i, worksheet, config, BaseDir, uniqueval):
    col_num = base.FindTestForExecution(worksheet, i)
    if col_num == "True":
        base.log.info("Iteration: " + str(i), extra={'timestamp': base.timestamp})
        if not (i == 1):
            time.sleep(int(config[4]))
        testdata = base.ReadFromExcel(worksheet, i, uniqueval, config[3], "Post Request", "Execute", config[5])
        payload = UpdateJson(BaseDir + config[0], testdata)
        if not re.search("You have set more parameters than Request Json can accomodate", payload):
            payload = DeleteUnwantedValues(payload)
            return payload
        else:
            base.log.error("Err : You have set more parameters than Request Json can accomodate",
                           extra={'timestamp': base.timestamp})
            result = "Err : You have set more parameters than Request Json can accomodate"
            base.WriteResult(BaseDir, result, i, config[2])
            return result
    else:
        result = "Skipped"
        base.WriteResult(BaseDir, result, i, config[2])
        return result