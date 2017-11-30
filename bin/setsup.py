import pip

def install(package):
    pip.main(['install', package])


install('robotframework')
install('xlrd')
install('xlwt')
install('xlutils')
install('prettytable')
install('requests')