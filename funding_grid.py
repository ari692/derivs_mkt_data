import json
from laevitas_api import read_json_file, get_funding_for_ccy

exchange_list = ['BINANCE', 'KRAKEN' 'OKX', 'DERIBIT', 'BYBIT']
symbol_list = {
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
    }
}

config = read_json_file('config.json')

for symbol in symbol_list.keys():
    print(symbol)
    result = get_funding_for_ccy(config['laevitas-api-key'], symbol_list[symbol]['ccy'])
    if result['success']:
        filter_funding_results

# result = get_funding_for_ccy(config['laevitas-api-key'], 'BTC')
# print(json.dumps(result, indent=2))

