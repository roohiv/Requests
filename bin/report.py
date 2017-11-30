import setup as base
import HTMLTestRunner
import unittest
import sys, re
import makejsonfromvariables as make
import dmaaptestapi as dmaap
import textwrap
import genericfunctions as generic
import pip, importlib
import prettytable


def CreateTestCase(testcaseresult):
    def test(self):
            from prettytable import PrettyTable
            if isinstance(testcaseresult, list):
                if "PASS" in testcaseresult[0]:
                    #r = testcaseresult.split("\n")
                    #res_list = r[1].split(",")
                    res_list = testcaseresult[1]
                    t = PrettyTable(['Keys', 'Values Matched'])
                    for j in range(0, len(res_list)):
                        r1 = res_list[j].split("#@")
                        t.add_row([textwrap.fill(str(r1[0]), 90), textwrap.fill(str(r1[1]), 70)])
                        t.add_row(['', ''])
                    resultl = t
                    print "\n"
                    print resultl
                elif "FAIL" in testcaseresult[0]:
                    #r = testcaseresult.split("\n")
                    #res_list = r[1].split(",")
                    res_list = testcaseresult[1]
                    t = PrettyTable(['Keys', 'Expected Values', 'Actual Result'])
                    for j in range(0, len(res_list)):
                        r1 = res_list[j].split("#@")
                        x = r1[1].split("*V*")
                        expected_value = x[1]
                        actual_result = x[2]
                        t.add_row([textwrap.fill(str(r1[0]), 50), textwrap.fill(str(expected_value), 50), textwrap.fill(str(actual_result), 50)])
                        t.add_row(['', '', ''])
                    resultl = t
                    print "\n"
                    print resultl
                    print "\n"
                    self.fail("Values not found or changed")
                    #elif re.search("ERROR", testcaseresult) or re.search("Error", testcaseresult) or re.search("Err", testcaseresult):
            else:
                    resultl = testcaseresult
                    print "\n"
                    print resultl
                    print "\n"
                    self.fail("No response")

    return test


class Suite(unittest.TestCase):
    message = True


r = []
def controller():
    for i in range(1, base.colcount):
        #uniqueval = generic.UniqueKeyword()
        uniqueval = str(generic.GetEpochMicroseconds())
        payload = make.createjsonrequestforexecutable(i, base.worksheet, base.config, base.BaseDir, uniqueval)
        if not(str(payload) == "Skipped"):
            requestat = base.SaveJson(payload, base.worksheet.cell(0, i).value, "request", "Request", base.BaseDir, base.config)
        if not(("Err : You have set more parameters than Request Json can accommodate" in str(payload)) or ("Skipped" in str(payload))):
            poststatus = dmaap.post(payload, base.config, i, base.worksheet, base.BaseDir)
            if "Publish Successful" in str(poststatus):
                result = dmaap.getandverifyresponse(base.worksheet, i, base.config, base.BaseDir, uniqueval)
                if generic.listinstance(result) == True:
                    responseat = result[1]
                    result = result[0]
                    print responseat
            else:
                result = poststatus
        else:
            result = payload
        r.insert(i, result)
    return r

#def createunittest(result, worksheet):
#    return suite


def generatereport(result, worksheet, BaseDir, config):
    suite = unittest.TestSuite()
    lengthofresult = len(result)
    for i in range(0, lengthofresult):
        #if not (re.search("Skipped", result[i].strip())):
      if not isinstance(result[i], list):
        if not (re.search("Skipped", result[i])):
            testcase_name = worksheet.cell(0, i + 1).value
            check_function = CreateTestCase(result[i])
            check_function.__name__ = 'test_expected_%d' % i
            setattr(Suite, 'test_{0}'.format(testcase_name), check_function)
            suite.addTest(Suite('test_{0}'.format(testcase_name)))
      else:
          testcase_name = worksheet.cell(0, i + 1).value
          check_function = CreateTestCase(result[i])
          check_function.__name__ = 'test_expected_%d' % i
          setattr(Suite, 'test_{0}'.format(testcase_name), check_function)
          suite.addTest(Suite('test_{0}'.format(testcase_name)))
    fp = open(BaseDir + "Result/" + config[2] + '_suite_result.html', 'wb')
    runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title='Report of Tests in Suite ' + config[2], verbosity=3,
                                           description='')
    del sys.argv[1:]
    runner.run(suite)

#red = controller()
#generatereport(red, base.worksheet, base.BaseDir, base.config)








