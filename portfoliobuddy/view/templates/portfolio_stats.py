
ASSET_CONCENTRATION_TEMPLATE = '''
Asset Concentration{% if liquid_only == True %} Liquid{% endif %}:

{% for ticker, concentration in ticker_concentrations %} {{ ticker }}\t\t{{ '{:.1%}'.format(concentration) }}
{% endfor %}
'''
