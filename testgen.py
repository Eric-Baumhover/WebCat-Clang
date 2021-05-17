import os, sys, subprocess, stat
from glob import glob as find
import webcat as WebCat

def create_tests(test_type, config):
    # CXXTESTGEN ARGS
    args = ['--error-printer', '--have-eh', '--abort-on-fail', '--no-static-init', '-o']

    # Args are different between student and instructor.
    if test_type == 'student':
        args += [config['build'] + '/runStudentTests.cpp']
        args += find(config['basedir'] + '/*.h')

    elif test_type == 'instructor':
        args += [config['build'] + '/runInstructorTests.cpp']
        args += [os.path.join(config['scriptData'],config['testCases'])]
    
    program = config['cxxtest.dir'] + '/bin/cxxtestgen'

    if not os.access(program, os.X_OK):
        print('CXXTESTGEN is not executable, running chmod.')
        os.chmod(program, 0o777)

    args = [program] + args

    print('Executing command: ' + ' '.join(args))
    test_process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    test_process.wait()
    # Get the return code and logs.
    test_code = test_process.returncode
    test_log, test_error = test_process.communicate()
    if test_code != 0:
        WebCat.addReport(config, test_type + '_cxxgen_error.html', 'cxxestgen error for ' + test_type, test_error)