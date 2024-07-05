import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd

# Fetch data from Snowflake
@st.cache_data
def fetch_data() -> pd.DataFrame:
    # Active session
    session = get_active_session()

    # Query
    sql_query = """
        select file_name, image_bytes
        from frostyfriday_db.public.week100_tbl
        """
    snowpark_df = session.sql(sql_query)
    df = snowpark_df.to_pandas()
    return df

# Main function
def main():
    # Set page config
    st.set_page_config(layout="wide")
    
    # Title
    st.title("🎉Celebrating 100 Challenges🎉")

    # Fetch and filter data from Snowflake
    df = fetch_data()

    # Select image
    selected_image = st.selectbox("Select image", df["FILE_NAME"])
    if selected_image is None:
        st.stop()

    # Convert hex string to bytes
    hex_string = df.loc[df["FILE_NAME"] == selected_image, "IMAGE_BYTES"].values[0]
    image_bytes = bytes.fromhex(hex_string)

    # Show image
    st.write("filename: ", selected_image)
    st.image(image_bytes, use_column_width=True)

if __name__ == "__main__":
    main()
