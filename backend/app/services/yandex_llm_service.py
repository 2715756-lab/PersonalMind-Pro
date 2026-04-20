"""Yandex GPT API Service for PersonalMind Pro"""

import aiohttp
import json
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class YandexMessage(BaseModel):
    role: str = Field(..., description="user or assistant")
    content: str = Field(..., description="Message content")


class YandexRequest(BaseModel):
    model: str = Field(default="gpt://b1g797fquvjlp32c2ldh/yandexgpt-lite")
    input: Optional[str] = Field(None)
    messages: Optional[List[Dict[str, str]]] = Field(None)
    temperature: float = Field(default=0.7)
    max_output_tokens: int = Field(default=2000)


class YandexLLMService:
    """Service for Yandex GPT API integration"""

    def __init__(
        self,
        api_key: str,
        folder_id: str,
        model: str = "gpt://b1g797fquvjlp32c2ldh/yandexgpt-lite",
    ):
        self.api_key = api_key
        self.folder_id = folder_id
        self.model = model
        self.base_url = "https://ai.api.cloud.yandex.net/v1"
        self.headers = {
            "Authorization": f"Api-Key {api_key}",
            "x-folder-id": folder_id,
            "Content-Type": "application/json",
        }

    async def generate_response(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Generate response from Yandex GPT

        Args:
            prompt: User message
            temperature: Model temperature (0-1)
            max_tokens: Maximum tokens in response
            system_prompt: Optional system instruction

        Returns:
            Generated text response
        """
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": self.model,
                "input": prompt,
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }

            try:
                async with session.post(
                    f"{self.base_url}/responses",
                    headers=self.headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    data = await response.json()

                    if response.status != 200:
                        raise Exception(
                            f"Yandex API error: {response.status} - {data}"
                        )

                    # Extract text from response
                    if "output" in data and len(data["output"]) > 0:
                        message = data["output"][0]
                        if "content" in message and len(message["content"]) > 0:
                            return message["content"][0]["text"]

                    return "No response generated"

            except aiohttp.ClientError as e:
                raise Exception(f"Yandex API request failed: {str(e)}")

    async def generate_streaming_response(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        """
        Generate streaming response from Yandex GPT

        Args:
            prompt: User message
            temperature: Model temperature
            max_tokens: Maximum tokens

        Yields:
            Text chunks as they arrive
        """
        payload = {
            "model": self.model,
            "input": prompt,
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.base_url}/responses",
                    headers=self.headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status != 200:
                        data = await response.json()
                        raise Exception(
                            f"Yandex API error: {response.status} - {data}"
                        )

                    data = await response.json()
                    if "output" in data and len(data["output"]) > 0:
                        message = data["output"][0]
                        if "content" in message and len(message["content"]) > 0:
                            text = message["content"][0]["text"]
                            # Simulate streaming by yielding chunks
                            chunk_size = 50
                            for i in range(0, len(text), chunk_size):
                                yield text[i : i + chunk_size]

            except aiohttp.ClientError as e:
                raise Exception(f"Yandex API streaming failed: {str(e)}")

    async def extract_json(
        self, text: str, schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract JSON from Yandex response

        Args:
            text: Response text
            schema: Optional schema for validation

        Returns:
            Extracted JSON data
        """
        prompt = f"""Extract JSON data from the following text. Return only valid JSON:
{text}

Return JSON only, no explanation."""

        response = await self.generate_response(prompt)

        try:
            # Try to extract JSON from response
            import re

            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw_response": response}

    async def classify_intent(
        self, text: str, intents: List[str]
    ) -> tuple[str, float]:
        """
        Classify user intent using Yandex GPT

        Args:
            text: User message
            intents: List of possible intents

        Returns:
            Tuple of (intent, confidence)
        """
        intent_list = "\n".join([f"- {i}" for i in intents])
        prompt = f"""Classify the following user message into one of these intents:
{intent_list}

Message: "{text}"

Return result in JSON format: {{"intent": "...", "confidence": 0.0-1.0}}"""

        response = await self.generate_response(prompt)
        result = await self.extract_json(response)

        intent = result.get("intent", intents[0] if intents else "unknown")
        confidence = result.get("confidence", 0.5)

        return intent, confidence

    async def health_check(self) -> bool:
        """Check if Yandex API is accessible"""
        try:
            response = await self.generate_response(
                "Hello", temperature=0.5, max_tokens=10
            )
            return len(response) > 0
        except Exception as e:
            print(f"Yandex API health check failed: {e}")
            return False


# Test usage
if __name__ == "__main__":
    import asyncio
    import os

    async def test():
        # Get credentials from environment
        api_key = os.getenv("YANDEX_API_KEY")
        folder_id = os.getenv("YANDEX_FOLDER_ID")
        
        if not api_key or not folder_id:
            print("Error: YANDEX_API_KEY or YANDEX_FOLDER_ID not set in environment")
            return
            
        service = YandexLLMService(
            api_key=api_key,
            folder_id=folder_id,
        )

        # Test basic response
        print("Testing Yandex GPT...")
        response = await service.generate_response("Привет, как дела?")
        print(f"Response: {response}\n")

        # Test health check
        is_healthy = await service.health_check()
        print(f"Health check: {'✅ OK' if is_healthy else '❌ Failed'}\n")

    asyncio.run(test())
