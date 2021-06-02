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
    with open('{}/'.format(resultDir) + "scriptRaw.txt", 'w') as out:
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

    outFile = open('{}/'.format(resultDir) + 'style.txt', 'w')

    with open('{}/'.format(resultDir) + "scriptRaw.txt", 'r') as f:
        lines = f.readlines()
        for line in lines:

            if line.find('#') == -1 or line.find('#include') != -1 or line.find('/*...*/') != -1:
                outFile.write(line)

            if "whitespace" in line:
                whitespaceCount+=1
                
            if "legal" in line:
                copyrightCount+=1

            if "runtime" in line:
                runtimeCount+=1
                
            if "readability" in line:
                readabilityCount+=1
                
            if "include" in line:
                includeCount+=1 
    
    outFile.close()

    #==============================================================
    # Calculate score:
    # TODO: configure includeCount to work
    #==============================================================
    totalErrors = runtimeCount + copyrightCount + whitespaceCount + readabilityCount + includeCount
    maxScore = 10

    if (totalErrors > maxScore):
        actualScore = 0
    else:
        actualScore =  maxScore - totalErrors       
    #=============================================================
    # Generate a readable report:
    #=============================================================
    # open my $f, '<', 'scriptRaw.txt';
    outFile2Name = "styleSummary.txt"
    outFile2 = open( '{}/'.format(resultDir) + outFile2Name, "w")
    outFile2.write("\n")
    outFile2.write("Total files processed:\t\t\t {}\n\n".format(fileCount))
    outFile2.write("Whitespace or parenthesis errors: \t {} \n".format(whitespaceCount))
    outFile2.write("Readability Errors \t\t\t {} \n".format(readabilityCount))
    outFile2.write("Copyright or legal errors: \t\t {} \n".format(copyrightCount))
    outFile2.write("Runtime or explicit errors: \t\t {} \n".format(runtimeCount))
    outFile2.write("Include errors: \t\t\t {} \n\n".format(includeCount))
    outFile2.write("Total Errors \t\t\t\t{}\n".format(totalErrors))
    outFile2.write("Score:\t\t\t\t\t {}".format(actualScore))

    #=============================================================
    # Clean up:
    #=============================================================
    outFile2.close()
    with open('{}/'.format(resultDir) + outFile2Name, "r") as f:
        WebCat.addReport(config, outFile2Name, 'Style Report', f.read())

    with open('{}/'.format(resultDir) + 'style.txt', 'r') as f:
        WebCat.addReport(config, 'styleReportRaw.txt', 'Style Data', f.read())

    # os.system("rm -R temp/ && rm {}/1-stdout.txt".format(resultDir))
    ## (`rm -R temp/ && rm scriptRaw.txt && rm $resultDir/1-stdout.txt`);
    ##-------------------------------------------------------------
    
    print('Style Score: ' + str(actualScore))

    return actualScore
    #--------------------------------------------------------------
