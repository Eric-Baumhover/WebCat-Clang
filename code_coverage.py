import os, glob, sys, subprocess, re
from glob import glob as find
import webcat as WebCat
from time import sleep
import fnmatch

# Main code coverage function.
# Called from execute.py
def runCodeCoverage(config):

    # Get necessary directories
    build                   = config['build']
    basedir                 = config['basedir']
    result_dir              = config['resultDir']
    student_tests           = config['student.tests']

    # Run llvm-profdata merge in order to obtain 
    # code coverage data from a profraw file 
    # generated earlier.

    profdata_command = ['llvm-profdata-8','merge','-sparse', build + '/runStudentTests.profraw','-o', build + '/runStudentTests.profdata']

    print('Running command: ' + ' '.join(profdata_command))
    # Directly report to WebCAT.
    code = WebCat.commandReport(profdata_command, config, 'llvm-profdata-log.html', 'LLVM-PROFDATA-8 Debug Log', True, True)
    if code != 0:
        print('Error in LLVM-PROFDATA command!')
        return code


    # Get a list of the original sources, 
    # needed to narrow coverage data.
    source_files = find(basedir + '/*.cpp') + find(basedir + '/*.h')
    test_files = find(basedir + '/*test.h') + find(basedir + '/*Test.h')
    source_args = list(set(source_files).difference(test_files))

    print('Files for code coverage: ' + ' '.join(source_args))
    print()

    # Check that there is any data to gather.
    if len(source_args) > 0:

        sources = ' '.join(source_args)


        # Convert data into a per file summarized json version.
        json_export_command = ['llvm-cov-8','export','-summary-only','-instr-profile',build + '/runStudentTests.profdata',student_tests]
        print('Running command: ' + ' '.join(json_export_command+source_args))
        export_error = ''
        with open(result_dir + '/coverageData.json', 'w') as file_data:
            process = subprocess.Popen(json_export_command + source_args, stdout=file_data, stderr=subprocess.PIPE, universal_newlines=True)
            code = process.wait()
            log, export_error = process.communicate()
        if code != 0:
            print('Error in LLVM-COV Export')
            print(export_error)
            return code
        
        file_data.close()
        
        print()

        # Output a human readable report of the data.
        # List only areas that were never called.
        # Use a demangler to make it more readable.
        base_args = ['llvm-cov-8','show', '-format=html','-Xdemangler','c++filt','-Xdemangler','-n','-show-line-counts-or-regions','-instr-profile',build+'/runStudentTests.profdata',student_tests]
        print('Running command: ' + ' '.join(base_args+source_args))
        with open(result_dir + '/coverageReport.html', 'w') as file_data:
            markup_process = subprocess.Popen(base_args + source_args, stdout=file_data, stderr=subprocess.STDOUT, universal_newlines=True)
            code = markup_process.wait()

        # Fix html styling for WebCAT.

        lines = []
        with open(result_dir + '/coverageReport.html', 'r') as file_data:
            lines = file_data.readlines()

        lines = ['<div class="shadow"><table><tbody><tr><th>Code Coverage Data</th></tr><tr><td><div style="overflow: scroll; max-width: 60vw; max-height: 25vw;">'] + lines + ['</div></td></tr></tbody></table></div><div class="spacer">&nbsp;</div>']
        
        with open(result_dir + '/coverageReport.html', 'w') as file_data:
            file_data.writelines(lines)
        return code
        
    else:
        print('No non test files.')
        return 1