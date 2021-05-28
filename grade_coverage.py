import json

# Uses json parsing to grade code coverage data exported by llvm-cov.
def gradeCoverage(filepath, functions, instantiations, lines, regions):
    # Open file.
    data_file = open(filepath, 'r')
    data = data_file.read()
    data_file.read()

    # Json dictionary. Name kept simple because it is used a lot.
    x = json.loads(data)
    
    # Template use data.
    # Rough estimate number.
    template_count = x['data'][0]['totals']['instantiations']['count'] / x['data'][0]['totals']['functions']['count']
    

    total = 0
    counted = 0

    # Retrieve the percentage of functions covered.
    if functions:
        total   += x['data'][0]['totals']['functions']['percent']
        counted += 1
    
    # Retrieve the percentage of instantiations (templates) covered.
    if instantiations:
        total   += x['data'][0]['totals']['instantiations']['percent']
        counted += 1
    
    # Retrive the percentage of lines covered.
    if lines:
        total   += x['data'][0]['totals']['lines']['percent']
        counted += 1
    
    # Retrieve the percentage of regions covered.
    if regions:
        total   += x['data'][0]['totals']['regions']['percent']
        counted += 1

    # All perfect.
    return [float(total) / counted, template_count]