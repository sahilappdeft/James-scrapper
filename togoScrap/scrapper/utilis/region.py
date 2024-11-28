import requests

from pycountry_convert import country_alpha2_to_continent_code, country_name_to_country_alpha2

def get_continent(country):
    def get_continent_by_country(country_name):
        try:
            # Convert country name to alpha-2 code
            country_alpha2 = country_name_to_country_alpha2(country_name)
            # Convert alpha-2 code to continent code
            continent_code = country_alpha2_to_continent_code(country_alpha2)
            # Map continent codes to continent names
            continent_names = {
                "AF": "Africa",
                "AS": "Asia",
                "EU": "Europe",
                "NA": "North America",
                "SA": "South America",
                "OC": "Oceania",
                "AN": "Antarctica",
            }
            return continent_names.get(continent_code, "Unknown")
        except Exception as e:
            return str(e)

    def get_country_by_city(city_name):
        username = "sahilappdeft"  # Replace with your GeoNames username
        url = f"http://api.geonames.org/searchJSON?q={city_name}&username={username}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['geonames']:
                return data['geonames'][0]['countryName']
            else:
                return "City not found"
        print(response.json())
        return "Error: Unable to fetch data"

    country_name = (get_country_by_city(country))

    return get_continent_by_country(country_name)