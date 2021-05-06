import sys, os, glob
from os import path
import subprocess as sp
import webcat as WebCat

def gradeStyle(config, pathName, script, resultDir):

    #==============================================================
    # Extraction and file directory management:
    #==============================================================
    fileCount = 0
    fileName  = ""
    pathCheck = path.exists(pathName)

    if not pathCheck:
        print("No such directory: {}".format(pathName))
        return 0

    files = [os.path.join(pathName, f) for f in os.listdir(pathName) if os.path.isfile(os.path.join(pathName, f))]
    fileCount = len(files)
    print(files)

    seperator = ' '

    #==============================================================
    # Build and execute python command for cpplint:
    #==============================================================
    with open("scriptRaw.txt", 'w') as out:
        res = sp.getoutput("python {} --verbose=5 --exclude=*/ --exclude=*.zip --exclude=*.txt --quiet --root=chrome/browser {}".format(script, seperator.join(files)))
        out.write(res)

    #==============================================================
    # Sort through the files, and count errors:
    #==============================================================

    whitespaceCount = 0
    runtimeCount = 0
    copyrightCount = 0
    readabilityCount = 0
    includeCount = 0 

    outFile = open('style.txt', 'w')

    with open("scriptRaw.txt", 'r') as f:
        lines = f.readlines()
        for line in lines:
            # print(line)
            math = len(line) - 4
            line = line[5: math]

            #TODO
            f1 = "Can't open for reading"
            f2 = "header_guard"
            f3 = "None"
            if (f1 or f2 or f3) not in line:
                outFile.write(line)

            if "whitespace" in line:
                whitespaceCount=+1
                
            if "legal" in line:
                copyrightCount=+1

            if "runtime" in line:
                runtimeCount=+1
                
            if "readability" in line:
                readabilityCount=+1
                
            if "include" in line:
                includeCount=+1 

    #==============================================================
    # Calculate score:
    # TODO: configure includeCount to work
    #==============================================================
    totalErrors = runtimeCount + copyrightCount + whitespaceCount + readabilityCount + includeCount
    maxScore = 10

    actualScore =  maxScore - totalErrors

    if (totalErrors > 10):
        actualScore = 0

    #=============================================================
    # Generate a readable report:
    #=============================================================
    # open my $f, '<', 'scriptRaw.txt';
    outFile2Name = "styleSummary.txt"
    outFile2 = open( '{}/'.format(resultDir) + outFile2Name, "w")
    outFile2.write("\n")
    outFile2.write("Total files processed:\t\t\t {}".format(fileCount))
    outFile2.write("-------- \n")
    outFile2.write("Whitespace or parenthesis errors: \t {} \n".format(whitespaceCount))
    outFile2.write("Readability Errors \t \t {} \n".format(readabilityCount))
    outFile2.write("Copyright or legal errors: \t\t {} \n".format(copyrightCount))
    outFile2.write("Runtime or explicit errors: \t\t {} \n\n".format(runtimeCount))
    outFile2.write("Include errors: \t\t {} \n\n".format(includeCount))
    outFile2.write("Total Errors \t\t\t\t{}\n".format(totalErrors))
    outFile2.write("Score:\t\t\t\t\t {}".format(actualScore))

    #=============================================================
    # Clean up:
    #=============================================================
    outFile2.close()
    outFile2 = open('{}/'.format(resultDir) + outFile2Name, "r")
    WebCat.addReport(config, outFile2Name, 'Style Report', outFile2.read())
    outFile2.close()


    os.system("mv style.txt {}/".format(resultDir))
    os.system("mv scriptRaw.txt {}/".format(resultDir))
    # os.system("rm -R temp/ && rm {}/1-stdout.txt".format(resultDir))
    ## (`rm -R temp/ && rm scriptRaw.txt && rm $resultDir/1-stdout.txt`);
    ##-------------------------------------------------------------
    
    print('Style Score: ' + str(actualScore))

    return actualScore
    #--------------------------------------------------------------
