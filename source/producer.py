# producer
from quixstreams import Application
import time
from connect_api import get_data_from_api

def main():
    app = Application(broker_address="localhost:9092", consumer_group="coin_group")
    coins_topic = app.topic(name="coins", value_serializer="json")

    with app.get_producer() as producer:
        while True:
            coin_latest = get_data_from_api("XRP")

            kafka_message = coins_topic.serialize(
                key=coin_latest["symbol"], value=coin_latest
            )

            print(
                f"produce event with key = {kafka_message.key}, price = {coin_latest['quote']['USD']['price']}"
                f"volume_24h = {coin_latest['quote']['USD']['volume_24h']},"
                f"market_cap = {coin_latest['quote']['USD']['market_cap']},"
                f"percent_change_1h = {coin_latest['quote']['USD']['percent_change_1h']},"
                f"percent_change_24h = {coin_latest['quote']['USD']['percent_change_24h']},"
                f"percent_change_7d = {coin_latest['quote']['USD']['percent_change_7d']}"   
            )

            producer.produce(
                topic=coins_topic.name, key=kafka_message.key, value=kafka_message.value
            )

            time.sleep(30)


if __name__ == "__main__":
    main()