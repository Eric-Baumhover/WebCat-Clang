import os, glob, sys, subprocess, re
from glob import glob as find
import webcat as WebCat
from time import sleep

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
    source_args = find(basedir + '/*.cpp') + find(basedir + '/*.h')
    sources = ' '.join(source_args)

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
    base_args = ['llvm-cov-8','show', '-format=text','-Xdemangler','c++filt','-Xdemangler','-n','-show-line-counts-or-regions','-instr-profile',build+'/runStudentTests.profdata',student_tests]
    #cov_report = os.popen('llvm-cov-8 show ' + '-format=html -Xdemangler c++filt -Xdemangler -n -region-coverage-lt=1 -show-line-counts-or-regions -instr-profile ' + build + '/runStudentTests.profdata ' + student_tests + ' ' + sources).read()

    with open(result_dir + '/coverageReport.html', 'w') as file_data:
        markup_process = subprocess.Popen(base_args + source_args, stdout=file_data, stderr=subprocess.STDOUT, universal_newlines=True)
        markup_code = markup_process.wait()
        return markup_code