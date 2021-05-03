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
    
    # If any of the next percentages aren't 100, fail.

    # Retrieve the percentage of functions covered.
    if functions and x['data'][0]['totals']['functions']['percent'] != 100:
        return [False, template_count]
    
    # Retrieve the percentage of instantiations (templates) covered.
    if instantiations and x['data'][0]['totals']['instantiations']['percent'] != 100:
        return [False, template_count]
    
    # Retrive the percentage of lines covered.
    if lines and x['data'][0]['totals']['lines']['percent'] != 100:
        return [False, template_count]
    
    # Retrieve the percentage of regions covered.
    if regions and x['data'][0]['totals']['regions']['percent'] != 100:
        return [False, template_count]

    # All perfect.
    return [True, template_count]