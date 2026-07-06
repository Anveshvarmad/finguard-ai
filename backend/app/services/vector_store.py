from typing import Any

import chromadb
from sqlalchemy.orm import Session

from app.config import settings
from app.models import SearchLog, Transaction
from app.services.openai_service import OpenAIService


class VectorStoreService:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.chroma_persist_path)
        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        self.openai_service = OpenAIService()

    def build_transaction_document(self, transaction: Transaction) -> str:
        risk_flags = ", ".join(transaction.risk_flags or [])

        return f"""
Transaction {transaction.transaction_id}
Vendor: {transaction.vendor_name}
Department: {transaction.department}
Amount: {transaction.amount} {transaction.currency}
Payment Method: {transaction.payment_method}
Country: {transaction.country}
Category: {transaction.category}
Description: {transaction.description}
Invoice ID: {transaction.invoice_id}
Approval Status: {transaction.approval_status}
Approved By: {transaction.approved_by}
Risk Level: {transaction.risk_level}
Risk Score: {transaction.risk_score}
Risk Flags: {risk_flags}
Review Status: {transaction.review_status}
Timestamp: {transaction.timestamp}
""".strip()

    def build_transaction_metadata(self, transaction: Transaction) -> dict[str, Any]:
        return {
            "transaction_id": transaction.transaction_id,
            "vendor_name": transaction.vendor_name,
            "department": transaction.department,
            "amount": float(transaction.amount),
            "currency": transaction.currency,
            "payment_method": transaction.payment_method,
            "country": transaction.country,
            "category": transaction.category,
            "risk_score": int(transaction.risk_score),
            "risk_level": transaction.risk_level,
            "review_status": transaction.review_status,
            "invoice_id": transaction.invoice_id or "",
            "approval_status": transaction.approval_status,
            "risk_flags_text": ", ".join(transaction.risk_flags or []),
            "timestamp": transaction.timestamp.isoformat() if transaction.timestamp else "",
        }

    def index_transaction(self, transaction: Transaction) -> dict[str, Any]:
        document = self.build_transaction_document(transaction)
        metadata = self.build_transaction_metadata(transaction)
        embedding = self.openai_service.generate_embedding(document)

        self.collection.upsert(
            ids=[transaction.transaction_id],
            embeddings=[embedding],
            documents=[document],
            metadatas=[metadata],
        )

        return {
            "transaction_id": transaction.transaction_id,
            "indexed": True,
            "document_length": len(document),
        }

    def index_transactions(
        self,
        db: Session,
        limit: int = 500,
    ) -> dict[str, Any]:
        transactions = (
            db.query(Transaction)
            .order_by(Transaction.created_at.desc())
            .limit(limit)
            .all()
        )

        indexed_ids = []

        for transaction in transactions:
            self.index_transaction(transaction)
            indexed_ids.append(transaction.transaction_id)

        return {
            "indexed_count": len(indexed_ids),
            "indexed_ids": indexed_ids,
        }

    def semantic_search(
        self,
        db: Session,
        query: str,
        top_k: int = 10,
        risk_level: str | None = None,
        department: str | None = None,
        vendor: str | None = None,
        payment_method: str | None = None,
        category: str | None = None,
        country: str | None = None,
        min_amount: float | None = None,
        max_amount: float | None = None,
    ) -> dict[str, Any]:
        query_embedding = self.openai_service.generate_embedding(query)

        where_filter = self._build_chroma_filter(
            risk_level=risk_level,
            department=department,
            payment_method=payment_method,
            category=category,
            country=country,
        )

        chroma_results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        ids = chroma_results.get("ids", [[]])[0]
        documents = chroma_results.get("documents", [[]])[0]
        metadatas = chroma_results.get("metadatas", [[]])[0]
        distances = chroma_results.get("distances", [[]])[0]

        results = []

        for index, transaction_id in enumerate(ids):
            transaction = (
                db.query(Transaction)
                .filter(Transaction.transaction_id == transaction_id)
                .first()
            )

            if not transaction:
                continue

            if vendor and vendor.lower() not in transaction.vendor_name.lower():
                continue

            if min_amount is not None and transaction.amount < min_amount:
                continue

            if max_amount is not None and transaction.amount > max_amount:
                continue

            distance = float(distances[index]) if index < len(distances) else 1.0
            similarity_score = round(max(0.0, 1.0 - distance), 4)

            result = {
                "transaction": transaction,
                "similarity_score": similarity_score,
                "distance": round(distance, 4),
                "evidence_text": documents[index] if index < len(documents) else "",
                "metadata": metadatas[index] if index < len(metadatas) else {},
                "matched_reason": self._build_matched_reason(
                    query=query,
                    transaction=transaction,
                    similarity_score=similarity_score,
                ),
            }

            results.append(result)

        search_log = SearchLog(
            query=query,
            filters={
                "risk_level": risk_level,
                "department": department,
                "vendor": vendor,
                "payment_method": payment_method,
                "category": category,
                "country": country,
                "min_amount": min_amount,
                "max_amount": max_amount,
                "top_k": top_k,
            },
            result_count=len(results),
        )

        db.add(search_log)
        db.commit()

        return {
            "query": query,
            "top_k": top_k,
            "result_count": len(results),
            "results": results,
        }

    def get_collection_stats(self) -> dict[str, Any]:
        return {
            "collection_name": settings.chroma_collection_name,
            "persist_path": settings.chroma_persist_path,
            "vector_count": self.collection.count(),
        }

    def reset_collection(self) -> dict[str, Any]:
        try:
            self.client.delete_collection(settings.chroma_collection_name)
        except Exception:
            pass

        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
        )

        return {
            "status": "reset",
            "collection_name": settings.chroma_collection_name,
            "vector_count": self.collection.count(),
        }

    def _build_chroma_filter(
        self,
        risk_level: str | None = None,
        department: str | None = None,
        payment_method: str | None = None,
        category: str | None = None,
        country: str | None = None,
    ) -> dict[str, Any] | None:
        filters = []

        if risk_level:
            filters.append({"risk_level": {"$eq": risk_level}})

        if department:
            filters.append({"department": {"$eq": department}})

        if payment_method:
            filters.append({"payment_method": {"$eq": payment_method}})

        if category:
            filters.append({"category": {"$eq": category}})

        if country:
            filters.append({"country": {"$eq": country}})

        if not filters:
            return None

        if len(filters) == 1:
            return filters[0]

        return {"$and": filters}

    def _build_matched_reason(
        self,
        query: str,
        transaction: Transaction,
        similarity_score: float,
    ) -> str:
        return (
            f"This transaction matched the query because its embedded evidence "
            f"is semantically similar to '{query}'. It involves {transaction.vendor_name}, "
            f"{transaction.payment_method}, {transaction.category}, "
            f"and has {transaction.risk_level} risk with score {transaction.risk_score}. "
            f"Similarity score: {similarity_score}."
        )
