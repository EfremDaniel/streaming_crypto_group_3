import requests
from constants import (
    EXCHANGERATE_API, 
)

URL = "https://api.exchangeratesapi.io/latest"

def get_exchange_rates():
    url = f"{URL}?access_key={EXCHANGERATE_API}"
    response = requests.get(url)
    
  #  Kontrollera om anropet lyckades
    if response.status_code == 200:
        data = response.json()
        print("API Response:", data)  
        rates = data.get("rates")
        if rates:
            return rates
        else:
            print("Rates not found in API response")
            return None
    else:
        print(f"API request failed with status code: {response.status_code}")
        print(f"Error message: {response.text}")
        return None
    
