import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from snowflake.snowpark.context import get_active_session

# ログとトレースのためのモジュール
import logging
import time
from snowflake import telemetry
import json

def do_logging(filename: str):
    logger = logging.getLogger("sis_logger")
    logger.info(f"File uploaded: {filename}")

def do_tracing(function_name: str, category_name: str, process_time: int):
    telemetry.add_event(
        "sis_tracing",
        {"function_name": function_name, "category_name": category_name, "process_time": process_time},
    )

uploaded_xml = st.file_uploader("XMLファイルを選択", type=["xml"])
if uploaded_xml is None:
    st.stop()

# ロギング
do_logging(uploaded_xml.name)

# XMLファイルを読み込む
xml_content = uploaded_xml.read().decode("utf-8")
# &を含むXMLファイルを正しく表示するために、&をエスケープする
xml_content = xml_content.replace("&", "&amp;")

with st.expander("XMLファイルの内容"):
    st.code(xml_content, language="xml")

# XMLファイルを解析
root = ET.fromstring(xml_content)

# カラム数を指定させる
columns_num = st.number_input("カラム数", min_value=1, max_value=10, value=4, step=1)

# 指定されたカラム数だけタブを作成
tab_list = [f"[{i+1}] XPath" for i in range(columns_num)]
tabs = st.tabs(tab_list)

def convert(s: str, data_type: str):
    if data_type == "int":
        return int(s)
    elif data_type == "float":
        return float(s)
    else:
        return s

# 各タブでXPathを入力させる
for i in range(columns_num):
    with tabs[i]:
        path = st.text_input("XPath", "book", key=f"path_{i}")
        data_type = st.selectbox("型", ["text", "int", "float"], key=f"type_{i}")
        if path:
            # XPathを使って要素を取得
            elements = root.findall(path)
            if len(elements) > 0:
                parted_xml = ET.tostring(elements[0], encoding="utf-8").decode("utf-8")
                st.code(parted_xml, language="xml")
                # 要素の値を取得して型変換する
                text = elements[0].text.strip()
                try:
                    _ = convert(text, data_type)
                    st.success(f"変換成功: {data_type}(\"{text}\")")
                except ValueError:
                    st.error(f"変換エラー: {data_type}(\"{text}\")")

# 設定に基づいてデータを抽出する
if st.button("データ抽出"):
    df = pd.DataFrame()
    for i in range(columns_num):
        # 時間計測
        start_time = time.time()
        # XPathを使って要素を取得
        data = []
        elements = root.findall(st.session_state[f"path_{i}"])
        for element in elements:
            try:
                d = convert(element.text.strip(), st.session_state[f"type_{i}"])
                data.append(d)
            except ValueError:
                pass
        # データをDataFrameに追加する
        if len(data) > 0:
            column_name = st.session_state[f"path_{i}"].split("/")[-1]
            df[column_name] = data
        # 時間計測終了
        end_time = time.time()
        process_time = end_time - start_time
        # トレース
        do_tracing("data_extraction", st.session_state[f"path_{i}"], process_time)
    # DataFrameを表示する
    st.dataframe(df, use_container_width=True)

    # 時間計測
    start_time = time.time()
    # Snowflakeに書き込む処理
    session = get_active_session()
    df2 = session.create_dataframe(df)
    result = df2.write.mode("overwrite").save_as_table("Uploaded")
    st.info("データを保存しました")
    # 時間計測終了
    end_time = time.time()
    process_time = end_time - start_time
    # トレース
    do_tracing("save_to_snowflake", "overwrite", process_time)

def get_trace_messages_query() -> str:
    return """
            SELECT
                TIMESTAMP,
                RESOURCE_ATTRIBUTES :"db.user" :: VARCHAR AS USER,
                RECORD_TYPE,
                RECORD_ATTRIBUTES
            FROM
                SIS_EVENTS
            WHERE
                RECORD :"name" :: VARCHAR = 'sis_tracing'
            ORDER BY
                TIMESTAMP DESC;
            """

if st.button("トレースを表示"):
    session = get_active_session()
    sql = get_trace_messages_query()
    df = session.sql(sql).to_pandas()
    # RECORD_ATTRIBUTESをfunction_name/category_name/process_timeに分割
    # RECORD_ATTRIBUTESはJSON形式のStringなので、辞書に変換する
    df["RECORD_ATTRIBUTES"] = df["RECORD_ATTRIBUTES"].apply(lambda x: json.loads(x))
    df["function_name"] = df["RECORD_ATTRIBUTES"].apply(lambda x: x["function_name"])
    df["category_name"] = df["RECORD_ATTRIBUTES"].apply(lambda x: x["category_name"])
    df["process_time"] = df["RECORD_ATTRIBUTES"].apply(lambda x: x["process_time"])
    st.dataframe(df, use_container_width=True)
