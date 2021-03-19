import os, sys, subprocess, re, math
from testgen import create_tests
from compile import compile
from code_coverage import runCodeCoverage
from cxl import gradeStyle
import webcat as WebCat
from grade_coverage import gradeCoverage

try:
    config_file_name = sys.argv[1]
    #config_file_name = "debug.grading.properties"

    config = WebCat.importConfig(config_file_name)

    config['build']             = config['resultDir'] + '/bin'
    config['student.tests']     = config['build'] + '/runStudentTests.exe'
    config['instructor.tests']  = config['build'] + '/runInstructorTests.exe'
    config['cxxtest.dir']       = config['scriptHome'] + '/cxxtest-4.4'
    config['basedir']           = config['workingDir']
    config['mac'] = False
    config['numReports'] = 0
    
    

    try:
        print(os.popen('chmod +x ' + config['cxxtest.dir'] + '/bin/cxxtestgen').read())

        os.mkdir(config['build'])

        student_successful = True

        score_correctness = 1.0
        score_tools       = 1.0

        create_tests('student', config)
        compile_return = compile('student', config)
        if compile_return == 0:
            os.environ['LLVM_PROFILE_FILE'] = config['build'] + '/runStudentTests.profraw'
            test_process = subprocess.Popen([config['student.tests']], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            test_process.wait()
            test_code = test_process.returncode
            test_log, test_error = test_process.communicate()
            
            print(test_log)

            cases_match = re.match('(?:Running cxxtest tests \((\d+) tests\)){0,1}',test_log)
            
            if cases_match is None:
                print('No cases found by RegEx')
                score_correctness = 0.0

            test_cases = int(test_log[cases_match.start(1) : cases_match.end(1)]) if not (cases_match is None) else 0

            

            WebCat.addReport(config,'student_test_log.html','Log from Student Tests', test_log)
            if test_code != 0:
                if config['allStudentTestsMustPass'] == 'true':
                    print('Not all tests passed, a zero for you.')
                    score_correctness = 0.0
                else:
                    final_match = re.search('(?:(\d{1,2})%[\s\n]{0,}$)', test_log)

                    if final_match is None:
                        print('No result percentage found in log.')
                        score_correctness = 0.0
                    else:
                        percent_string = final_match.groups()[0]
                        print(percent_string)
                        percent = int(percent_string)
                        print(percent / 100)
                        score_correctness *= percent / 100
                student_successful = False
                
            minimum_tests = int(config['minimumTestCases'])
            if test_cases < minimum_tests and minimum_tests != 0:
                print('Not enough tests')
                score_correctness *= test_cases / minimum_tests

            
            print('\n')

            runCodeCoverage(config)

            functions   = bool(config['coverageCheckFunctions'])
            inst        = bool(config['coverageCheckInstances'])
            regions     = bool(config['coverageCheckRegions'])
            
            result, templates = gradeCoverage(config['resultDir'] + '/coverageData.json', functions, inst, True, regions)
            if not result:
                print('Bad code coverage')
                score_tools = 0.0
            if math.ceil(templates) < int(config['minimumTemplateInstances']):
                score_tools = 0.0
                print('Not enough template instances.')
            
        else:
            student_successful = False
            score_correctness = 0.0

        instructorTests = False
        instructorRan = False
        if config.get('testCases', False) and os.path.isdir(os.path.join(config['scriptData'],config['testCases'])):
            instructorTests = True
            create_tests('instructor', config)
            compile_return = compile('instructor', config)
            if compile_return == 0:
                test_process = subprocess.Popen([config['instructor.tests']], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
                test_process.wait()
                test_code = test_process.returncode
                test_log, test_error = test_process.communicate()
                WebCat.addReport(config,'instructor_test_log.html','Log from Instructor Tests', test_log)
                if test_code != 0:
                    score_tools = 0.0
                else:
                    instructorRan = True
            else:
                score_tools = 0.0
        
        style_score = gradeStyle(config, config['basedir'], config['scriptHome'] + '/cpplint.py', config['resultDir'])
        score_tools *= style_score / 10


        config['score.correctness'] = score_correctness * float(config['max.score.correctness'])
        config['score.tools']       = score_tools * float(config['max.score.tools'])

    except:
        print("Unexpected error: ", sys.exc_info())
        config['score.correctness'] = 0
        config['score.tools']       = 0

    WebCat.exportConfig(config_file_name, config)
    
except:
    print("Unexpected error outside main block: ", str(sys.exc_info()))