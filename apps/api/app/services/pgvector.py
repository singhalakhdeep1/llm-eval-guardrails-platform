# PostgreSQL + pgvector integration for llm-eval-guardrails-platform

import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
import numpy as np
import os

class PGVectorService:
    def __init__(self):
        self.connection = psycopg2.connect(
            host=os.getenv("PGVECTOR_HOST", "localhost"),
            port=os.getenv("PGVECTOR_PORT", "5432"),
            database=os.getenv("PGVECTOR_DATABASE", "llm_eval"),
            user=os.getenv("PGVECTOR_USER", "postgres"),
            password=os.getenv("PGVECTOR_PASSWORD", "")
        )
        self._enable_extension()

    def _enable_extension(self):
        """Enable pgvector extension"""
        with self.connection.cursor() as cursor:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            self.connection.commit()

    def create_table(self, table_name: str, dimensions: int):
        """Create a table with vector column"""
        with self.connection.cursor() as cursor:
            cursor.execute(sql.SQL("""
                CREATE TABLE IF NOT EXISTS {} (
                    id SERIAL PRIMARY KEY,
                    text TEXT,
                    embedding vector({}),
                    metadata JSONB
                );
            """).format(sql.Identifier(table_name), sql.Literal(dimensions)))
            self.connection.commit()

    def insert_embedding(self, table_name: str, text: str, embedding: np.ndarray, metadata: dict = None):
        """Insert an embedding"""
        with self.connection.cursor() as cursor:
            cursor.execute(sql.SQL("""
                INSERT INTO {} (text, embedding, metadata)
                VALUES (%s, %s, %s)
                RETURNING id;
            """).format(sql.Identifier(table_name)),
            (text, embedding.tolist(), metadata))
            self.connection.commit()
            return cursor.fetchone()[0]

    def search_similar(self, table_name: str, query_embedding: np.ndarray, limit: int = 10):
        """Search for similar embeddings"""
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql.SQL("""
                SELECT id, text, metadata, 1 - (embedding <=> %s) as similarity
                FROM {}
                ORDER BY embedding <=> %s
                LIMIT %s;
            """).format(sql.Identifier(table_name)),
            (query_embedding.tolist(), query_embedding.tolist(), limit))
            return cursor.fetchall()

    def get_embedding(self, table_name: str, id: int):
        """Get an embedding by ID"""
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql.SQL("""
                SELECT id, text, embedding, metadata
                FROM {}
                WHERE id = %s;
            """).format(sql.Identifier(table_name)), (id,))
            return cursor.fetchone()

    def delete_embedding(self, table_name: str, id: int):
        """Delete an embedding"""
        with self.connection.cursor() as cursor:
            cursor.execute(sql.SQL("""
                DELETE FROM {} WHERE id = %s;
            """).format(sql.Identifier(table_name)), (id,))
            self.connection.commit()

    def create_index(self, table_name: str, index_name: str):
        """Create an index on the vector column"""
        with self.connection.cursor() as cursor:
            cursor.execute(sql.SQL("""
                CREATE INDEX IF NOT EXISTS {} ON {} USING ivfflat (embedding vector_cosine_ops);
            """).format(sql.Identifier(index_name), sql.Identifier(table_name)))
            self.connection.commit()

    def close(self):
        """Close the connection"""
        self.connection.close()
