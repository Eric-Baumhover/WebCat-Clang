import os, sys, subprocess

def importConfig(config_file_name):

    try:
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

def exportConfig(config_file_name, config_data):
    try:
        config_export = open(config_file_name, 'w')

        lines = []

        for key in config_data.keys():
            lines += [str(key) + "=" + str(config_data[key]) + "\n"]

        lines.sort()

        for line in lines:
            config_export.write(line)

    except FileNotFoundError:
        print("Export Config error: ", str(sys.exc_info()))

def addReport(config, report_file_name, title, data):
    result_dir = config['resultDir']
    file_data = open(result_dir + '/' + report_file_name, 'w')

    file_data.write('<div class="shadow"><table><tbody><tr><th>' + title + '</th></tr><tr><td>')

    file_data.write('<div style="overflow: scroll; max-width: 60vw; max-height: 25vw;">')
    
    for line in data.split('\n'):
        file_data.write('<pre style="display: inline; margine: 0;">' + line + '<br></pre>')

    file_data.write('</div>')

    file_data.write('</td></tr></tbody></table></div><div class="spacer">&nbsp;</div>')

    file_data.close()

    addExistingReport(config, report_file_name)

def addExistingReport(config, report_file_name):
    reportNum = config['numReports'] + 1
    config['numReports'] = reportNum
    report = 'report' + str(reportNum)
    config[report + '.file'] = report_file_name
    config[report + '.mimeType'] = 'text/html'

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