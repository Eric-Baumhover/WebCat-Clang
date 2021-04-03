import os, sys, subprocess
from glob import glob as find
import webcat as WebCat

def create_tests(test_type, config):
    args = ['--error-printer', '--have-eh', '--abort-on-fail', '--no-static-init', '-o']

    if test_type == 'student':
        args += [config['build'] + '/runStudentTests.cpp']
        args += find(config['basedir'] + '/*.h')

    elif test_type == 'instructor':
        args += [config['build'] + '/runInstructorTests.cpp']
        args += [os.path.join(config['scriptData'],config['testCases'])]
    
    args = [config['cxxtest.dir'] + '/bin/cxxtestgen'] + args

    print('Executing command: ' + ' '.join(args))
    test_process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    test_process.wait()
    # Get the return code and logs.
    test_code = test_process.returncode
    test_log, test_error = test_process.communicate()
    if test_code != 0:
        WebCat.addReport(config, test_type + '_cxxgen_error.html', 'cxxestgen error for ' + test_type, test_error)