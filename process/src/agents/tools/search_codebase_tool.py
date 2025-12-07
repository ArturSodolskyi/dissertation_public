import os
from langchain.tools import BaseTool
import cocoindex
import functools
from numpy.typing import NDArray
import numpy as np
from psycopg_pool import ConnectionPool
from pgvector.psycopg import register_vector
from dotenv import load_dotenv

load_dotenv()


@cocoindex.transform_flow()
def code_to_embedding(
    text: cocoindex.DataSlice[str],
) -> cocoindex.DataSlice[NDArray[np.float32]]:
    return text.transform(
        cocoindex.functions.SentenceTransformerEmbed(
            model="sentence-transformers/all-MiniLM-L6-v2"
        )
    )


@functools.cache
def connection_pool() -> ConnectionPool:
    return ConnectionPool(os.getenv("COCOINDEX_DATABASE_URL"))


class SearchCodebaseTool(BaseTool):
    name: str = "search_codebase"
    description: str = (
        "Search through indexed codebase using semantic similarity. "
        "Takes a natural language query and optional k parameter for number of results. "
        "Returns relevant code snippets with their file locations. "
        "Useful for finding specific functionality, classes, functions, or patterns in the codebase. "
        "Usage: query='your search query' k=5 (optional, default is 5)"
    )

    def _run(self, query: str, k: int = 5) -> str:
        """
        Search the indexed codebase using semantic similarity.

        Args:
            query: Natural language query describing what to search for
            k: Number of top results to return (default: 5)

        Returns:
            String containing search results with code snippets and file locations
        """
        try:
            query_vector = code_to_embedding.eval(query)
            table_name = "CodeEmbedding__code_embeddings"
            top_k = k

            with connection_pool().connection() as conn:
                register_vector(conn)
                with conn.cursor() as cur:
                    cur.execute(
                        f"""
                        SELECT filename, code, embedding <=> %s AS distance, start, "end"
                        FROM {table_name} 
                        ORDER BY distance 
                        LIMIT %s
                        """,
                        (query_vector, top_k),
                    )

                    results = cur.fetchall()

                    if not results:
                        return f"No results found for query: '{query}'"

                    output = f"Search results for: '{query}'\n"
                    output += "=" * 50 + "\n\n"

                    for i, row in enumerate(results, 1):
                        filename, code, distance, start, end = row
                        score = 1.0 - distance

                        output += f"Result {i}:\n"
                        output += f"File: {filename}\n"
                        output += f"Score: {score:.3f}\n"

                        if start is not None and end is not None:
                            output += f"Lines: {start}-{end}\n"

                        output += f"Code:\n```\n{code}\n```\n"
                        output += "-" * 30 + "\n\n"

                    return output.strip()

        except Exception as e:
            return f"Error searching codebase: {str(e)}"

    async def _arun(self, query: str, k: int = 5) -> str:
        """
        Asynchronous execution (optional). Not implemented here.
        """
        raise NotImplementedError(
            "Asynchronous execution is not supported for this tool."
        )
