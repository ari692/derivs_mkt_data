import json

from massive import RESTClient

from laevitas_api import read_json_file

config = read_json_file("config.json")

client = RESTClient(api_key=config["Massive-api-key"])

ticker = "IBIT"
trade = client.get_last_trade(ticker=ticker)
print(trade)


# options_chain = []
# for o in client.list_snapshot_options_chain(
#     "IBIT",
#     params={
#         "order": "asc",
#         "limit": 10,
#         "sort": "ticker",
#     },
# ):
#     options_chain.append(o)
print("********")
# contracts = []
# for c in client.list_options_contracts(
#     underlying_ticker="IBIT",
#     order="asc",
#     limit=10,
#     sort="ticker",
# ):
#     contracts.append(c)

# print(contracts[0])
details = client.get_ticker_details(
    "IBIT",
)

print(details)

print("********\n")
balance_sheets = []
for b in client.list_financials_balance_sheets(
    limit="100",
    sort="period_end.asc",
    tickers="IBIT",
):
    balance_sheets.append(b)

print(balance_sheets)
