import os, glob, sys, subprocess
from glob import glob as find
import webcat as WebCat

def getCompilerArgs(test_type, config : dict):

    arg_log = 'Deciding on compilation arguments.\n\n'

    # Get necessary values from environment.
    cxxtest_dir             = config['cxxtest.dir']
    basedir                 = config['basedir']
    result_dir              = config['resultDir']
    code_coverage           = config.get('codeCoverage', False)
    mac                     = config.get('mac', False)
    script_home             = config['scriptHome']
    build                   = config['build']
    assignment_includes     = config.get('assignmentIncludes', False)
    general_includes        = config.get('generalIncludes', False)
    assignment_lib          = config.get('assignmentLib', False)
    general_lib             = config.get('generalLib', False)

    args = []
    # Add default args.
    if test_type != 'tool':
        args = ['-O0','-g3','-Wall','-fnon-call-exceptions','-finstrument-functions']
    else:
        args = ['--', 'clang++-8', '-x', 'c++']
    arg_log += 'Using default compilation arguments: ' + ' '.join(args) + '\n'

    # If code coverage is needed, add necessary args.
    # For context on the comparison with code coverage,
    # if there is no value for an ant variable, 
    # it uses the string literal.
    #
    # Also, the code coverage file is outputted based
    # on the LLVM_PROFILE_FILE env variable which is 
    # passed in in the build.xml
    if code_coverage and test_type == "student":
        arg_log += 'Code coverage enabled. Adding args: -fprofile-instr-generate -fcoverage-mapping \n'
        args += ['-fprofile-instr-generate','-fcoverage-mapping']

    # Mac vs not mac require different libraries.
    if mac:
        args + ['-lobjc','-lsymreader']
    else:
        args + ['-lbfd']
    arg_log += 'Adding platform specific arguments.\n'

    # Include cxxtest and stdc++
    args += ['-I' + cxxtest_dir,'-I' + basedir]
    arg_log += 'Adding default include directories: cxxtest and basedir.\n'
    if test_type != 'tool':
        args += ['-lstdc++']
    else:
        args += ['-I/usr/include/x86_64-linux-gnu/c++/5/','-I/usr/include/c++/5/', '-I/usr/lib/gcc/x86_64-linux-gnu/5/include']
    arg_log += 'Adding stdc++ as a library.\n'

    # If additional includes exit for this assignment, 
    # add them.
    if assignment_includes:
        arg_log += "Assignment Includes exist, adding.\n"
        args += ['-I' + assignment_includes]

    # Other includes.
    if general_includes:
        arg_log += "General Includes exist, adding.\n"
        args += ['-I' + general_includes]

    # Similar to the includes, but with libraries this time.
    assignment_lib_valid    = assignment_lib != False
    general_lib_valid       = general_lib    != False
    if assignment_lib_valid or general_lib_valid:
        
        #If there are any libraries start a linking group.
        args += ['--start-group']

        if assignment_lib_valid:
            arg_log += "Assignment Library exists, adding.\n"
            args += ['-L' + assignment_lib]
        
        if general_lib_valid:
            arg_log += "General Library exists, adding.\n"
            args += ['-L' + general_lib]
        
        args += ['--end-group']

    # Output correctly if its a student or an 
    # instructor test.
    if test_type == 'student':
        student_tests           = config['student.tests']
        args += ['-o', student_tests]
    elif test_type == 'instructor':
        instructor_tests        = config['instructor.tests']
        args += ['-o', instructor_tests]

    files = []

    if test_type == 'student':
        # Files need to be added, all cpp files first.
        files = find(basedir + '/*.cpp')
        # Then the o files in the plugin to prevent
        # system calls.
        files += find(script_home + '/obj/*.o')
        # Finally use the correct tests.
        files += [build + '/runStudentTests.cpp']
    elif test_type == 'instructor':
        # Files need to be added, all cpp files first.
        files = find(basedir + '/*.cpp')
        # Then the o files in the plugin to prevent
        # system calls.
        files += find(script_home + '/obj/*.o')
        # Finally use the correct tests.
        files += [build + '/runInstructorTests.cpp']

    arg_log += '\n'
    args += files

    return args, arg_log

def compile(test_type, config):
    try:
        print('Compiling tests for type: ' + test_type)

        # We use an argument to determine which args to use, as well as environment variables.
        args, arg_log = getCompilerArgs(test_type, config)

        # Complete the command.
        command = ['clang++-8'] + args

        arg_log += '\nExecuting command: ' + ' '.join(command) + '\n'

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        process.wait()
        code = process.returncode
        arg_log += 'Exited with code ' + str(code) + '\n\n'
        log, error = process.communicate()

        title_start = 'Student Compiling ' if test_type == 'student' else 'Instructor Compiling '

        WebCat.addReport(config, test_type + '_compile_log.html', title_start + 'Tests', arg_log + log)
        if code != 0:
            WebCat.addReport(config, test_type + '_compile_error_log.html', title_start + 'Errors', error)
        return code
    except:
        print("Compile error: ", str(sys.exc_info()))

    