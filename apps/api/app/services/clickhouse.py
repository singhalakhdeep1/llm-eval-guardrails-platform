# ClickHouse integration for llm-eval-guardrails-platform

import clickhouse_connect
from clickhouse_connect import common
import pandas as pd
import os

class ClickHouseService:
    def __init__(self):
        self.client = clickhouse_connect.get_client(
            host=os.getenv("CLICKHOUSE_HOST", "localhost"),
            port=int(os.getenv("CLICKHOUSE_PORT", 8123)),
            username=os.getenv("CLICKHOUSE_USER", "default"),
            password=os.getenv("CLICKHOUSE_PASSWORD", ""),
            database=os.getenv("CLICKHOUSE_DATABASE", "llm_eval")
        )

    def execute(self, query: str, parameters: dict = None):
        """Execute a query"""
        return self.client.command(query, parameters)

    def insert_df(self, table_name: str, df: pd.DataFrame):
        """Insert a DataFrame"""
        return self.client.insert_df(table_name, df)

    def query_df(self, query: str, parameters: dict = None):
        """Execute a query and return a DataFrame"""
        return self.client.query_df(query, parameters)

    def query(self, query: str, parameters: dict = None):
        """Execute a query and return results"""
        return self.client.query(query, parameters)

    def create_table(self, table_name: str, schema: str):
        """Create a table"""
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})"
        return self.execute(query)

    def drop_table(self, table_name: str):
        """Drop a table"""
        query = f"DROP TABLE IF EXISTS {table_name}"
        return self.execute(query)

    def get_tables(self):
        """Get all tables"""
        query = "SHOW TABLES"
        return self.query(query)

    def get_table_schema(self, table_name: str):
        """Get table schema"""
        query = f"DESCRIBE TABLE {table_name}"
        return self.query(query)

    def insert(self, table_name: str, data: list, columns: list):
        """Insert data"""
        return self.client.insert(table_name, data, column_names=columns)

    def create_vector_table(self, table_name: str, dimensions: int):
        """Create a table for vector storage"""
        schema = f"""
            id UInt64,
            text String,
            embedding Array(Float32),
            metadata String,
            created_at DateTime DEFAULT now()
        """
        return self.create_table(table_name, schema)

    def search_vectors(self, table_name: str, query_vector: list, limit: int = 10):
        """Search for similar vectors using cosine distance"""
        query = f"""
            SELECT id, text, metadata,
                   cosineDistance(embedding, {query_vector}) as distance
            FROM {table_name}
            ORDER BY distance ASC
            LIMIT {limit}
        """
        return self.query(query)

    def create_materialized_view(self, view_name: str, source_table: str, query: str):
        """Create a materialized view"""
        create_query = f"CREATE MATERIALIZED VIEW IF NOT EXISTS {view_name} AS {query}"
        return self.execute(create_query)

    def ping(self):
        """Ping the ClickHouse server"""
        return self.client.ping()

    def close(self):
        """Close the connection"""
        self.client.close()
