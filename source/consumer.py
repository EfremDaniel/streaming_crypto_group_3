# consumer
from quixstreams import Application
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
    return {
        "coin": message["name"],
        "price_usd": latest_quote["price"],
        "volume": latest_quote["volume_24h"],
        "updated": message["last_updated"],
    }


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

    sdf.update(lambda coin_data: print(coin_data))

    # sink to postgres
    postgres_sink = create_postgres_sink()
    sdf.sink(postgres_sink)

    app.run()


if __name__ == "__main__":
    main()