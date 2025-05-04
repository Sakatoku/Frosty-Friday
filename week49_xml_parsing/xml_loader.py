import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET

# 文字列をキャストする関数
def my_cast(s: str, data_type: str):
    if data_type == "int":
        return int(s)
    elif data_type == "float":
        return float(s)
    else:
        return s

# 子要素のタグを取得する関数。なくてもいい
def get_child_tags(element):
    return [child.tag for child in element]

# ファイルアップローダ
uploaded_xml = st.file_uploader("XMLファイルを選択", type=["xml"])

# ファイルがアップロードされていれば
if uploaded_xml:
    # XMLファイルを文字列として読み込む
    xml_content = uploaded_xml.read().decode("utf-8")
    # &を含むXMLファイルを正しく表示するために、&をエスケープする
    xml_content = xml_content.replace("&", "&amp;")

    # 読み込んだXMLファイルの内容を表示
    with st.expander("XMLファイルの内容"):
        st.code(xml_content, language="xml")

    # ElementTreeでXMLファイルを解析
    root = ET.fromstring(xml_content)

    # 代表的なタグを取得
    typical_tag = ""
    child_tags = get_child_tags(root)
    if len(child_tags) > 0:
        typical_tag = child_tags[0]

    # 抽出するカラム数を指定してもらう
    columns_num = st.number_input("カラム数", min_value=1, max_value=10, value=3, step=1)

    # 指定されたカラム数だけタブを作成
    tab_list = [f"[{i+1}] XPath" for i in range(columns_num)]
    tabs = st.tabs(tab_list)

    # 各タブで抽出するカラムのXPathを入力してもらう
    for i in range(columns_num):
        with tabs[i]:
            # ここからは各タブの内容
            # Streamlitにおいて各入力コンポーネントの値はst.session_state.{key}に保存される。後でこのkeyを使って値を取得する
            _path = st.text_input("XPath", typical_tag, key=f"path_{i}")
            _type = st.selectbox("型", ["text", "int", "float"], key=f"type_{i}")
            # XPathを使って要素を取得
            if _path:
                # findall()メソッドにXPathを渡すと、それに一致する要素がリストで得られる
                elements = root.findall(_path)
                if len(elements) > 0:
                    # 最初の要素のみをプレビュー表示する
                    element = elements[0]
                    # 一致した要素をXMLで表示する
                    parted_xml = ET.tostring(element, encoding="utf-8").decode("utf-8")
                    st.code(parted_xml, language="xml")
                    # 一致した要素の値を取得して型変換を試す
                    text = element.text.strip()
                    try:
                        _ = my_cast(text, _type)
                        st.success(f"変換成功: {_type}(\"{text}\")")
                    except ValueError:
                        st.error(f"変換エラー: {_type}(\"{text}\")")

# ここまでの設定に基づいてデータを抽出する
if st.button("データ抽出"):
    # このDataFrameに抽出したデータを格納する
    df = pd.DataFrame()

    for i in range(columns_num):
        _path = st.session_state[f"path_{i}"]
        _type = st.session_state[f"type_{i}"]
        data_array = []
        # XPathを使って要素を取得
        elements = root.findall(_path)
        for element in elements:
            # 要素の値を取得して型変換する
            try:
                d = my_cast(element.text.strip(), _type)
                data_array.append(d)
            except ValueError:
                pass
        # データをDataFrameに追加する。カラム名はタグから決定する
        if len(data_array) > 0:
            column_name = _path.split("/")[-1]
            df[column_name] = data_array

    # データを格納したDataFrameをst.session_stateに保存する
    st.session_state["df"] = df

# データが格納されたDataFrameを表示する
if "df" in st.session_state:
    # データを格納したDataFrameを取得する
    df = st.session_state["df"]
    st.dataframe(df, use_container_width=True)

    # Snowflakeに書き込む処理
    st.divider()
    st.caption("以降はStreamlit in Snowflakeのみで動作します")

    # Snowflakeに書き込むための設定を入力してもらう
    table_name = st.text_input("テーブル名", "")
    mode = st.selectbox("書き込みモード", ["append", "overwrite", "errorifexists", "ignore"])
    if table_name:
        if st.button("Snowflakeに保存"):
            # Snowflakeに書き込む処理
            try:
                from snowflake.snowpark.context import get_active_session
                session = get_active_session()
                snowpark_df = session.create_dataframe(df)
                result = snowpark_df.write.mode(mode).save_as_table(table_name)
                st.info("データを保存しました")
            except Exception as e:
                st.exception(e)
