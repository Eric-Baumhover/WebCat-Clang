import os, glob, subprocess

cxxtest_dir             = os.getenv('cxxtest_dir')
cxxtest_symreader_dir   = os.getenv('cxxtest_symreader_dir')
basedir                 = os.getenv('basedir')
student_tests           = os.getenv('student_tests')
code_coverage           = os.getenv('code_coverage')
mac                     = os.getenv('mac')
script_home             = os.getenv('script_home')
build                   = os.getenv('build')

args = ['clang++-8','-O0','-g3','-Wall','-fnon-call-exceptions','-finstrument-functions','-DCXXTEST_INCLUDE_SYMREADER_DIRECTLY']

if True or code_coverage == 'true':
    print('Code coverage enabled. Adding args: -fprofile-instr-generate -fcoverage-mapping')
    args += ['-fprofile-instr-generate','-fcoverage-mapping']

if mac == 'true':
    args + ['-lobjc','-lsymreader']
else:
    args + ['-lbfd']

args += ['-I' + cxxtest_dir,'-I' + cxxtest_symreader_dir,'-I' + basedir,'-lstdc++','-o',student_tests]

files = glob.glob(basedir + '/*.cpp')
files += glob.glob(script_home + '/obj/*.o')
files += [build + '/runStudentTests.cpp']
args += files

command = ' '.join(args)

print('Python executing command: ' + command)

print(os.popen(command).read())

print('Running command: ' + student_tests)
print(os.popen(student_tests).read())

print('Running command: ' + 'llvm-profdata-8 merge -sparse ' + build + '/runStudentTests.profraw -o ' + build + '/runStudentTests.profdata')
print(os.popen('llvm-profdata-8 merge -sparse ' + build + '/runStudentTests.profraw -o ' + build + '/runStudentTests.profdata').read())

sources = ' '.join(glob.glob(basedir + '/*.cpp') + glob.glob(basedir + '/*.h'))

print('Running command: ' + 'llvm-cov-8 export ' + '-summary-only -instr-profile ' + build + '/runStudentTests.profdata ' + student_tests + ' ' + sources)
cov_data = os.popen('llvm-cov-8 export ' + '-summary-only -instr-profile ' + build + '/runStudentTests.profdata ' + student_tests + ' ' + sources).read()
print(cov_data)

print('Running command: ' + 'llvm-cov-8 show ' + '-region-coverage-lt=1 -show-line-counts-or-regions -instr-profile ' + build + '/runStudentTests.profdata ' + student_tests + ' ' + sources)
cov_report = os.popen('llvm-cov-8 show ' + '-Xdemangler c++filt -Xdemangler -n -region-coverage-lt=1 -show-line-counts-or-regions -instr-profile ' + build + '/runStudentTests.profdata ' + student_tests + ' ' + sources).read()
print(cov_report)