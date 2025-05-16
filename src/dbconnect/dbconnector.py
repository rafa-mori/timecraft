import sys

sys.path.append('../')
sys.path.append('../../src')

import os

import pandas as pd
from sqlalchemy import create_engine


class DatabaseConnector:
    def __init__(self, db_type, **kwargs):
        self.db_type = db_type.lower()
        self.connection = None
        self.credentials = kwargs

    def connect(self):
        try:
            if self.db_type == "oracle":
                import cx_Oracle

                self.connection = cx_Oracle.connect(
                    user=self.credentials.get("username") or os.getenv("ORACLE_USERNAME"),
                    password=self.credentials.get("password") or os.getenv("ORACLE_PASSWORD"),
                    dsn=self.credentials.get("dsn") or os.getenv("ORACLE_DSN")
                )
            elif self.db_type == "sqlite":
                import sqlite3

                self.connection = sqlite3.connect(
                    self.credentials.get("db_path") or os.getenv("SQLITE_DB_PATH")
                )
            elif self.db_type == "mssql":
                conn_string = (
                    "mssql+pyodbc://"
                    f'{self.credentials.get("username") or os.getenv("MSSQL_USERNAME")}:'
                    f'{self.credentials.get("password") or os.getenv("MSSQL_PASSWORD")}@'
                    f'{self.credentials.get("host") or os.getenv("MSSQL_HOST", "127.0.0.1")}:'
                    f'{self.credentials.get("port") or os.getenv("MSSQL_PORT", 1433)}/'
                    f'{self.credentials.get("database") or os.getenv("MSSQL_DATABASE")}?'
                    "driver=ODBC+Driver+17+for+SQL+Server"
                )
                self.connection = create_engine(conn_string)
            elif self.db_type == "postgres":
                import psycopg2
                
                self.connection = psycopg2.connect(
                    host=self.credentials.get("host") or os.getenv("POSTGRES_HOST"),
                    database=self.credentials.get("database") or os.getenv("POSTGRES_DATABASE"),
                    user=self.credentials.get("user") or os.getenv("POSTGRES_USER"),
                    password=self.credentials.get("password") or os.getenv("POSTGRES_PASSWORD"),
                    port=self.credentials.get("port") or os.getenv("POSTGRES_PORT", 5432)
                )
            elif self.db_type == "mysql":
                import mysql.connector

                self.connection = mysql.connector.connect(
                    host=self.credentials.get("host") or os.getenv("MYSQL_HOST"),
                    user=self.credentials.get("user") or os.getenv("MYSQL_USER"),
                    password=self.credentials.get("password") or os.getenv("MYSQL_PASSWORD"),
                    database=self.credentials.get("database") or os.getenv("MYSQL_DATABASE"),
                    port=self.credentials.get("port") or os.getenv("MYSQL_PORT", 3306)
                )
            elif self.db_type == "mongodb":
                from pymongo import MongoClient

                self.connection = MongoClient(
                    self.credentials.get("uri") or os.getenv("MONGODB_URI")
                )
            else:
                raise ValueError("Unsupported database type")
            print(f"Conexão com {self.db_type.upper()} estabelecida com sucesso!")
        except Exception as e:
            print(f"Erro ao conectar ao banco de dados {self.db_type}: {e}")
            self.connection = None

    def close(self):
        if self.connection:
            if hasattr(self.connection, "close"):
                self.connection.close()
            elif hasattr(self.connection, "disconnect"):
                self.connection.disconnect()

            print(f"Conexão com {self.db_type.upper()} encerrada!")

    def execute_query(self, query):
        if self.connection and self.db_type == "mssql":
            try:
                return pd.read_sql(query, self.connection)
            except Exception as e:
                print(f"Erro ao executar a query: {e}")
                return pd.DataFrame()
        if self.connection and self.db_type == "oracle":
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute(query)
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()
                return pd.DataFrame(rows, columns=columns)
            except Exception as e:
                print(f"Erro ao executar a query: {e}")
                return pd.DataFrame()
        elif self.db_type == "mongodb":
            print("Use métodos específicos para MongoDB como find() ou insert_one().")
            return None
        else:
            print("Nenhuma conexão ativa.")
            return pd.DataFrame()
