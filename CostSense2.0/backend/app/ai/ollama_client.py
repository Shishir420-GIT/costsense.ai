import httpx
import json
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from ..config import settings
from ..logging_config import get_logger

logger = get_logger(__name__)


class OllamaResponse(BaseModel):
    """Ollama API response"""
    model: str
    response: str
    done: bool
    context: Optional[List[int]] = None
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_duration: Optional[int] = None
    eval_duration: Optional[int] = None


class OllamaClient:
    """Client for Ollama LLM API with retry logic and validation"""

    def __init__(
        self,
        base_url: str = None,
        model: str = None,
        timeout: int = None,
        max_retries: int = None,
    ):
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.ollama_model
        self.timeout = timeout or settings.ollama_timeout
        self.max_retries = max_retries or settings.ollama_max_retries

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
        )

        logger.info(
            "Ollama client initialized",
            base_url=self.base_url,
            model=self.model,
        )

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        format: Optional[str] = None,
    ) -> str:
        """Generate text using Ollama with retry logic"""
        for attempt in range(self.max_retries):
            try:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                    },
                }

                if system_prompt:
                    payload["system"] = system_prompt

                if max_tokens:
                    payload["options"]["num_predict"] = max_tokens

                if format:
                    payload["format"] = format

                response = await self.client.post("/api/generate", json=payload)
                response.raise_for_status()

                result = response.json()
                return result.get("response", "")

            except httpx.TimeoutException as e:
                logger.warning(
                    f"Ollama request timeout (attempt {attempt + 1}/{self.max_retries})",
                    error=str(e),
                )
                if attempt == self.max_retries - 1:
                    raise
            except httpx.HTTPError as e:
                logger.error("Ollama HTTP error", error=str(e))
                raise
            except Exception as e:
                logger.error("Ollama generation error", error=str(e))
                raise

    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Generate JSON output with strict schema enforcement"""
        try:
            response = await self.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                format="json",
            )

            # Parse and validate JSON
            try:
                return json.loads(response)
            except json.JSONDecodeError as e:
                logger.error("Failed to parse JSON response", response=response[:200])
                raise ValueError(f"Invalid JSON response from LLM: {str(e)}")

        except Exception as e:
            logger.error("JSON generation error", error=str(e))
            raise

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Chat completion with message history"""
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                },
            }

            if max_tokens:
                payload["options"]["num_predict"] = max_tokens

            response = await self.client.post("/api/chat", json=payload)
            response.raise_for_status()

            result = response.json()
            return result.get("message", {}).get("content", "")

        except Exception as e:
            logger.error("Chat completion error", error=str(e))
            raise

    async def health_check(self) -> bool:
        """Check if Ollama is healthy and model is available"""
        try:
            response = await self.client.get("/api/tags")
            response.raise_for_status()

            models = response.json().get("models", [])
            model_names = [m.get("name") for m in models]

            if self.model not in model_names:
                logger.warning(
                    f"Model {self.model} not found in available models",
                    available=model_names,
                )
                return False

            logger.info("Ollama health check passed")
            return True

        except Exception as e:
            logger.error("Ollama health check failed", error=str(e))
            return False


# Global client instance
_ollama_client: Optional[OllamaClient] = None


async def get_ollama_client() -> OllamaClient:
    """Get or create Ollama client instance"""
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client


async def close_ollama_client():
    """Close Ollama client"""
    global _ollama_client
    if _ollama_client is not None:
        await _ollama_client.close()
        _ollama_client = None
