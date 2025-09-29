import requests
import json

ROOT_URL = 'https://api.laevitas.ch'

def read_json_file(file_name):
    ''' simply read a simple json file and return a dict '''
    with open(file_name, 'r') as file:
        data = json.load(file)
    return data

def get_funding_for_ccy(api_key, ccy):
    ''' get all funding rates from laevitas for a given currency
        
    '''
    url = f'{ROOT_URL}/analytics/futures/perpetual_funding/{ccy.upper()}'
    print(ROOT_URL)
    headers = {
        'apikey': api_key,
    }
    try:
        response = requests.get(url, headers=headers)
        result = response.json()
    except err as Exception:
        return {
            'success': False,
            'error': err
        }
    return {
        'success': True,
        'data': result
    }

# config = read_json_file('config.json')

# headers = {
#     'apikey': config['laevitas-api-key'],
# }
# url = ROOT_URL + '/analytics/futures/instruments'
# url = ROOT_URL + '/analytics/futures/futures_curve/BTC'


# result = get_funding_for_ccy(config['laevitas-api-key'], 'BTC')
# print(json.dumps(result, indent=2))
