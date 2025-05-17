# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session

# Get the current credentials
session = get_active_session()

df = session.sql('LIST @FROSTYFRIDAY_DB.WEEK139.FROSTY_STAGE;')
st.dataframe(df.collect())

file = session.file.get('@FROSTYFRIDAY_DB.WEEK139.FROSTY_STAGE/challenge_139/snowflake_course_reviews.csv', '/tmp')
with open('/tmp/snowflake_course_reviews.csv','r') as f:
    st.code(f.read(), line_numbers=True)
