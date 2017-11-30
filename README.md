Pre-requisites

1.	Install Python 2.7.13

2.	Installation procedure for the following services (2-A through 2-F below) is identical;  use the following procedure for each service name listed:

Open a windows command prompt (Start > cmd) and execute the ‘pip install’ command as outlined below. 

•	Substitute the service name being installed for <serviceName>
pip install <serviceName>

A.	Install the requests service: service name = requests

B.	Install the xlrd service: service name = xlrd

C.	Install the xlwt service: service name = xlwt

D.	Install the xlutils service: service name = xlutils

E.	Install the robotframework service: service name = robotframework

F.	Install the deepdiff service: service name = deepdiff

G.	Install the prettytable service: service name = prettytable


To Execute Automation-

Key Files to be created:

1.	config.ini- This file contains details for endpoint url, userid, password for publish and subscription.

2.	sample.json- This file contains json template for a particular uri.

2.      mapping.xls- This file contains testdata in separate columns which will be populated in sample json for publish. Json key fields in sample json are written in mapping excel using comma separated values, which help to verify json structure.

SetUp Configurations for Execution:

A config.ini, sampledata.json and mapping.xls file on your PC workstation for execution of your automation scenarios.  Once prepared, use the following procedure to execute:

1.	Open a Windows command prompt window and navigate to the \bin directory cloned from git.  (This is the directory which contains file fm-test-controller.robot.)

2.	Identify the path of the directory containing the config.ini, sampledata.json and mapping.xls files for the automation scenarios to be  run. 


Execute command Example:

c:\path to code files>robot -d <path to config>  fm-test-controller.robot


Result

1.	A Result folder will be created in the path(path of config file) which will contain html results for executed test cases.

2.	Result Folder will contain separate request and response folders which will contains requests and responses for each set of data to be in mapping excelfile.

3.	There will robot generated log file in html and xml format for the executed test cases.	

Key Functionalities Covered:

1.	Creation of Json for publish for each set of test data in mapping excel file.

2.	Publishing Json using python requests api.

3.	Subscribing to Unique Json which is created in Step 1 appending timestampmicrosec to any eventidentifier key field using python requests api.

4.	Considering each set of test data as a testcase, using Python Unit Testing Framework.

5.	Verifying subscribed json against expected values present in mapping excelfile.

6.	Generating HTML Report for the verified Result for each and every test case using Python Unit Testing Framework.

7.	Generating Robot HTML and XML Log File for the executed test cases.
 

End-of-Document 
asdf
