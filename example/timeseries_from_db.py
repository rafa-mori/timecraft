import sys

sys.path.append('../')
sys.path.append('../src')

from statistics import LinearRegression

from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

import pandas as pd

from concurrent.futures import ProcessPoolExecutor

from src.timeseries.model import TimeSeriesModel
from src.dbconnect.dbconnector import DatabaseConnector
from concurrent.futures import ProcessPoolExecutor

def process_product(product_id):
    # Configurar o conector do banco de dados
    db_connector = DatabaseConnector(
        db_type="oracle",
        username="myusername",
        password="abcdefg",
        dsn="127.0.0.1:1521/orcl"
    )

    # Definir a consulta SQL para extrair dados históricos de estoque
    with open("data/ST_X_PROD_X_DATE.sql.j2", "r") as file:
        query_template = file.read()

    # Renderiza o template com o ID do produto
    query = query_template.format({"product_id": product_id})

    ts_model = TimeSeriesModel(
        db_connector=db_connector,
        query=query.replace("{ product_id }", str(product_id)),
        date_column="history_dt",
        value_columns=["balance"],
        is_csv=False,
        periods=30
    )

    try:

        ts_model.run()

    except Exception as e:
        print(f"Error processing product {product_id}: {e}")
        return None
    
    print(f"Product extracted: {product_id}")


    output_file = f"output/products_stock/forecast_estoque_{product_id}.csv"
    ts_model.save_forecast(output_file)


    ts_model.save_plots(f"output/forecast_estoque_{product_id}.png")

    return None


def get_product_ids() -> list:
    query_products = """
    SELECT 
        p.product_id
    FROM 
        products_table p
    WHERE 
        p.fieldA = 'R'
        AND p.fieldB = 'S'
    """

    # Conectar ao banco de dados
    db_connector = DatabaseConnector(
        db_type="oracle",
        username="myusername",
        password="abcdefg",
        dsn="127.0.0.1:1521/orcl"
    )
    db_connector.connect()

    try:
        # Consultar a lista de produtos
        products_df = db_connector.execute_query(query_products)
    except Exception as e:
        print(f"Erro ao consultar produtos: {e}")
        return []

    # Fechar a conexão
    db_connector.close()

    # Lista de IDs dos produtos
    product_ids_list = products_df.get("CODPROD").tolist()

    return product_ids_list

# Get product IDs
product_ids = get_product_ids()


# Process each product in parallel
with ProcessPoolExecutor(max_workers=4) as executor:
    executor.map(process_product, product_ids)

print("All products processed successfully.")

# # Output: