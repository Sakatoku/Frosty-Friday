import streamlit as st
import snowflake.connector
import pandas as pd

# Connect to Snowflake
@st.cache_resource(ttl=7200)
def connect_snowflake() -> snowflake.connector.cursor:
    conn = snowflake.connector.connect(
        user=st.secrets["Snowflake"]["user"],
        password=st.secrets["Snowflake"]["password"],
        account=st.secrets["Snowflake"]["account"],
        session_parameters={
            'QUERY_TAG': 'Frosty Friday',
        }
    )
    cursor = conn.cursor()
    return cursor

# Fetch data from Snowflake
@st.cache_data
def fetch_data(_cursor: snowflake.connector.cursor) -> pd.DataFrame:
    cursor = connect_snowflake()
    sql_query = """
        select
            date_trunc('week', to_date(payment_date)) as payment_date,
            sum(amount_spent) as amount_spent
        from frostyfriday_db.public.week8_tbl
        group by 1
        """
    query_result = cursor.execute(sql_query).fetchall()
    df = pd.DataFrame(query_result, columns=[column.name for column in cursor.description])
    return df

# Filter data
def filter_data(df: pd.DataFrame) -> pd.DataFrame:
    # min and max datetime
    min_date = df['PAYMENT_DATE'].min()
    max_date = df['PAYMENT_DATE'].max()

    # Create slider
    selected_dates = st.slider("Select min date and max date", min_value=min_date, max_value=max_date, value=(min_date, max_date))

    # Filter data
    date_mask1 = selected_dates[0] < df['PAYMENT_DATE']
    date_mask2 = df['PAYMENT_DATE'] <= selected_dates[1]
    df_filtered = df[date_mask1 & date_mask2]
    return df_filtered

# Main function
def main():
    # Title
    st.title("Payments in 2021")

    # Fetch and filter data from Snowflake
    cursor = connect_snowflake()
    df = fetch_data(cursor)
    df_filtered = filter_data(df)

    # Show chart
    st.line_chart(df_filtered, x='PAYMENT_DATE', y='AMOUNT_SPENT')

if __name__ == "__main__":
    main()