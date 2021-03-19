import os, glob, sys
from glob import glob as find
import webcat as WebCat

def runCodeCoverage(config):
    #TODO: Add fail checks

    # Get necessary directories
    build                   = config['build']
    basedir                 = config['basedir']
    result_dir              = config['resultDir']
    student_tests           = config['student.tests']

    # Run llvm-profdata merge in order to obtain 
    # code coverage data from a profraw file 
    # generated earlier.
    print('Running command: ' + 'llvm-profdata-8 merge -sparse ' + build + '/runStudentTests.profraw -o ' + build + '/runStudentTests.profdata')
    print(os.popen('llvm-profdata-8 merge -sparse ' + build + '/runStudentTests.profraw -o ' + build + '/runStudentTests.profdata').read())

    # Get a list of the origin sources, 
    # needed to narrow coverage data.
    sources = ' '.join(find(basedir + '/*.cpp') + find(basedir + '/*.h'))

    # Convert data into a per file summarized json version.
    print('Running command: ' + 'llvm-cov-8 export ' + '-summary-only -instr-profile ' + build + '/runStudentTests.profdata ' + student_tests + ' ' + sources)
    cov_data = os.popen('llvm-cov-8 export ' + '-summary-only -instr-profile ' + build + '/runStudentTests.profdata ' + student_tests + ' ' + sources).read()

    # Save this data to a file for later.
    print('Saving to file: ' + result_dir + '/coverageData.json')
    file_data = open(result_dir + '/coverageData.json', 'w')
    file_data.write(cov_data)
    file_data.close()

    # Output a human readable report of the data.
    # List only areas that were never called.
    # Use a demangler to make it more readable.
    print('Running command: ' + 'llvm-cov-8 show ' + '-region-coverage-lt=1 -show-line-counts-or-regions -instr-profile ' + build + '/runStudentTests.profdata ' + student_tests + ' ' + sources)
    cov_report = os.popen('llvm-cov-8 show ' + '-Xdemangler c++filt -Xdemangler -n -region-coverage-lt=1 -show-line-counts-or-regions -instr-profile ' + build + '/runStudentTests.profdata ' + student_tests + ' ' + sources).read()

    # Add this coverage report to reports in webcat
    WebCat.addReport(config, 'coverageReport.html', 'Code Not Covered', cov_report)