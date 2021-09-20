import os, sys, subprocess

# Gets necessary WebCAT data.
def importConfig(config_file_name):

    try:
        # Parses config file.
        config_raw      = open(config_file_name, 'r').read()
        config_pairs    = config_raw.split('\n')

        config = {}

        for pair in config_pairs:

            split = pair.split('=')

            if len(split) == 2:
                config[split[0]] = split[1]

        return config
    
    except FileNotFoundError:
        print("Import Config error: ", str(sys.exc_info()))
        return {}

# Returns data to WebCAT.
def exportConfig(config_file_name, config_data):
    try:
        # Write to config file.
        config_export = open(config_file_name, 'w')

        lines = []

        for key in config_data.keys():
            lines += [str(key) + "=" + str(config_data[key]) + "\n"]

        lines.sort()

        for line in lines:
            config_export.write(line)

    except FileNotFoundError:
        print("Export Config error: ", str(sys.exc_info()))

# Takes in a text string and wraps it in html. Outputs as a file and tells WebCAT to display it.
def addReport(config, report_file_name, title, data):

    result_dir = config['resultDir']
    file_data = open(result_dir + '/' + report_file_name, 'w')

    file_data.write('<div class="shadow"><table><tbody><tr><th>' + title + '</th></tr><tr><td>')

    file_data.write('<div style="overflow: scroll; max-width: 60vw; max-height: 25vw;">')
    
    for line in data.split('\n'):
        file_data.write('<pre style="display: inline; margine: 0;">' + line + '<br></pre>')

    file_data.write('</div>')

    file_data.write('</td></tr></tbody></table></div><div class="spacer">&#160;</div>')

    file_data.close()

    addExistingReport(config, report_file_name)

# Normally internal function for adding an html file as a report.
def addExistingReport(config, report_file_name):
    reportNum = config['numReports'] + 1
    config['numReports'] = reportNum
    report = 'report' + str(reportNum)
    config[report + '.file'] = report_file_name
    config[report + '.mimeType'] = 'text/html'

# Useful function for running a command and reporting directly to WebCAT.
def commandReport(command, config, report_file_name_prefix, title_prefix, combine=False, debug=False):

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr= subprocess.STDOUT if combine else subprocess.PIPE, universal_newlines=True)
    process.wait()
    # Get the return code and logs.
    code = process.returncode
    log, error = process.communicate()

    if not (debug and not config.get('debugReports','false') != 'false'):
        addReport(config, report_file_name_prefix if combine else report_file_name_prefix + '_log', title_prefix if combine else report_file_name_prefix + ' Log', log)
        if not combine:
            addReport(config, report_file_name_prefix + '_error', title_prefix + ' Error', error)
    else:
        print(log)
        if not combine:
            print(error)
    return code

def addMarkup(config, file_name, text):
    html = '<table cellspacing="0" cellpadding="0" class="srcView" bgcolor="white" id="bigtab"><tbody id="tab">'
    split = text.split('\n')
    lineNum = 1
    for line in split:
        num = str(lineNum)
        line = line.replace('&', '&amp;').replace('"', '&quot;').replace("'", '&apos;').replace('<', '&lt;').replace('>', '&gt;')
        html += '<tr id="O:' + num + '"><td align="right" class="lineCount" id="O:' + num + '">&#160;' + num + '</td><td align="right" class="coverageCount" id="O:' + num + '">&#160;&#160;</td><td class="srcLine" id="O:' + num + '"><pre class="srcLine" id="O:' + num + '">&#160;' + line + '</pre></td></tr>'
        lineNum += 1
    html += '</tbody></table>'
    with open("{}/html/{}.html".format(config['resultDir'], file_name), 'w') as file_data:
        file_data.write(html)

    #Format is not valid yet. Cannot be an actual Markup

    #markupNum = config['numCodeMarkups'] + 1
    #config['numCodeMarkups'] = markupNum
    #name = 'codeMarkup' + str(markupNum)
    #config[name + '.sourceFileName'] = file_name
    #config[name + '.markupFileName'] = "html/{}.html".format(file_name)