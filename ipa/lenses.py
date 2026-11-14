"""Management lenses: priority tiers (1.0 / 0.6 / 0.2) and the rule behind each one."""
ANNEX9_MEASURED = ['nitrato', 'nitrito', 'ba', 'cd', 'pb', 'cu', 'cr', 'ni']
P23 = ['amonia', 'nitrito', 'nitrato', 'dureza', 'cloreto', 'cor', 'pH', 'SDT', 'sulfato', 'turbidez', 'ct', 'ec',
       'al', 'ba', 'cd', 'pb', 'cu', 'cr', 'fe', 'mn', 'ni', 'na', 'zn']
LENSES = {
    # regulatory risk class: E. coli and Annex 9 substances on top
    'health': {1.0: ['ec'] + ANNEX9_MEASURED, 0.6: ['ct', 'al', 'mn', 'amonia', 'turbidez'],
               0.2: ['dureza', 'cloreto', 'sulfato', 'SDT', 'cor', 'fe', 'na', 'zn', 'pH']},
    # indicators of sewage contamination on top
    'sanitation': {1.0: ['ec', 'ct', 'amonia', 'nitrato', 'nitrito'], 0.6: ['turbidez', 'cloreto', 'cor', 'SDT'],
                   0.2: ['al', 'ba', 'cd', 'pb', 'cu', 'cr', 'fe', 'mn', 'ni', 'na', 'zn', 'dureza', 'sulfato', 'pH']},
    # treatment complexity: adsorption / ion exchange / reverse osmosis on top; disinfection or pH correction at the bottom
    'treatability': {1.0: ['pb', 'cd', 'cr', 'ni', 'ba', 'cu', 'nitrato', 'nitrito', 'SDT', 'cloreto', 'na', 'dureza', 'sulfato', 'zn'],
                     0.6: ['fe', 'mn', 'al', 'turbidez', 'cor', 'amonia', 'ec'], 0.2: ['pH', 'ct']},
    'compliance': {1.0: P23},
}
EXPERTS = {'pH': 0.4, 'turbidez': 0.7, 'cor': 0.6, 'cloreto': 0.3, 'sulfato': 0.3, 'al': 0.9, 'amonia': 0.8, 'nitrito': 0.85,
           'nitrato': 0.75, 'SDT': 0.4, 'dureza': 0.4, 'fe': 0.5, 'mn': 0.6, 'zn': 0.4, 'na': 0.5, 'cu': 0.7, 'cr': 0.8,
           'ni': 0.8, 'cd': 1.0, 'pb': 1.0, 'ba': 0.7, 'ct': 0.9, 'ec': 1.0}
ECOLI_DOMINANT = {'health': True, 'sanitation': True, 'experts': True, 'treatability': False, 'compliance': False}
