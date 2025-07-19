"""
Database Connection Module
========================
This module provides functionality for connecting to various types of databases and executing queries.
"""

from sqlalchemy import create_engine
import pandas as pd
import os
import logging

# Setup logging configuration for the package
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("timecraft_ai")


class DatabaseConnector:
    """
    Class for managing database connections and executing queries for various database types.
    """

    def __init__(self, db_type, **kwargs):
        """
        Initialize the DatabaseConnector.
        :param db_type: Type of the database (oracle, sqlite, mssql, postgres, mysql, mongodb).
        :param kwargs: Database connection parameters.
        """
        self.db_type = db_type.lower()
        self.connection = None
        self.credentials = kwargs

    def connect(self):
        """
        Establish a connection to the database.
        """
        try:
            if self.db_type == "oracle":
                import cx_Oracle

                self.connection = cx_Oracle.connect(
                    user=self.credentials.get("username")
                    or os.getenv("ORACLE_USERNAME"),
                    password=self.credentials.get("password")
                    or os.getenv("ORACLE_PASSWORD"),
                    dsn=self.credentials.get("dsn") or os.getenv("ORACLE_DSN"),
                )
            elif self.db_type == "sqlite":
                import sqlite3

                db_path = self.credentials.get(
                    "db_path") or os.getenv("SQLITE_DB_PATH")
                if db_path is None:
                    raise ValueError(
                        "Database path for SQLite cannot be None.")
                self.connection = sqlite3.connect(db_path)
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
                    host=self.credentials.get(
                        "host") or os.getenv("POSTGRES_HOST"),
                    database=self.credentials.get("database")
                    or os.getenv("POSTGRES_DATABASE"),
                    user=self.credentials.get(
                        "user") or os.getenv("POSTGRES_USER"),
                    password=self.credentials.get("password")
                    or os.getenv("POSTGRES_PASSWORD"),
                    port=self.credentials.get("port")
                    or os.getenv("POSTGRES_PORT", 5432),
                )
            elif self.db_type == "mysql":
                import mysql.connector

                self.connection = mysql.connector.connect(
                    host=self.credentials.get(
                        "host") or os.getenv("MYSQL_HOST"),
                    user=self.credentials.get(
                        "user") or os.getenv("MYSQL_USER"),
                    password=self.credentials.get("password")
                    or os.getenv("MYSQL_PASSWORD"),
                    database=self.credentials.get("database")
                    or os.getenv("MYSQL_DATABASE"),
                    port=self.credentials.get(
                        "port") or os.getenv("MYSQL_PORT", 3306),
                )
            elif self.db_type == "mongodb":
                from pymongo import MongoClient

                self.connection = MongoClient(
                    self.credentials.get("uri") or os.getenv("MONGODB_URI")
                )
            else:
                raise ValueError("Unsupported database type")
            logger.info(f"Connected to {self.db_type.upper()} database.")
        except Exception as e:
            logger.error(
                f"Erro ao conectar ao banco de dados {self.db_type}: {e}")
            self.connection = None

    def close(self):
        """
        Close the database connection if it exists.
        """
        if self.connection:
            from sqlalchemy.engine.base import Engine

            if self.db_type == "mssql" and isinstance(self.connection, Engine):
                self.connection.dispose()
            elif not isinstance(self.connection, Engine) and hasattr(
                self.connection, "close"
            ):
                self.connection.close()
            logger.info(f"Connection to {self.db_type.upper()} closed.")

    def execute_query(self, query):
        """
        Execute a SQL query and return the result as a DataFrame (or None for MongoDB).
        :param query: SQL query string.
        :return: DataFrame with query results or None.
        """
        if self.connection and self.db_type == "mssql":
            try:
                from sqlalchemy.engine.base import Engine

                if isinstance(self.connection, Engine):
                    logger.info(f"Executing query on MSSQL: {query}")
                    return pd.read_sql(query, self.connection)
                else:
                    logger.warning(
                        "Conexão mssql não é um Engine do SQLAlchemy.")
                    return pd.DataFrame()
            except Exception as e:
                logger.error(f"Erro ao executar a query: {e}")
                return pd.DataFrame()
        if self.connection and self.db_type == "oracle":
            try:
                from sqlalchemy.engine.base import Engine

                if not isinstance(self.connection, Engine) and hasattr(
                    self.connection, "cursor"
                ):
                    cursor_method = getattr(
                        self.connection, "cursor", pd.DataFrame)

                    if cursor_method is None:
                        logger.warning(
                            "Conexão Oracle não possui método cursor().")
                        return pd.DataFrame()

                    cursor = cursor_method()
                    execute = getattr(cursor, "execute", None)
                    description = getattr(cursor, "description", None)
                    fetchall = getattr(cursor, "fetchall", None)
                    close = getattr(cursor, "close", None)
                    if callable(execute) and callable(fetchall) and callable(close):
                        logger.info(f"Executing query on Oracle: {query}")
                        execute(query)
                        columns = [col[0]
                                   for col in description] if description else []
                        rows = list(fetchall())  # type: ignore
                        if hasattr(rows, "__iter__"):
                            rows = list(rows)
                            close()
                            return pd.DataFrame(rows, columns=columns)
                        else:
                            logger.warning(
                                "fetchall() não retornou um iterável.")
                            close()
                            return pd.DataFrame()
                    else:
                        logger.warning("Métodos do cursor não são chamáveis.")
                        return pd.DataFrame()
                else:
                    logger.warning(
                        "Conexão Oracle não possui método cursor() ou é um Engine."
                    )
                    return pd.DataFrame()
            except Exception as e:
                logger.error(f"Erro ao executar a query: {e}")
                return pd.DataFrame()
        elif self.db_type == "mongodb":
            logger.warning(
                "Use métodos específicos para MongoDB como find() ou insert_one()."
            )
            return None
        else:
            logger.warning("Nenhuma conexão ativa.")
            return pd.DataFrame()
            return pd.DataFrame()
            return pd.DataFrame()
