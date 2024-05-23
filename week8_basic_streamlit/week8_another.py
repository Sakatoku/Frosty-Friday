import streamlit as st
import snowflake.connector
import snowflake.snowpark as snowpark
import snowflake.cortex
import pandas as pd
import json

# Connect to Snowflake
@st.cache_resource(ttl=7200)
def connect_snowflake() -> snowpark.session:
    connection = snowflake.connector.connect(
        user=st.secrets["Snowflake"]["user"],
        password=st.secrets["Snowflake"]["password"],
        account=st.secrets["Snowflake"]["account"])
    session = snowpark.Session.builder.configs({"connection": connection}).create()
    return session

# Fetch data from Snowflake
@st.cache_data
def fetch_data(_session: snowpark.session) -> pd.DataFrame:
    sql_query = """
        select
            date_trunc('week', to_date(payment_date)) as payment_date,
            sum(amount_spent) as amount_spent
        from frostyfriday_db.public.week8_tbl
        group by 1
        """
    df = _session.sql(sql_query).to_pandas()
    return df

# Call Snowflake Cortex LLM Functions
def cortex_complete(session, model_name, prompt, temperature):
    prompt = prompt.replace('\'', '\\\'')
    cmd = f"select snowflake.cortex.complete('{model_name}', [{{'role': 'user', 'content': '{prompt}'}}], {{'temperature': {temperature}}}) as RESPONSE"
    df_response = session.sql(cmd).collect()
    json_response = json.loads(df_response[0]["RESPONSE"])
    message = json_response["choices"][0]["messages"]
    return message

# コード整形
def code_format(code):
    # もし```pythonがあればそれ以降を取得する
    code = code[code.find("```python") + 9:]
    # もし```があればそれ以降を削除する
    code = code[:code.find("```")]
    return code

# Main function
def main():
    # Title
    st.title("Payments in 2021")

    # Fetch data from Snowflake
    session = connect_snowflake()
    df = fetch_data(session)

    if "code" in st.session_state:
        st.write("前回生成したコードを使用します。")
        code = st.session_state.code
    else:
        # プロンプト
        prompt = "あなたはエキスパートなPythonプログラマーです。あなたは必ずPythonコードのみを出力してください。\n" \
                + "あなたには変数名dfのPandas DataFrameが与えられました。\n" \
                + "このdfにはDate型のPAYMENT_DATE列と、Number型のAMOUNT_SPENT列が含まれています。\n" \
                + "まず、dfからPAYMENT_DATE列の最小値と最大値を取得してください。\n" \
                + "次に、Streamlitで最小値と最大値の間の日付を2つ選択させるst.sliderを作成してください。\n" \
                + "次に、選択された日付の範囲でdfをフィルタリングしてください。\n" \
                + "最後に、フィルタリングされたdfを使って、PAYMENT_DATEをX軸、AMOUNT_SPENTをY軸にしたline_chartをStreamlitで表示してください。\n" \
                + "dfはこちらで定義するため、サンプルを定義する必要はありません。\n" \
                + "繰り返しますが、あなたは必ずPythonコードのみを出力してください。他の応答は出力してはいけません。"

        # 動くコードが生成されるように真剣にお祈りする
        st.code(prompt)
        st.write("Pray for data...")
        st.image("resoureces/pray-for-data.jpg")

        # コード生成
        code = cortex_complete(session, "snowflake-arctic", prompt, 0.0)

        # コード整形
        code = code_format(code)

    # コード表示
    st.code(code)

    # コード実行
    try:
        compiled = compile(code, filename='streamlit_app.py', mode='exec')
        exec(compiled, {'df': df})

        # ここまですべて実行が成功したら、コードをキャッシュする
        st.session_state.code = code
    except:
        pass

if __name__ == "__main__":
    main()