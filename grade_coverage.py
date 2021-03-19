import json

def gradeCoverage(filepath, functions, instantiations, lines, regions):
    data_file = open(filepath, 'r')
    data = data_file.read()
    data_file.read()

    x = json.loads(data)
    
    template_count = x['data'][0]['totals']['instantiations']['count'] / x['data'][0]['totals']['functions']['count']
    
    if functions and x['data'][0]['totals']['functions']['percent'] != 100:
        return [False, template_count]
    
    if instantiations and x['data'][0]['totals']['instantiations']['percent'] != 100:
        return [False, template_count]
    
    if lines and x['data'][0]['totals']['lines']['percent'] != 100:
        return [False, template_count]
    
    if regions and x['data'][0]['totals']['regions']['percent'] != 100:
        return [False, template_count]

    return [True, template_count]