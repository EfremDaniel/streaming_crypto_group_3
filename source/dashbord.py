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
                SELECT timestamp, coin, price_sek AS SEK, price_dkk AS DKK, price_nok AS NOK, price_isk AS ISK, price_eur AS EUR, volume FROM "XRP";
                """
    )

    df.columns = df.columns.str.upper()

    st.markdown("# Data for the cryptocurrency XRP")

    st.markdown("## Latest incoming data")
    
    st.dataframe(df.tail(10))
    
    st.markdown("## Select a certain exchange")

    exchange_options = [col for col in df.columns if col not in ["timestamp", "COIN"]]

    exchange = st.selectbox("Choose your exchange", exchange_options)

    st.markdown(f"## Graph on XRP latest price in {exchange.upper()}")

    price_chart = line_chart(x=df.index, y=df[exchange], title=f"Price in {exchange.upper()}")

    st.pyplot(price_chart, bbox_inches="tight")

if __name__ == "__main__":
    layout()