import json
import pickle
import decimal
import re

def load_config(path: str) -> dict:
    with open(file=path, mode='r') as f:
        config_dict = json.load(f)
    return config_dict

def save_list(list_to_save: list, path: str) -> None:
    with open(path, mode='wb') as raw_file:
        pickle.dump(list_to_save, raw_file)
    return None

def print_data_report(data: list, price_key: str, floorplan_key: str) -> None:
    price_errors = 0
    records_wo_floorplan = 0
    seen_floorplans = set()
    
    data_no_duplicates = [dict(t) for t in {tuple(sorted(d.items())) for d in data}]
    for dict in data_no_duplicates:
        # Convert the price to Decimal
        try:
            decimal.Decimal(re.sub(r'[^\d]', '', dict[price_key]))
        except decimal.InvalidOperation:
            price_errors += 1
        try:
            seen_floorplans.add(dict[floorplan_key])
        except KeyError:
            records_wo_floorplan += 1
    
    print('=======Data quality report=======')
    print('Number of scraped offerings:', len(data))
    print('Number of duplicates:', len(data) - len(data_no_duplicates))
    print('Number of observations with nonnumeric price:', price_errors)
    print('The dispositions encountered:', seen_floorplans)
    print('Records without disposition:', records_wo_floorplan)
    
    return None
    
