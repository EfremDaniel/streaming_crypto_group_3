# consumer
from quixstreams import Application

from quixstreams import Application
from quixstreams.sinks.community.postgresql import PostgreSQLSink
from constants import (
    POSTGRES_DBNAME,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_USER,
)

from quixstreams.sinks.community.postgresql import PostgreSQLSink


def extract_coin_data(message):
    latest_quote = message["quote"]["USD"]
    price_usd = latest_quote["price"]
    price_sek = update_price_in_currency(price_usd, "SEK")
    price_dkk = update_price_in_currency(price_usd, "DKK")
    price_nok = update_price_in_currency(price_usd, "NOK")
    price_isk = update_price_in_currency(price_usd, "ISK")
    price_eur = update_price_in_currency(price_usd, "EUR")
    
    return {
        "coin": message["name"],
        "price_sek": price_sek,
        "price_dkk": price_dkk,
        "price_nok": price_nok,
        "price_isk": price_isk,
        "price_eur": price_eur,
        "volume": latest_quote["volume_24h"],
        "updated": message["last_updated"],
    }



# exchange by hardcoding
def get_exchange_rate_hardcoded(target_currency):
    exchange_rates = {
        "SEK": 10.7,    
        "DKK": 7.1,    
        "NOK": 11.2,    
        "ISK": 140.0,
        "EUR": 0.95   
    }
    
    if target_currency in exchange_rates:
        return exchange_rates[target_currency]
    else:
        print(f"Currency {target_currency} not supported.")
        return None

def update_price_in_currency(price_in_usd, target_currency):
    exchange_rate = get_exchange_rate_hardcoded(target_currency)
    if exchange_rate:
        return round(price_in_usd * exchange_rate, 3)
    else:
        print(f"Cannot update price, since the currency was not able to be found for {target_currency}.")
        return None
    


def create_postgres_sink():
    sink = PostgreSQLSink(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DBNAME,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        table_name="XRP",
        schema_auto_update=True,
    )

    return sink

def main():
    app = Application(
        broker_address="localhost:9092",
        consumer_group="coin_group",
        auto_offset_reset="earliest",
    )
    coins_topic = app.topic(name="coins", value_deserializer="json")

    sdf = app.dataframe(topic=coins_topic)

    # transformations
    sdf = sdf.apply(extract_coin_data)


    sdf.update(lambda coin_data: 
    print(f"Coin Data:\n"
     f"Coin: {coin_data['coin']}\n"
     f"Price in SEK: {coin_data['price_sek']:.3f}\n"
     f"Price in DKK: {coin_data['price_dkk']:.3f}\n"
     f"Price in NOK: {coin_data['price_nok']:.3f}\n"
     f"Price in ISK: {coin_data['price_isk']:.3f}\n"
     f"Price in EUR: {coin_data['price_eur']:.3f}\n"
     f"Volume: {coin_data['volume']:.3f}\n"
     f"Updated: {coin_data['updated']}"))
    

    # sink to postgres
    postgres_sink = create_postgres_sink()
    sdf.sink(postgres_sink)

    app.run()

if __name__ == "__main__":
    main()