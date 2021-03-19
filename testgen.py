import os, sys
from glob import glob as find

def create_tests(test_type, config):
    args = ['--error-printer', '--have-eh', '--abort-on-fail', '--no-static-init', '-o']

    if test_type == 'student':
        args += [config['build'] + '/runStudentTests.cpp']
        args += find(config['basedir'] + '/*.h')

    elif test_type == 'instructor':
        args += [config['build'] + '/runInstructorTests.cpp']
        args += [os.path.join(config['scriptData'],config['testCases'])]
    

    
    command = config['cxxtest.dir'] + '/bin/cxxtestgen ' + ' '.join(args)

    print('Executing command: ' + command)
    print(os.popen(command).read())