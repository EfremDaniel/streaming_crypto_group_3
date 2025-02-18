import streamlit as st
from streamlit_autorefresh import st_autorefresh
from sqlalchemy import create_engine
import pandas as pd
from constants import (
    POSTGRES_USER,
    POSTGRES_DBNAME,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
)

from charts import line_chart


connection_string = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DBNAME}"

count = st_autorefresh(interval=10 * 1000, limit=100, key="data_refresh")

engine = create_engine(connection_string)


def load_data(query):
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
        # print(df)
        df = df.set_index("timestamp")
    return df

# create a function that makes it able to change graph and name based on selectbox

def layout():
    df = load_data(
        """
        SELECT timestamp, coin, 
            price_sek AS SEK, 
            price_dkk AS DKK, 
            price_nok AS NOK, 
            price_isk AS ISK, 
            price_eur AS EUR, 
            volume,
            LAG(volume) OVER (ORDER BY timestamp) AS prev_volume,
            LAG(price_sek) OVER (ORDER BY timestamp) AS prev_price_sek,
            LAG(price_dkk) OVER (ORDER BY timestamp) AS prev_price_dkk,
            LAG(price_nok) OVER (ORDER BY timestamp) AS prev_price_nok,
            LAG(price_isk) OVER (ORDER BY timestamp) AS prev_price_isk,
            LAG(price_eur) OVER (ORDER BY timestamp) AS prev_price_eur
        FROM "XRP";
        """
    )



    df.columns = df.columns.str.upper()

    # calculate volumechange and pricechange
    df['VOLUME_CHANGE'] = df['VOLUME'] - df['PREV_VOLUME']
    df['PRICE_CHANGE_SEK'] = df['SEK'] - df['PREV_PRICE_SEK']
    df['PRICE_CHANGE_DKK'] = df['DKK'] - df['PREV_PRICE_DKK']
    df['PRICE_CHANGE_NOK'] = df['NOK'] - df['PREV_PRICE_NOK']
    df['PRICE_CHANGE_ISK'] = df['ISK'] - df['PREV_PRICE_ISK']
    df['PRICE_CHANGE_EUR'] = df['EUR'] - df['PREV_PRICE_EUR']

    st.markdown("# Data for the cryptocurrency XRP")

    st.markdown("## Latest incoming data")
    
    st.dataframe(df.tail(10))
    
    st.markdown("## Select a certain exchange")


   # selectbox options

    exchange_options = [col for col in df.columns if col not in ["TIMESTAMP", "COIN", "PREV_VOLUME", "PREV_PRICE_SEK", "PREV_PRICE_DKK", "PREV_PRICE_NOK", "PREV_PRICE_ISK", "PREV_PRICE_EUR"]]
    exchange = st.selectbox("Choose your exchange or metric", exchange_options)

    st.markdown(f"## Graph on XRP latest price in {exchange.upper()}")

    price_chart = line_chart(x=df.index, y=df[exchange], title=f"Price in {exchange.upper()}")

    st.pyplot(price_chart, bbox_inches="tight")


if __name__ == "__main__":
    layout()