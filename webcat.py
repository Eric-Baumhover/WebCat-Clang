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

    max_length = 75

    for line in data.split('\n'):
        length = len(line)
        more = False
        while True:
            file_data.write('<pre>' + line[0:(length if length <= max_length else max_length)] + '</pre>')
            if length > max_length:
                line = line[max_length:]
                length -= max_length
                more = True
            else:
                if more:
                    file_data.write('<br>')
                break

    file_data.write('</td></tr></tbody></table></div><div class="spacer">&nbsp;</div>')

    file_data.close()

    reportNum = config['numReports'] + 1
    config['numReports'] = reportNum
    report = 'report' + str(reportNum)
    config[report + '.file'] = report_file_name
    config[report + '.mimeType'] = 'text/html'