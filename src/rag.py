from langchain_openai import ChatOpenAI
from qdrant_client import QdrantClient
from typing import List, Dict, Any

from src.config import settings


class RAGSystem:
    def __init__(self):
        self.llm = ChatOpenAI(
            base_url=settings.llm_base_url,
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            api_key="not-needed",
        )

        if settings.qdrant_url:
            self.qdrant_client = QdrantClient(url=settings.qdrant_url)
        else:
            self.qdrant_client = QdrantClient(path=settings.qdrant_path or "./vectors/qdrant")

        self.collection_name = settings.collection_name

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        from langchain_community.embeddings import HuggingFaceEmbeddings

        if settings.embedding_device == "cuda":
            model = settings.embedding_model
        else:
            model = settings.cpu_embedding_model

        embeddings = HuggingFaceEmbeddings(
            model_name=model,
            model_kwargs={"device": settings.embedding_device},
            encode_kwargs={"normalize_embeddings": True},
        )

        query_vector = embeddings.embed_query(query)

        search_results = self.qdrant_client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k,
            with_payload=True,
        )

        results = []
        for result in search_results.points:
            results.append(
                {
                    "score": result.score,
                    "text": result.payload.get("text"),
                    "work_detail": result.payload.get("work_detail"),
                    "device": result.payload.get("device"),
                    "error_code": result.payload.get("error_code"),
                    "report_id": result.payload.get("report_id"),
                    "report_cd": result.payload.get("report_cd"),
                    "work_symptom": result.payload.get("work_symptom"),
                }
            )

        return results

    def query(self, user_query: str, top_k: int = 5) -> Dict[str, Any]:
        search_results = self.search(user_query, top_k=top_k)

        if not search_results:
            return {
                "answer": "No relevant information found for your query.",
                "sources": [],
                "question": user_query,
            }

        context = "\n\n".join(
            [
                f"Case {i + 1} (Device: {r.get('device', 'N/A')}, Error: {r.get('error_code', 'N/A')}):\n"
                f"Problem: {r.get('work_symptom', 'N/A')}\n"
                f"Solution: {r.get('work_detail', 'N/A')}"
                for i, r in enumerate(search_results)
            ]
        )

        system_prompt = """You are a technical support assistant. Your task is to help users find solutions to their technical issues based on past repair records.

When answering:
1. First identify what the user's issue is about
2. Find relevant cases from the provided context
3. Provide the solution(s) that worked
4. Include the device type and error codes if available
5. Be concise and practical

If no relevant solution is found, clearly state that."""

        user_prompt = f"""Context from past repair cases:
{context}

User's Question: {user_query}

Based on the above context, provide a helpful answer to the user's question. Include:
- The solution that worked
- Device information if relevant
- Any error codes mentioned"""

        response = self.llm.invoke(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
        )

        sources = [
            {
                "report_id": r.get("report_id"),
                "report_cd": r.get("report_cd"),
                "device": r.get("device"),
                "error_code": r.get("error_code"),
                "work_detail": r.get("work_detail"),
                "score": r.get("score"),
            }
            for r in search_results
        ]

        return {
            "answer": response.content
            if hasattr(response, "content")
            else str(response),
            "sources": sources,
            "question": user_query,
        }


rag_system = RAGSystem()
