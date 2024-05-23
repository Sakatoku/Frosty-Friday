import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd

# Fetch data from Snowflake
@st.cache_data
def fetch_data() -> pd.DataFrame:
    # Active session
    session = get_active_session()

    # Maybe there are no way to set QUERY_TAG at SiS (2024/5/23)

    # Query
    sql_query = """
        select
            date_trunc('week', to_date(payment_date)) as payment_date,
            sum(amount_spent) as amount_spent
        from frostyfriday_db.public.week8_tbl
        group by 1
        """
    snowpark_df = session.execute(sql_query)
    df = snowpark_df.to_pandas()
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
    df = fetch_data()
    df_filtered = filter_data(df)

    # Show chart
    st.line_chart(df_filtered, x='PAYMENT_DATE', y='AMOUNT_SPENT')

if __name__ == "__main__":
    main()