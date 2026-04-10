import json

from laevitas_api import (
    get_options_snapshot,
    get_options_term_structure_atm,
    get_vol_smile_by_type,
    read_json_file,
)

config = read_json_file("config.json")

# result = get_vol_smile_by_type(
#     config["laevitas-api-key"], "deribit", "btc", "26DEC25", "c"
# )
# result = result["data"]["data"]
# print(json.dumps(result, indent=2))

# result = get_options_snapshot(config["laevitas-api-key"], "deribit", "btc")
# result = result["data"]["data"]
# print(json.dumps(result, indent=2))
# print(f"num entries: {len(result)}")

result = get_options_term_structure_atm(config["laevitas-api-key"], "btc")
result = result["data"]["data"]
print(json.dumps(result, indent=2))
print(f"num entries: {len(result)}")
