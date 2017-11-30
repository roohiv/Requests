*** Settings ***
Library  OperatingSystem
Library  String
Library  Collections
Library  setup.py
Library  makejsonfromvariables.py
Library  dmaaptestapi.py
Library  report.py
Library  genericfunctions.py
Library  verifyjson.py
Suite Setup  Initial


*** Variables ***
#${OUTPUT_DIRs}=  C:/Users/rv692q/PycharmProjects/Automation/PythonCallfinal/HP-Edge/regression/jerichosnmp


*** Test Cases ***
Test Suite
    : FOR  ${i}  IN RANGE  1  ${colcount}
    # *** Generating Uniquekeyword for every testcase ******************************************* 
    \   ${testcasename}=  gettestcasename  ${worksheet}  ${i}
    \   Log to console  ${\n}Test-${testcasename}   
    \   ${Epochmicroseconds}=  GetEpochMicroseconds
    \   ${uniqueval}=  Convert to String  ${Epochmicroseconds} 
    # *** Creating Json from variables in excel as per sample json provided *********************    
    \   ${payload}=  createjsonrequestforexecutable  ${i}  ${worksheet}  ${config}  ${BaseDir}  ${uniqueval}
    # *** No Action if testcase is set as skipped ***********************************************
    \   ${skippedtestcase}=  comp    ${payload}    Skipped
    \   ${requestat}=  RUN KEYWORD IF      ${skippedtestcase}!=True  SaveJson  ${payload}  ${testcasename}  request  Request  ${BaseDir}  ${config} 
    \   ${Request}=   RUN KEYWORD IF      ${skippedtestcase}!=True  Catenate  SEPARATOR=  RequestAT-   ${requestat}
    \   RUN KEYWORD IF      ${skippedtestcase}!=True  Log to console  ${Request}
    \   ...  ELSE  Log to console  Skipped  
    # *** Post Action for testcase set for execution ********************************************
    \   ${poststatus}=  RUN KEYWORD IF      ${skippedtestcase}!=True  post      ${payload}      ${config}      ${i}  ${worksheet}  ${BaseDir}
    \   ...             ELSE   Set Variable  "Skipped"
    # *** Checking Publish Status ***************************************************************
    \   ${Publish}=  comp  ${poststatus}  Publish Successful
    # *** Get if Post has been successful *******************************************************
    \   ${result}=  RUN KEYWORD IF  ${Publish}==True  getandverifyresponse  ${worksheet}  ${i}  ${config}  ${BaseDir}  ${uniqueval}
    \   ...         ELSE IF  ${skippedtestcase}==True    Set Variable  "Skipped" 
    \   ...         ELSE  Set Variable      ${poststatus}
    # *** Result ********************************************************************************
    \   ${saveresponse}=  RUN KEYWORD IF  ${Publish}==True  listinstance  ${result}
    \   ${responseat}=  Run Keyword if  ${saveresponse}==True  Get From List  ${result}  1
    \   ${result}=   Run Keyword if  ${saveresponse}==True  Get From List  ${result}  0
    \   ...  ELSE  Set Variable  ${result} 
    \   Run Keyword if  ${saveresponse}==True  Log to console  ${\n}ResponseAT-${responseat}
    \   @{results}=  Run Keyword if  ${i}==1  create list  ${result}
    \   Run Keyword if  ${i}==1  Set Suite Variable  @{r}  @{results}
    \   Run Keyword if  ${i}!=1  Append to list  ${r}  ${result}
    # *** Report Creation **************************************************************
    generatereport  ${r}  ${worksheet}  ${BaseDir}  ${config}
    ${r}=  Convert to String  ${r}
    SHOULD NOT CONTAIN  FAIL  ${r}


#Compare two independent json
#    ${Difference}=  compare_json    ${Path_Json1}     ${Path_Json2}
#    Log to console  ${Difference}    

    
*** Keywords ***
Initial
     ${BaseDir}=  Catenate  SEPARATOR=  ${OUTPUT_DIR}  /
     ${configpath}=   Catenate  SEPARATOR=  ${BaseDir}  config.ini
     @{config}=  Configuration    ${configpath}
     ${workbookname}=  Get From List  ${config}  1
     ${workbookpath}=  Catenate  SEPARATOR=  ${BaseDir}  ${workbookname}
     ${worksheetname}=  Get From List  ${config}  2
     ${worksheet}=  OpenExcelWorksheet  ${workbookpath}  ${worksheetname}
     ${colcount}=  GetColumnsCount  ${worksheet}
     ${EpochTime}=  GetEpochTime
     ${timestamp}=  Convert to String  ${EpochTime}
     ${Epochmicroseconds}=  GetEpochMicroseconds
     ${timemicroseconds}=  Convert to String  ${Epochmicroseconds}
     Set Suite Variable  @{config}  @{config}
     Set Suite Variable  ${worksheet}  ${worksheet}
     Set Suite Variable  ${worksheetname}  ${worksheetname}
     Set Suite Variable  ${colcount}  ${colcount}
     Set Suite Variable  ${BaseDir}  ${BaseDir}
     
     

    
    