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

    # Importing function from python script volume_prefixes
    df["VOLUME"] = df["VOLUME"].apply(format_numbers)

    st.markdown("# Data for the cryptocurrency XRP")
    st.markdown("Explore a comprehensive view of XRP, one of the leading cryptocurrencies reshaping the global financial landscape. This dashboard is designed to provide you with comprehensive insights and real-time data. This will give understanding over the landscape of cryptocurrency where it will help you to make informed decisions. empowering you to make informed decisions in the ever-evolving landscape of cryptocurrency. ")     
    st.markdown("#### Data and statistics for XRP")
    st.markdown("##### KPIs for volumes in XRP (USD)")
    st.markdown("The KPIs here gives a overview regarding the volume and the changes that happens live. Volume refers to the total amount of the cryptocurrency that has been traded within a specific time period. This usually includes both buying and selling activities. ")


    # KPI label
    label = ("Volume (24H)").upper()
    latest_volume = df["VOLUME"].iloc[-1]
    st.metric(label=label, value=latest_volume)

    label2 = ("Percentage change in the last 24H").upper()
    latest_percentage = df["PERCENT_CHANGE_24H"].iloc[-1]
    decimal_2 = f"{latest_percentage:.2f}"
    st.metric(label=label2, value=decimal_2)

    # Markdowns for the raw data
    st.markdown("## Latest incoming data")
    st.markdown("This table provides an overview of the value of XRP. The value of XRP, like other cryptocurrencies, is subject to market fluctuations and can change rapidly in response to various economic factors and news. The data presented here reflects its market price at specific points in time")
    
    # Raw data
    st.dataframe(df.tail(10))
    
    # selectbox options to choose exchange value for the graph
    st.markdown("## Selection of a certain exchange or metric")
    exchange_options = [col for col in df.columns if col not in ["TIMESTAMP", "COIN", "VOLUME", "PERCENT_CHANGE_24H", "PREV_PRICE_SEK", "PREV_PRICE_DKK", "PREV_PRICE_NOK", "PREV_PRICE_ISK", "PREV_PRICE_EUR"]]
    exchange = st.selectbox("Choose your exchange or metric", exchange_options)

    # Graph
    st.markdown(f"## Graph on XRP values in {exchange.upper()}")

    price_chart = line_chart(x=df.index, y=df[exchange], title=f"{exchange.upper()}")

    st.pyplot(price_chart, bbox_inches="tight")

    st.markdown("#### About XRP")
    st.markdown("XRP is a digital asset and cryptocurrency created by Ripple Labs. It is used to facilitate fast and cost-effective international money transfers and payments")
    st.markdown("#### Disclaimer")
    st.markdown("This dashboard is for informational purposes only and should not be considered financial advice. Always conduct your own research before making investment decisions.")
   

if __name__ == "__main__":
    layout()