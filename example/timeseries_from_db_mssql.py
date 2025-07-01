# -*- coding: utf-8 -*-

from timecraft_ai import TimeCraftModel
from timecraft_ai import DatabaseConnector
from concurrent.futures import ProcessPoolExecutor

def process_product(product_id):
    print(f"Processing product {product_id}...")


    """Process a specific product."""
    db_connector = DatabaseConnector(
        db_type="mssql",
        username="sankhya",
        password="abcdefg",
        host="127.0.0.1",
        database="SANKHYA_PROD",
        port=1433,
        trust_cert="yes"
    )
    
    db_connector.connect()

    try:
        # HERE COMES THE QUERY THAT WILL FETCH THE DATA USED TO TRAIN THE MODEL
        # BE IT STOCK, PRICE, EXCHANGE RATE, ETC. (RELATED TO THE PRODUCTS FROM THE QUERY BELOW)
        with open("../data/EST_X_PROD_X_DATE-MSSQL.sql.j2", "r") as file:
            query_template = file.read()

        query = query_template.replace("{ product_id }", str(product_id))
        ts_model = TimeCraftModel(
            db_connector=db_connector,
            query=query,
            date_column="DTNEG",
            value_columns=["SALDO_HISTORICO"],
            is_csv=False,
            periods=30
        )

        ts_model.run()

        print(f"Forecast for product {product_id} completed.")

        try:
            output_file = f"output/products_stock/forecast_estoque_{product_id}.csv"

            ts_model.save_forecast(output_file)

            plot_types = list(['line', 'scatter', 'bar'])
            formats = list(['html', 'png'])

            ts_model.save_plots(output_dir="./output", plot_types=plot_types, formats=formats)

            return None
        except Exception as e:
            print(f"Error saving forecasts for product {product_id}: {e}")
            return None

    except Exception as e:
        print(f"Error processing product {product_id}: {e}")
        return None


def get_product_ids():
    """Get the IDs of active products from the database."""
    query_products = (
        "SELECT P.CODPROD "
        "FROM SANKHYA.TGFPRO P "
        "WHERE P.ATIVO = 'S' "
        f'AND P.CODPROD IN(1,2,3) '
    )

    db_connector = DatabaseConnector(
        db_type="mssql",
        username="sankhya",
        password="abcdefg",
        host="127.0.0.1",
        database="SANKHYA_PROD",
        port=1433,
        trust_cert="yes"
    )

    db_connector.connect()
    products_df = db_connector.execute_query(query_products)

    try:
        return products_df["CODPROD"].tolist()
    except Exception as e:
        print(f"Error retrieving product IDs: {e}")
        return []


if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=4) as executor:
        executor.map(process_product, get_product_ids())

    print("Processing completed.")
