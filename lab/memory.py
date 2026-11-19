"""
Persistent vector memory for Research Agency Lab.
Uses ChromaDB for long-term knowledge storage per Lab / Project.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False


DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
CHROMA_DIR = DATA_DIR / "chroma"
CHROMA_DIR.mkdir(parents=True, exist_ok=True)


class LabMemory:
    """Persistent vector memory scoped to a single Research Lab / Project."""

    def __init__(self, lab_id: str, collection_name: Optional[str] = None):
        self.lab_id = lab_id
        self.collection_name = collection_name or f"lab_{lab_id}"

        if not CHROMA_AVAILABLE:
            self.client = None
            self.collection = None
            return

        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"lab_id": lab_id, "created": datetime.utcnow().isoformat()},
        )

    def add(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> None:
        if not self.collection:
            return
        if ids is None:
            ids = [f"{self.lab_id}_{datetime.utcnow().timestamp()}_{i}" for i in range(len(texts))]
        if metadatas is None:
            metadatas = [{"source": "agent", "timestamp": datetime.utcnow().isoformat()} for _ in texts]
        self.collection.add(documents=texts, metadatas=metadatas, ids=ids)

    def query(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        if not self.collection:
            return []
        try:
            results = self.collection.query(query_texts=[query_text], n_results=n_results)
            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]
            dists = results.get("distances", [[]])[0]
            return [
                {"text": d, "metadata": m, "distance": dist}
                for d, m, dist in zip(docs, metas, dists)
            ]
        except Exception:
            return []

    def count(self) -> int:
        if not self.collection:
            return 0
        return self.collection.count()

    def clear(self) -> None:
        if self.client and self.collection:
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.get_or_create_collection(name=self.collection_name)


def get_lab_memory(lab_id: str) -> LabMemory:
    return LabMemory(lab_id)
