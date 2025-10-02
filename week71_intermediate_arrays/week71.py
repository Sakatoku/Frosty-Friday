import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

# データベースとスキーマ
db_path = "FROSTYFRIDAY_DB.WEEK71"

# コンフィグ設定
st.set_page_config(page_title="Frosty Friday Week71", layout="wide")

# タイトルを表示
st.markdown("# :snowflake: Frosty Friday Week 71 🕸️")
st.markdown("Streamlit :streamlit: で共通するカテゴリーを見つけよう！")

# セッション取得
session = st.connection('snowflake').session()

# SalesテーブルをDataFrameで取得する
def get_sales_data(_session):
    query = f"""
    SELECT 
        Sale_ID,
        Product_ID_List.value::NUMBER AS Product_ID
    FROM {db_path}.Sales,
    LATERAL FLATTEN(Sales.Product_IDs) Product_ID_List
    """
    data = _session.sql(query).collect()
    return data

# ProductsテーブルをDataFrameで取得する
def get_products_data(_session):
    query = f"""
    SELECT * FROM {db_path}.Products
    """
    data = _session.sql(query).collect()
    return data

# ProductsテーブルからCategoryをDataFrameで取得する
def get_category_data(_session):
    query = f"""
    SELECT 
        Product_ID,
        Product_Category_List.value::STRING AS Product_Category
    FROM Products,
    LATERAL FLATTEN(Products.Product_Categories) Product_Category_List
    """
    data = _session.sql(query).collect()
    return data

# 画像を取得する
def id2url(id):
    return f"https://github.com/Sakatoku/Frosty-Friday/blob/main/week71_intermediate_arrays/image/product{id}.png?raw=true"

sales_data = get_sales_data(session)
with st.expander("Sales"):
    st.dataframe(sales_data)

products_data = get_products_data(session)
with st.expander("Products"):
    st.dataframe(products_data)

categories_data = get_category_data(session)
with st.expander("Categories"):
    st.dataframe(categories_data)

sale_list = {}
for row in sales_data:
    sale_id = row["SALE_ID"]
    if not sale_id in sale_list:
        sale_list[sale_id] = f"Sale:{sale_id}"

product_list = {}
for row in products_data:
    product_id = row["PRODUCT_ID"]
    product_name = row["PRODUCT_NAME"]
    if not product_id in product_list:
        product_list[product_id] = f"{product_name}"

category_list = {}
for row in categories_data:
    category_name = row["PRODUCT_CATEGORY"]
    if not category_name in category_list:
        category_list[category_name] = f"{category_name}"

# ノードを作成
nodes = []
for id, text in sale_list.items():
    node = Node(id=f"sale:{id}", label=text, size=25, shape="circle", color="red")
    nodes.append(node)
for id, text in product_list.items():
    node = Node(id=f"product:{id}", label=text, size=25, shape="circularImage", image=id2url(id))
    nodes.append(node)
for id, text in category_list.items():
    node = Node(id=f"category:{id}", label=text, size=25, shape="circle", color="green")
    nodes.append(node)

# エッジを作成
edges = []
for row in sales_data:
    sale_id = row["SALE_ID"]
    product_id = row["PRODUCT_ID"]
    edge = Edge(source=f"sale:{sale_id}", target=f"product:{product_id}")
    edges.append(edge)
for row in categories_data:
    product_id = row["PRODUCT_ID"]
    category_name = row["PRODUCT_CATEGORY"]
    edge = Edge(source=f"product:{product_id}", target=f"category:{category_name}")
    edges.append(edge)

config = Config(width=1920,
                height=1280,
                directed=True, 
                physics=True, 
                hierarchical=False
                )

_ = agraph(nodes=nodes, edges=edges, config=config)