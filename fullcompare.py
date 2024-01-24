# %%
# %pip install pandas
# %pip install requests
# %pip install osm2geojson
# %pip install geopandas

# %%
import argparse
import json
from pprint import pprint
from typing import Dict

import requests

NOMINATIM_API_URL = "https://nominatim.openstreetmap.org"
NOMINATIM_DETAILS_ENDPOINT = f"{NOMINATIM_API_URL}/details"
NOMINATIM_SEARCH_ENDPOINT = f"{NOMINATIM_API_URL}/search"
NOMINATIM_REVERSE_ENDPOINT = f"{NOMINATIM_API_URL}/reverse"

# query_params = {
#     "namedetails": 1,
#     "polygon_geojson": 1,
#     "hierarchy": 1,
# }

query_params = {
    "namedetails": 1,
    "hierarchy": 1,
}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", type=str, choices=["details", "reverse", "search"])
    return parser.parse_args()


def fetch_osm_details(osm_id: str, osm_type: str, params: Dict[str, int]) -> dict:
    params_query = "&".join(f"{param_name}={param_value}" for param_name, param_value in params.items())
    request_url = f"{NOMINATIM_DETAILS_ENDPOINT}?osmtype={osm_type}&osmid={osm_id}&{params_query}&format=json"
    print(request_url)
    response = requests.get(request_url)
    response.raise_for_status()
    return response.json()

def fetch_osm_search(query: str, params: Dict[str, int]) -> dict:
    params_query = "&".join(f"{param_name}={param_value}" for param_name, param_value in params.items())
    request_url = f"{NOMINATIM_SEARCH_ENDPOINT}?q={query}&{params_query}&format=json"
    print(request_url)
    response = requests.get(request_url)
    response.raise_for_status()
    return response.json()

def search_for_city_by_zip(zip_code: str) -> dict:
    request_url = f"{NOMINATIM_SEARCH_ENDPOINT}?country=usa&postalcode={zip_code}&format=json"
    print(request_url)
    response = requests.get(request_url)
    response.raise_for_status()
    return response.json()


def get_population_by_city_state_country(city: str, state: str, country: str) -> dict:
    request_url = f"{NOMINATIM_SEARCH_ENDPOINT}?city={city}&state={state}&country={country}&format=json"
    print(request_url)
    response = requests.get(request_url)
    response.raise_for_status()
    result = response.json()
    result = result[0]
    return response.json()

# %%
def geocode_city_state_country(city: str, state: str, country: str) -> dict:
    request_url = f"{NOMINATIM_SEARCH_ENDPOINT}?city={city}&state={state}&country={country}&format=json"
    print(request_url)
    response = requests.get(request_url)
    response.raise_for_status()
    result = response.json()
    result = result[0]
    return result

def geocode_address(street: str, city: str, state: str) -> dict:
    request_url = f"{NOMINATIM_SEARCH_ENDPOINT}?street={street}&city={city}&state={state}&format=json"
    request_url = request_url.replace(" ", "%20")
    print(request_url)
    response = requests.get(request_url)
    response.raise_for_status()
    result = response.json()
    result = result[0]
    return result




# %%
def fetch_osm_reverse(lat: float, lon: float, params: Dict[str, int], zoom: int = 10) -> dict:
    params_query = "&".join(f"{param_name}={param_value}" for param_name, param_value in params.items())
    # request_url = f"{NOMINATIM_REVERSE_ENDPOINT}?lat={lat}&lon={lon}&zoom={zoom}&{params_query}&format=geocodejson"
    request_url = f"{NOMINATIM_REVERSE_ENDPOINT}?lat={lat}&lon={lon}&zoom={zoom}&{params_query}&format=json"
    print(request_url)
    response = requests.get(request_url)
    response.raise_for_status()
    result = response.json()
    # result = result[0]
    return result

def get_type_id_city_from_reverse_data(reverse):
    try:
        if reverse and reverse.get('osm_type') in ['relation', 'way']:
                        entity_type_char = reverse['osm_type'][0].upper()
                        city = reverse['address'].get('city', reverse['address'].get('town'))
                        if city:
                            return (entity_type_char, reverse['osm_id'], city)
    except:
        print('no city found')
    return None




# %%

def create_overpass_query(osm_id: str, osm_type: str):
    if osm_type not in ['R', 'W']:
        raise ValueError("Invalid osm_type. Must be 'R' or 'W'.")
    # if osm_type is R set string to relation else set string to way
    osm_type = "relation" if osm_type == 'R' else "way"
    overpass_query = f"""
    [out:json][timeout:25];
    {osm_type}({osm_id});
    (._;>;);
    out body;
    """
    print(overpass_query)
    return overpass_query


# %%
import osm2geojson
import geopandas as gpd

def get_overpass_data(query_str):
    overpass_url = "http://overpass-api.de/api/interpreter"
    response = requests.get(overpass_url, params={'data': query_str})
    data = response.json()
    geojson_data = osm2geojson.json2geojson(data)
    return geojson_data


result = geocode_address(street="19 Richard ln", city="bloomfield", state="ct")
latlon = (result['lat'], result['lon'])
pprint(latlon)
reverse = fetch_osm_reverse(lat=latlon[0], lon=latlon[1], params=query_params)

type_id_city = get_type_id_city_from_reverse_data(reverse)
print(type_id_city)

query_str = create_overpass_query(osm_id=type_id_city[1], osm_type=type_id_city[0])
geojson_data = get_overpass_data(query_str)
# print(geojson_data)

gdf = gpd.GeoDataFrame.from_features(geojson_data['features'])



# result = geocode_address(street="30 Maujer st", city="Brooklyn", state="NY")
# result = geocode_address(street="1228 fairmont st", city="washington", state="dc")




# find the city name given that zip code
# find the population of that city
# determine if the population is greater than gaza's population 
# if not, store the population and find the bordering cities
# find the population of the bordering cities
# determine which combination of cities and their percentages would equal that of gazas population
# area = gdf.area[0]
# print(area)



# %%
