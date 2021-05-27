# Generic Python imports
import os, sys, subprocess, re, math, shutil, stat
from glob import glob as find

# Other files in plugin.
from testgen import create_tests
from compile import compile
from compile import getCompilerArgs
from code_coverage import runCodeCoverage
from cxl import gradeStyle
import webcat as WebCat
from grade_coverage import gradeCoverage


# Important part of any WebCAT plugin. This is the file that must be read from and written to. This is how grading is finalized.
config_file_name = sys.argv[1]

# This is necessary for the whole thing to work, this takes in all the data.
config = WebCat.importConfig(config_file_name)

# Set up some necessary values in the config that most things use.
# Build is the "Temporary" directory for intermediate files.
config['build']             = config['resultDir'] + '/bin'
# StudentTests is the executable made from student code and tests.
config['student.tests']     = config['build'] + '/runStudentTests.exe'
# InstructorTests is the executable made from instructor tests and student code.
config['instructor.tests']  = config['build'] + '/runInstructorTests.exe'
# CXXTESTDir is the directory containing the cxxtest 4 library and executables.
config['cxxtest.dir']       = config['scriptHome'] + '/cxxtest'
# Basedir is the folder with student code.
config['basedir']           = config['workingDir']
# Mac messes with some command line arguments, no implementation exists other than that. Carry over from CXL.
config['mac'] = False
# Initialization of counters for reports.
config['numReports'] = 0
config['numCodeMarkups'] = 0

# Variable for later. Determines if there exists a coverage report to put at the end.
add_coverage_report = False

# Variable storing the message to the student explaining their grade.
grade_report = ''

try:
    #Copy data files into directory.
    if config.get('localFiles', False):
        # Determine the path of the data files.
        lf_path = os.path.join(config['scriptData'],config['localFiles'])
        # If its a directory loop, otherwise use just that file.
        if os.path.isdir(lf_path):
            for data_file in os.listdir(lf_path):
                shutil.copy(os.path.join(lf_path,data_file), config['basedir'] + "/" + data_file)
        else:
            base_path = os.path.basename(os.path.normpath(lf_path))
            shutil.copy(lf_path, config['basedir'] + base_path)

    # Make sure the temporary directory exists.
    os.mkdir(config['build'])

    # Should run instructor tests and other tools.
    student_successful = True

    # Initalize scores.
    config['score.correctness'] = 0.0
    config['score.tools'] = 0.0
    score_correctness = float(config['max.score.correctness'])
    score_style       = float(config['max.score.tools'])

