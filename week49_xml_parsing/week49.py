import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from snowflake.snowpark.context import get_active_session

uploaded_xml = st.file_uploader("XMLファイルを選択", type=["xml"])
if uploaded_xml is None:
    st.stop()

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
                except ValueError:
                    st.error(f"変換エラー: {data_type}(\"{text}\")")

# 設定に基づいてデータを抽出する
if st.button("データ抽出"):
    df = pd.DataFrame()
    for i in range(columns_num):
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
    # DataFrameを表示する
    st.dataframe(df, use_container_width=True)

    # Snowflakeに書き込む処理
    session = get_active_session()
    df2 = session.create_dataframe(df)
    result = df2.write.mode("overwrite").save_as_table("Uploaded")
    st.info("データを保存しました")
