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

def print_data_report(raw_data: list, processed_data: list, price_key: str, floorplan_key: str) -> None:
    price_errors = 0
    records_wo_floorplan = 0
    seen_floorplans = set()
    
    for dict in processed_data:
        # Convert the price to Decimal
        if dict[price_key] is None:
            price_errors += 1
        try:
            if dict[floorplan_key] is not None:
                seen_floorplans.add(dict[floorplan_key])
            else:
                records_wo_floorplan += 1
        except KeyError:
            records_wo_floorplan += 1
    
    print('=======Data quality report=======')
    print('Number of scraped offerings:', len(raw_data))
    print('Number of duplicates:', len(raw_data) - len(processed_data))
    print('Number of observations with nonnumeric price:', price_errors)
    print('The dispositions encountered:', seen_floorplans)
    print('Records without disposition:', records_wo_floorplan)
    
    return None
    
