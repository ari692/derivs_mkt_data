''' funding_grid.py 
    goal is to output a grid of funding rates set up with symbols on one axis
    and venue on the other
'''
import json
import pandas as pd
from laevitas_api import read_json_file, get_funding_for_ccy, get_perp_data_for_venue

exchange_list = ['BINANCE', 'KRAKEN', 'OKX', 'DERIBIT', 'BYBIT']
symbol_map = {
    'BTC-INVERSE': {
        'ccy': 'BTC',
        'map': {
            'BINANCE': 'BTCUSD_PERP',
            'KRAKEN': 'PI_XBTUSD',
            'DERIBIT': 'BTC-PERPETUAL',
            'OKX': 'BTC-USD-SWAP',
            'BYBIT': 'BTCUSD'
        }
    },
    'ETH-INVERSE': {
        'ccy': 'ETH',
        'map': {
            'BINANCE': 'ETHUSD_PERP',
            'KRAKEN': 'PI_ETHUSD',
            'DERIBIT': 'ETH-PERPETUAL',
            'OKX': 'ETH-USD-SWAP',
            'BYBIT': 'ETHUSD'
        }
    },
    'AVAX-USDT': {
        'ccy': 'AVAX',
        'map': {
            'BINANCE': 'AVAXUSDT',
            'OKX': 'AVAX-USDT-SWAP',
            'BYBIT': 'AVAXUSDT'
        }
    }
}

def filter_funding_results(api_results, symbol):
    ''' takes results from laevitas api and uses the symbol map to grab the
        relevant results since the api returns everything all at once
    '''
    data_dict = {}
    for entry in api_results:
        if entry['market'] in symbol_map[symbol]['map'].keys():
            # then this is an exchange/market we care about
            if entry['symbol'] == symbol_map[symbol]['map'][entry['market']]:
                # then this is what we care about
                data_dict[entry['market']] = entry['yield']
    return data_dict

def main():
    ''' main control function '''
    config = read_json_file('config.json')
    grid_data = {}
    # for symbol, symbol_entry in symbol_map.items():
    #     result = get_funding_for_ccy(config['laevitas-api-key'], symbol_entry['ccy'])
    #     if result['success']:
    #         data = result['data']['data']
    #         grid_data[symbol] = filter_funding_results(data, symbol)
    # print(json.dumps(grid_data, indent=2))
    # print('\n')
    # df = pd.DataFrame.from_dict(grid_data, orient='index')
    # print(df)
    print('\n*******\n')
    result = get_perp_data_for_venue(config['laevitas-api-key'], 'Deribit')
    if result['success']:
        print(json.dumps(result['data'], indent=2))
    else:
        print('fail')

if __name__ == "__main__":
    main()