#=============================================================================================================================================================================================
#              Student Test Block
#=============================================================================================================================================================================================
    try:
        # Runs CXXTESTGEN (in testgen.py)
        create_tests('student', config)
        # Compile the student code and get the result (in compile.py)
        compile_return = compile('student', config)
        if compile_return == 0:
            student_successful = True
            # If successful prepare for tests.
            # First specify where coverage data should go, regardless of if we need it.
            os.environ['LLVM_PROFILE_FILE'] = config['build'] + '/runStudentTests.profraw'
            # Run the tests.
            program = config['student.tests']
                    
            if not os.access(program, os.X_OK):
                print('No-Loops is not executable, running chmod.')
                os.chmod(program, 0o777)

            test_process = subprocess.Popen([program], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            test_process.wait()
            # Get the return code and logs. Test_Error is moved into Test_Log immediately, so its always null.
            test_code = test_process.returncode
            test_log, test_error = test_process.communicate()
            
            print(test_log)

            # Find the number of tests.
            cases_match = re.match('(?:Running cxxtest tests \((\d+) test){0,1}',test_log)

            # Check for failed match.
            if cases_match is None:
                print('No cases found by RegEx')
                grade_report += 'Error parsing cxxtest test number: Correctness = 0.0\n'
                score_correctness = 0.0

            # Store count as int.
            test_cases = int(test_log[cases_match.start(1) : cases_match.end(1)]) if not (cases_match is None) else 0

            
            # Display the result to WebCat. This is a utility function that is used a lot.
            WebCat.addReport(config,'student_test_log.html','Log from Student Tests', test_log)
            if test_code != 0:
                # If tests failed, decide how to grade.
                if config['allStudentTestsMustPass'] == 'true':
                    # If all must pass, that didn't happen, so 0.
                    print('Not all tests passed, a zero for you.')
                    grade_report += 'Not all tests passed: Correctness = 0.0\n'
                    score_correctness = 0.0
                else:
                    # Find out how many passed.
                    final_match = re.search('(?:(\d{1,2})%[\s\n]{0,}$)', test_log)
                    
                    if final_match is None:
                        # If the percentage cannot be found, a 0 must be given.
                        print('No result percentage found in log.')
                        grade_report += 'Not all tests passed and result percentage not found: Correctness = 0.0\n'
                        score_correctness = 0.0
                    else:
                        # Calculate percentage from match.
                        percent_string = final_match.groups()[0]
                        print(percent_string)
                        percent = int(percent_string)
                        print(percent / 100)
                        coefficient = percent / 100
                        grade_report += 'Not all student tests passed: Correctness Points Lost = ' + "%.1f" % (score_correctness * (1.0 - coefficient)) + '\n'
                        score_correctness *= coefficient
            else:
                grade_report += 'Your tests passed, nice.\n'
            
            # Run minimum tests check.
            minimum_tests = int(config.get('minimumTestCases', 0))
            if test_cases < minimum_tests and minimum_tests != 0:
                print('Not enough tests')
                coefficient = test_cases / minimum_tests
                grade_report += 'Did not reach minimum number of tests "' + str(minimum_tests) + '": Correctness Points Lost = ' + "%.1f" % (score_correctness * (1.0 - coefficient)) + '\n'
                score_correctness *= coefficient
            else:
                grade_report += 'You have enough tests, nice.\n'
            
            print('\n')

            try:
                # Run code coverage if set.
                if config.get('codeCoverage', 'false') != 'false':

                    # Execution is contained in this function. (in code_coverage.py)
                    add_coverage_report = runCodeCoverage(config) == 0
                    if add_coverage_report:

                        # Decide what to grade.
                        lines       = config.get('coverageCheckLines',     'false') != 'false'
                        inst        = config.get('coverageCheckInstances', 'false') != 'false'
                        regions     = config.get('coverageCheckRegions',   'false') != 'false'
                        
                        # Run grader. (in grade_coverage.py)
                        result, templates = gradeCoverage(config['resultDir'] + '/coverageData.json', True, inst, lines, regions)
                        if not result:
                            # Give a zero for failed coverage.
                            print('Bad code coverage')
                            grade_report += 'Not all code covered: Correctness Score = 0.0\n'
                            score_correctness = 0.0
                        else:
                            grade_report += 'You have perfect coverage, nice.\n'
                        # Grab minimum templates needed.
                        # This acts as a ratio. FunctionInstances / Functions is a rough approximation of template coverage.
                        min_templates = int(config.get('minimumTemplateInstances', 0))
                        if math.ceil(templates) < min_templates:
                            coefficient = math.ceil(templates) / min_templates
                            grade_report += 'Did not reach minimum ratio of covered templates "' + str(min_templates) + '": Correctness Points Lost = ' + "%.1f" % (score_correctness * (1.0 - coefficient)) + '\n'
                            score_correctness *= coefficient
                            print('Not enough template instances.')
                    else:
                        print("Unexpected error running code coverage: ")
                        grade_report += 'Error In Code Coverage Generation Block...\n'
                        score_correctness = 0.0
            except:
                print("Unexpected error running code coverage: ", str(sys.exc_info()))
                grade_report += 'Fatal Error In Code Coverage Test Block...\n'
                score_correctness = 0.0
                
            
        else:
            # If student code didn't compile, they get a full zero and nothing else runs.
            student_successful = False
            grade_report += 'Student Failed to compile: Score = 0.0\n'
            score_correctness = 0.0
            score_style = 0.0
    except:
        print("Unexpected error running student tests: ", str(sys.exc_info()))
        grade_report += 'Fatal Error In Student Block...\n'
        config['score.correctness'] = 0
#=============================================================================================================================================================================================

    if student_successful:
        try:
            instructorTests = False
            instructorRan = False
            if config.get('testCases', False) and not os.path.isdir(os.path.join(config['scriptData'],config['testCases'])):
#=============================================================================================================================================================================================
#              Instructor Test Block
#=============================================================================================================================================================================================
                instructorTests = True
                # Runs CXXTESTGEN
                create_tests('instructor', config)
                # Compile the instructor code and get the result
                compile_return = compile('instructor', config)
                if compile_return == 0:
                    # Run the instructor's executable.

                    program = config['instructor.tests']

                    if not os.access(program, os.X_OK):
                        print('No-Loops is not executable, running chmod.')
                        os.chmod(program, 0o777)

                    test_process = subprocess.Popen([program], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
                    test_process.wait()

                    test_code = test_process.returncode
                    test_log, test_error = test_process.communicate()

                    # Report to WebCAT. If there is an error give a 0.
                    WebCat.addReport(config,'instructor_test_log.html','Log from Instructor Tests', test_log)
                    if test_code != 0:
                        grade_report += 'Not all instructor tests passed: Correctness Score = 0.0\n'

                        score_correctness = 0.0

                    else:
                        grade_report += 'No problems with instructor tests, nice.\n'
                        instructorRan = True
                else:
                    grade_report += 'Instructor tests failed to compile: Correctness Score = 0.0\n'
                    score_correctness = 0.0
        except:
            print("Unexpected error running instructor tests: ", str(sys.exc_info()))
            grade_report += 'Fatal Error In Instructor Tests Block...\n'
            score_correctness = 0.0
#=============================================================================================================================================================================================
        
        # Run style grader.
        style_score = gradeStyle(config, config['basedir'], config['scriptHome'] + '/cpplint.py', config['resultDir'])
        # If there are problems with style, report and grade accordingly.
        if style_score < 10:
            # Ten is the max style score.
            coefficient = style_score / 10.0
            grade_report += 'Did not have perfect style score, you got "' + str(style_score) + '": Style Points Lost = ' + "%.1f" % (score_style * (1.0 - coefficient)) + '\n'
            score_style *= coefficient
        else:
            grade_report += 'Perfect style, nice.\n'

        basedir = config['basedir']
        
        # Precalculate files to compile for libtooling.
        source_files = find(basedir + '/*.cpp') + find(basedir + '/*.h')
        test_files = find(basedir + '/*test.h') + find(basedir + '/*Test.h')
        source_args = list(set(source_files).difference(test_files))

        # Check to make sure that libtooling is necessary.
        if (config.get('noLoops', 'false') != 'false' or config.get('noIndexing', 'false') != 'false'):

            # Make sure there is something to run the tools on.
            if len(source_args) != 0:
                try:
                    if config.get('noLoops', 'false') != 'false':
    #=============================================================================================================================================================================================
    #              No-Loops Test Block
    #=============================================================================================================================================================================================
                        # Run the tool.
                        program = config['scriptHome'] + '/bin/no-loops'

                        if not os.access(program, os.X_OK):
                            print('No-Loops is not executable, running chmod.')
                            os.chmod(program, 0o777)

                        loop_command = [program] + source_args + getCompilerArgs('tool', config)[0]
                        print('Running no-loops: ' + ' '.join(loop_command))
                        loop_process = subprocess.Popen(loop_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, cwd=config['basedir'])
                        loop_process.wait()
                        loop_code = loop_process.returncode
                        loop_log, loop_error = loop_process.communicate()

                        # Check for no output. If that fails there was a result.
                        if re.match('(^[\s\n]{0,}$)', loop_log) is None:
                            score_correctness = 0.0
                            grade_report += 'Found loops: Correctness Score = 0.0\n'
                            WebCat.addReport(config,'no-loops_test_log.html','Fail Log from No-Loop Tests', loop_log)
                        else:
                            grade_report += 'No loops found. Good work!\n'
                            print('No loops found. Good work!')
                        if re.match('(^[\s\n]{0,}$)', loop_error) is None:
                            print('Errors running no-loops!')
                            print(loop_error)
                            # Oh boy a no-loops error. Doesn't effect grade.
                            WebCat.addReport(config,'no-loops_test_error.html','No-Loop Error', 'There was an error with the no-loops check.\nThis won\'t effect your grade, tell your professor though.')
                        
                except:
                    print("Unexpected error inside no-loops call: ", str(sys.exc_info()))
                    grade_report += 'Fatal Error In No-Loops Block...\n'
                    score_correctness = 0.0

                try:
                    if config.get('noIndexing', 'false') != 'false':
    #=============================================================================================================================================================================================
    #              No-Indexing Test Block
    #=============================================================================================================================================================================================
                        # Run the tool.
                        program = config['scriptHome'] + '/bin/no-indexing'

                        if not os.access(program, os.X_OK):
                            print('No-Indexing is not executable, setting permissions.')
                            os.chmod(program, 0o777)
                        
                        indexing_command = [program] + source_args + getCompilerArgs('tool', config)[0]
                        print('Running no-indexing: ' + ' '.join(indexing_command))
                        index_process = subprocess.Popen(indexing_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, cwd=config['basedir'])
                        index_process.wait()
                        index_code = index_process.returncode
                        index_log, index_error = index_process.communicate()

                        # Check for no output. If that fails there was a result.
                        if re.match('(^[\s\n]{0,}$)', index_log) is None:
                            score_correctness = 0.0
                            grade_report += 'Found index operation: Correctness Score = 0.0\n'
                            WebCat.addReport(config,'no-indexing_test_log.html','Fail Log from No-Indexing Tests', index_log)
                        else:
                            grade_report += 'No array indexing operations found. Good work!\n'
                            print('No array indexing operations found. Good work!')
                        if re.match('(^[\s\n]{0,}$)', index_error) is None:
                            print('Errors running no-indexing!')
                            print(index_error)
                            # Oh boy a no-indexing error. Doesn't effect grade.
                            WebCat.addReport(config,'no-indexing_test_error.html','No-Indexing Error', 'There was an error with the no-indexing check.\nThis won\'t effect your grade, tell your professor though.')
                        
                except:
                    print("Unexpected error inside no-indexing call: ", str(sys.exc_info()))
                    grade_report += 'Fatal Error In No-Indexing Block...\n'
                    score_correctness = 0.0
            else:
                grade_report += 'No non test files found. Non test files must exist. Score = 0\n'
                print('No non test files found.')
                score_style = 0.0
                score_correctness = 0.0
#=============================================================================================================================================================================================
    # Finalize score.
    config['score.correctness'] = score_correctness
    config['score.tools']       = score_style

    # Delete temporary directory if specified.
    if config.get('doNotDelete', 'true') == 'false':
        shutil.rmtree(config['build'])

except:
    print("Unexpected error: ", sys.exc_info())
    config['score.correctness'] = 0.0
    config['score.tools']       = 0.0
    grade_report += 'Fatal Error... Score 0.0\n'

# Print out score in a formatted manner.
score_str = '%.1f' % (config['score.correctness'] + config['score.tools']) 
grade_report += 'Final Score: ' + score_str

# Add the grading information as a report.
try:
    WebCat.addReport(config,'grade_report.html','Grade Report', grade_report)
except:
    print("Unexpected error writing grade report: ", str(sys.exc_info()))

# Add coverage data as the final report.
if add_coverage_report:
    WebCat.addExistingReport(config, 'coverageReport.html')

# This is necessary for the whole thing to work, this finalizes the output.
WebCat.exportConfig(config_file_name, config)