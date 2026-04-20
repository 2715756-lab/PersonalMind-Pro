from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx


class BackendError(Exception):
    pass


class BackendClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(timeout=15.0)

    async def chat(self, user_id: str, message: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        payload = {
            "user_id": user_id,
            "message": message,
            "conversation_history": history or []
        }
        return await self._post("/chat", json=payload, field="text")

    async def memory_query(self, user_id: str, query: str) -> str:
        payload = {"user_id": user_id, "query": query}
        return await self._post("/memory/query", json=payload, field="text")

    async def list_documents(self, user_id: str) -> List[Dict[str, Any]]:
        response = await self._client.get(f"{self.base_url}/api/documents/{user_id}")
        self._raise_for_status(response)
        return response.json()

    async def search_documents(self, user_id: str, query: str) -> List[Dict[str, Any]]:
        payload = {"user_id": user_id, "query": query}
        response = await self._client.post(f"{self.base_url}/api/documents/search", json=payload)
        self._raise_for_status(response)
        return response.json()

    async def upload_document(self, user_id: str, filename: str, content: bytes) -> Dict[str, Any]:
        files = {"file": (filename, content)}
        data = {"user_id": user_id}
        response = await self._client.post(f"{self.base_url}/api/documents/upload", data=data, files=files)
        self._raise_for_status(response)
        return response.json()

    async def search_commerce(self, user_id: str, query: str) -> Dict[str, Any]:
        payload = {"user_id": user_id, "query": query}
        response = await self._client.post(f"{self.base_url}/api/commerce/search", json=payload)
        self._raise_for_status(response)
        return response.json()

    async def create_order(self, user_id: str, store_id: str, product_id: str, quantity: int = 1) -> Dict[str, Any]:
        payload = {"user_id": user_id, "store_id": store_id, "items": [{"product_id": product_id, "quantity": quantity}]}
        response = await self._client.post(f"{self.base_url}/api/commerce/order", json=payload)
        self._raise_for_status(response)
        return response.json()

    async def list_orders(self, user_id: str) -> List[Dict[str, Any]]:
        response = await self._client.get(f"{self.base_url}/api/commerce/{user_id}/orders")
        self._raise_for_status(response)
        return response.json()

    async def _post(self, path: str, json: Dict[str, Any], field: str) -> str:
        response = await self._client.post(f"{self.base_url}/api{path}", json=json)
        self._raise_for_status(response)
        data = response.json()
        if field not in data:
            raise BackendError(f"Не получилось найти поле {field} в ответе")
        return data[field]

    def _raise_for_status(self, response: httpx.Response):
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise BackendError(exc.response.text or str(exc)) from exc

    async def close(self):
        await self._client.aclose()
