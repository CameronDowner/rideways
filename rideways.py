from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import requests
import argparse
import sys

CAR_SIZES = {
    'STANDARD': 4,
    'EXECUTIVE': 4,
    'LUXURY': 4,
    'PEOPLE_CARRIER': 6,
    'LUXURY_PEOPLE_CARRIER': 6,
    'MINIBUS': 16
}

def get_car_size(car):
    return CAR_SIZES[car]

BASE_URL = 'https://techtest.rideways.com/'
DAVE_URL = 'https://techtest.rideways.com/dave'
ERIC_URL = 'https://techtest.rideways.com/eric'
JEFF_URL = 'https://techtest.rideways.com/jeff'

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("pickup", type=str)
    parser.add_argument("dropoff", type=str)
    parser.add_argument("passengers", type=int)
    return parser.parse_args()

def fetch_options(pickup, dropoff):
    errors = 0
    try:
        dave_options = fetch_options_for(DAVE_URL, pickup, dropoff)
    except:
        dave_options = []
        errors += 1
    
    try:
        eric_options = fetch_options_for(ERIC_URL, pickup, dropoff)
    except:
        eric_options = []
        errors += 1

    try:
        jeff_options = fetch_options_for(JEFF_URL, pickup, dropoff)
    except:
        jeff_options = []
        errors += 1
    
    if errors is 3:
        print('An error has occurred. Please try again later.')
        sys.exit(1)
    
    return dave_options + eric_options + jeff_options

def fetch_options_for(url, pickup, dropoff):
    response = send_request(url, pickup, dropoff)
    options = response['options']
    for option in options:
        option['supplier'] = response['supplier_id']
    return options

def send_request(url, pickup, dropoff):
    query_params = {'pickup': pickup, 'dropoff': dropoff}
    r = requests.get(url, params=query_params, timeout=2)

    if r.status_code is not 200:
        raise Error()

    return r.json()

def display_results(options):
    if not options:
        print('No options available.')
        return
    
    for option in options:
        car_type = option['car_type']
        supplier = option['supplier']
        price = option['price']
        print('{} - {} - {}'.format(car_type, supplier, price))

def is_valid_option(option, passengers):
    return get_car_size(option['car_type']) >= passengers

def price(option):
    return option['price']

def filter_options(options, passengers):
    valid_car_types = []
    for car_type, size in CAR_SIZES.items():
        if size >= passengers:
            valid_car_types.append(car_type)
    
    results = []
    for car_type in valid_car_types:
        cars_of_type = [x for x in options if x['car_type'] == car_type]
        if not cars_of_type:
            continue
        min_price_car = min(cars_of_type, key=price)
        results.append(min_price_car)

    return results

def main():
    args = parse_args()
    pickup = args.pickup
    dropoff = args.dropoff

    options = fetch_options(pickup, dropoff)
    filtered_options = filter_options(options, args.passengers)
    
    display_results(filtered_options)

if __name__ == '__main__':
    main()
