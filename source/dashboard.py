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
from volume_prefixes import format_numbers
import requests
from connect_api_exchangerate import get_exchange_rates




connection_string = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DBNAME}"

count = st_autorefresh(interval=10 * 1000, limit=100, key="data_refresh")

engine = create_engine(connection_string)


def load_data(query):
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
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
            percent_change_24h,
            LAG(price_sek) OVER (ORDER BY timestamp) AS prev_price_sek,
            LAG(price_dkk) OVER (ORDER BY timestamp) AS prev_price_dkk,
            LAG(price_nok) OVER (ORDER BY timestamp) AS prev_price_nok,
            LAG(price_isk) OVER (ORDER BY timestamp) AS prev_price_isk,
            LAG(price_eur) OVER (ORDER BY timestamp) AS prev_price_eur
        FROM "XRP";
        """
    )

    df.columns = df.columns.str.upper()

    # calculate pricechange
    df['PRICE_CHANGE_SEK'] = df['SEK'] - df['PREV_PRICE_SEK']
    df['PRICE_CHANGE_DKK'] = df['DKK'] - df['PREV_PRICE_DKK']
    df['PRICE_CHANGE_NOK'] = df['NOK'] - df['PREV_PRICE_NOK']
    df['PRICE_CHANGE_ISK'] = df['ISK'] - df['PREV_PRICE_ISK']
    df['PRICE_CHANGE_EUR'] = df['EUR'] - df['PREV_PRICE_EUR']

    df["VOLUME"] = df["VOLUME"].apply(format_numbers)

    # Remove the columns you don't want to display
    df_display = df.drop(columns=['PREV_PRICE_SEK', 'PREV_PRICE_DKK', 'PREV_PRICE_NOK', 'PREV_PRICE_ISK', 'PREV_PRICE_EUR'])



    st.markdown("# Data for the cryptocurrency XRP")

    # KPI label
    label = ("Volume (24H) in USD")
    latest_volume = df["VOLUME"].iloc[-1]
    st.metric(label=label, value=latest_volume)

    label2 = ("Percentage change 24H")
    latest_percentage = df["PERCENT_CHANGE_24H"].iloc[-1]
    st.metric(label=label2, value=latest_percentage)

    # Raw data
    st.markdown("## Latest incoming data")
    
    st.dataframe(df_display.tail(10))
    
    # selectbox options
    st.markdown("## Selection of a certain exchange or metric")

    exchange_options = [col for col in df.columns if col not in ["TIMESTAMP", "COIN", "VOLUME", "PREV_PRICE_SEK", "PREV_PRICE_DKK", "PREV_PRICE_NOK", "PREV_PRICE_ISK", "PREV_PRICE_EUR"]]
    exchange = st.selectbox("Choose your exchange or metric", exchange_options)

    # Graph
    st.markdown(f"## Graph on XRP values in {exchange.upper()}")

    price_chart = line_chart(x=df.index, y=df[exchange], title=f"{exchange.upper()}")

    st.pyplot(price_chart, bbox_inches="tight")


    # Lägg till selectbox för att välja valuta
    valuta_options = ["SEK", "DKK", "NOK", "ISK", "EUR"]
    valuta = st.selectbox("Välj valuta", valuta_options)

    # Uppdatera graferna baserat på aktuella valutakurser
    rates = get_exchange_rates()

    df["SEK"] = df["SEK"] * rates["SEK"]
    df["DKK"] = df["DKK"] * rates["DKK"]
    df["NOK"] = df["NOK"] * rates["NOK"]
    df["ISK"] = df["ISK"] * rates["ISK"]
    df["EUR"] = df["EUR"] * rates["EUR"]
                      
    # Uppdatera grafen baserat på vald valuta
    st.markdown(f"## Prisgraf för XRP i {valuta}")

    if valuta == "SEK":
        price_chart = line_chart(x=df.index, y=df["SEK"], title=f"Pris i {valuta}")
    elif valuta == "DKK":
        price_chart = line_chart(x=df.index, y=df["DKK"], title=f"Pris i {valuta}")
    elif valuta == "NOK":
        price_chart = line_chart(x=df.index, y=df["NOK"], title=f"Pris i {valuta}")
    elif valuta == "ISK":
        price_chart = line_chart(x=df.index, y=df["ISK"], title=f"Pris i {valuta}")
    elif valuta == "EUR":
        price_chart = line_chart(x=df.index, y=df["EUR"], title=f"Pris i {valuta}")

    st.pyplot(price_chart, bbox_inches="tight")


if __name__ == "__main__":
    layout()