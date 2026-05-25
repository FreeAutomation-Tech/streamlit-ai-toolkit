import json
import re
import urllib.request
import urllib.error
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Generator, List, Optional


class APIKeyError(Exception):
    pass


class RateLimitError(Exception):
    pass


class TimeoutError(Exception):
    pass


class APIError(Exception):
    pass


@dataclass
class ChatMessage:
    role: str
    content: str


@dataclass
class ChatCompletion:
    content: str
    model: str
    role: str = "assistant"
    finish_reason: str = "stop"
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0


class AIProvider(ABC):
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: int = 60,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self._validate_api_key()
    
    def _validate_api_key(self) -> None:
        if not self.api_key or not self.api_key.strip():
            raise APIKeyError("API key is required but was not provided.")
    
    @abstractmethod
    def chat_completion(
        self,
        model: str,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> ChatCompletion:
        pass
    
    @abstractmethod
    def stream_chat(
        self,
        model: str,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> Generator[str, None, None]:
        pass
    
    def _make_request(
        self,
        url: str,
        method: str = "POST",
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, Any]] = None,
        stream: bool = False,
    ) -> Any:
        req_headers = headers or {}
        
        req_data = None
        if data:
            req_data = json.dumps(data).encode("utf-8")
            req_headers["Content-Type"] = "application/json"
        
        request = urllib.request.Request(
            url,
            data=req_data,
            headers=req_headers,
            method=method,
        )
        
        try:
            response = urllib.request.urlopen(request, timeout=self.timeout)
            
            if stream:
                return response
            
            response_data = response.read().decode("utf-8")
            return json.loads(response_data)
            
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else ""
            
            try:
                error_json = json.loads(error_body)
                error_msg = self._extract_error_message(error_json, e.code)
            except json.JSONDecodeError:
                error_msg = error_body[:500] if error_body else str(e)
            
            if e.code == 401:
                raise APIKeyError(f"Authentication failed (401): {error_msg}")
            elif e.code == 429:
                raise RateLimitError(f"Rate limit exceeded (429): {error_msg}")
            elif e.code in (500, 502, 503, 504):
                raise APIError(f"Server error ({e.code}): {error_msg}. Please try again later.")
            elif e.code == 400:
                raise APIError(f"Bad request (400): {error_msg}")
            elif e.code == 404:
                raise APIError(f"Not found (404): {error_msg}. Check if the model name is correct.")
            else:
                raise APIError(f"API error ({e.code}): {error_msg}")
                
        except urllib.error.URLError as e:
            if "timed out" in str(e).lower():
                raise TimeoutError(f"Request timed out after {self.timeout} seconds. Please try again.")
            raise APIError(f"Connection error: {str(e)}")
    
    @abstractmethod
    def _extract_error_message(self, error_json: Dict[str, Any], status_code: int) -> str:
        pass


class OpenAIProvider(AIProvider):
    DEFAULT_BASE_URL = "https://api.openai.com/v1"
    
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: int = 60,
    ):
        super().__init__(
            api_key=api_key,
            base_url=base_url or self.DEFAULT_BASE_URL,
            timeout=timeout,
        )
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    def _format_messages(self, messages: List[ChatMessage]) -> List[Dict[str, Any]]:
        formatted = []
        for msg in messages:
            if isinstance(msg, ChatMessage):
                formatted.append({"role": msg.role, "content": msg.content})
            elif isinstance(msg, dict):
                formatted.append(msg)
        return formatted
    
    def chat_completion(
        self,
        model: str,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> ChatCompletion:
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": model,
            "messages": self._format_messages(messages),
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        
        for key in ["top_p", "frequency_penalty", "presence_penalty"]:
            if key in kwargs and kwargs[key] is not None:
                payload[key] = kwargs[key]
        
        response = self._make_request(
            url=url,
            method="POST",
            headers=self._get_headers(),
            data=payload,
        )
        
        return self._parse_completion_response(response)
    
    def stream_chat(
        self,
        model: str,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> Generator[str, None, None]:
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": model,
            "messages": self._format_messages(messages),
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        
        for key in ["top_p", "frequency_penalty", "presence_penalty"]:
            if key in kwargs and kwargs[key] is not None:
                payload[key] = kwargs[key]
        
        response = self._make_request(
            url=url,
            method="POST",
            headers=self._get_headers(),
            data=payload,
            stream=True,
        )
        
        for line in self._read_sse_stream(response):
            if line.startswith("data: "):
                data_str = line[6:]
                if data_str.strip() == "[DONE]":
                    break
                try:
                    data = json.loads(data_str)
                    delta = data.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        yield content
                except json.JSONDecodeError:
                    continue
    
    def _parse_completion_response(self, response: Dict[str, Any]) -> ChatCompletion:
        choice = response.get("choices", [{}])[0]
        message = choice.get("message", {})
        usage = response.get("usage", {})
        
        return ChatCompletion(
            content=message.get("content", ""),
            model=response.get("model", ""),
            role=message.get("role", "assistant"),
            finish_reason=choice.get("finish_reason", "stop"),
            total_tokens=usage.get("total_tokens", 0),
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
        )
    
    def _read_sse_stream(self, response) -> Generator[str, None, None]:
        buffer = b""
        for chunk in iter(lambda: response.read(1024), b""):
            buffer += chunk
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                try:
                    yield line.decode("utf-8")
                except UnicodeDecodeError:
                    continue
    
    def _extract_error_message(self, error_json: Dict[str, Any], status_code: int) -> str:
        error = error_json.get("error", {})
        if isinstance(error, dict):
            message = error.get("message", str(error_json))
            error_type = error.get("type", "")
            if error_type:
                return f"[{error_type}] {message}"
            return message
        return str(error_json)


class AnthropicProvider(AIProvider):
    DEFAULT_BASE_URL = "https://api.anthropic.com/v1"
    API_VERSION = "2023-06-01"
    
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: int = 60,
    ):
        super().__init__(
            api_key=api_key,
            base_url=base_url or self.DEFAULT_BASE_URL,
            timeout=timeout,
        )
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            "x-api-key": self.api_key,
            "anthropic-version": self.API_VERSION,
            "Content-Type": "application/json",
        }
    
    def _format_messages(
        self, 
        messages: List[ChatMessage]
    ) -> tuple[List[Dict[str, Any]], Optional[str]]:
        formatted_messages = []
        system_prompt = None
        
        for msg in messages:
            if isinstance(msg, ChatMessage):
                role = msg.role
                content = msg.content
            elif isinstance(msg, dict):
                role = msg.get("role", "")
                content = msg.get("content", "")
            else:
                continue
            
            if role == "system":
                system_prompt = content
            else:
                if formatted_messages and formatted_messages[-1]["role"] == role:
                    formatted_messages[-1]["content"] += "\n" + content
                else:
                    formatted_messages.append({"role": role, "content": content})
        
        return formatted_messages, system_prompt
    
    def chat_completion(
        self,
        model: str,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> ChatCompletion:
        url = f"{self.base_url}/messages"
        
        formatted_messages, system_prompt = self._format_messages(messages)
        
        payload = {
            "model": model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        response = self._make_request(
            url=url,
            method="POST",
            headers=self._get_headers(),
            data=payload,
        )
        
        return self._parse_completion_response(response)
    
    def stream_chat(
        self,
        model: str,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> Generator[str, None, None]:
        url = f"{self.base_url}/messages"
        
        formatted_messages, system_prompt = self._format_messages(messages)
        
        payload = {
            "model": model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        response = self._make_request(
            url=url,
            method="POST",
            headers=self._get_headers(),
            data=payload,
            stream=True,
        )
        
        for line in self._read_sse_stream(response):
            if line.startswith("event: "):
                event_type = line[7:]
                if event_type == "message_stop":
                    break
            elif line.startswith("data: "):
                data_str = line[6:]
                try:
                    data = json.loads(data_str)
                    event_type = data.get("type", "")
                    
                    if event_type == "content_block_delta":
                        delta = data.get("delta", {})
                        content = delta.get("text", "")
                        if content:
                            yield content
                    elif event_type == "message_delta":
                        delta = data.get("delta", {})
                        if "stop_reason" in delta:
                            break
                            
                except json.JSONDecodeError:
                    continue
    
    def _parse_completion_response(self, response: Dict[str, Any]) -> ChatCompletion:
        content_parts = []
        for block in response.get("content", []):
            if block.get("type") == "text":
                content_parts.append(block.get("text", ""))
        
        usage = response.get("usage", {})
        
        return ChatCompletion(
            content="".join(content_parts),
            model=response.get("model", ""),
            role="assistant",
            finish_reason=response.get("stop_reason", "stop"),
            total_tokens=usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
            prompt_tokens=usage.get("input_tokens", 0),
            completion_tokens=usage.get("output_tokens", 0),
        )
    
    def _read_sse_stream(self, response) -> Generator[str, None, None]:
        buffer = b""
        for chunk in iter(lambda: response.read(1024), b""):
            buffer += chunk
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                try:
                    yield line.decode("utf-8")
                except UnicodeDecodeError:
                    continue
    
    def _extract_error_message(self, error_json: Dict[str, Any], status_code: int) -> str:
        error = error_json.get("error", {})
        if isinstance(error, dict):
            message = error.get("message", str(error_json))
            error_type = error.get("type", "")
            if error_type:
                return f"[{error_type}] {message}"
            return message
        return str(error_json)


class OllamaProvider(AIProvider):
    DEFAULT_BASE_URL = "http://localhost:11434"
    
    def __init__(
        self,
        api_key: str = "ollama-local",
        base_url: Optional[str] = None,
        timeout: int = 120,
    ):
        super().__init__(
            api_key=api_key,
            base_url=base_url or self.DEFAULT_BASE_URL,
            timeout=timeout,
        )
    
    def _validate_api_key(self) -> None:
        pass
    
    def _format_messages(self, messages: List[ChatMessage]) -> List[Dict[str, Any]]:
        formatted = []
        for msg in messages:
            if isinstance(msg, ChatMessage):
                formatted.append({"role": msg.role, "content": msg.content})
            elif isinstance(msg, dict):
                formatted.append(msg)
        return formatted
    
    def chat_completion(
        self,
        model: str,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> ChatCompletion:
        url = f"{self.base_url}/api/chat"
        
        options = {"temperature": temperature, "num_predict": max_tokens}
        
        for key in ["top_p", "frequency_penalty", "presence_penalty"]:
            if key in kwargs and kwargs[key] is not None:
                options[key] = kwargs[key]
        
        payload = {
            "model": model,
            "messages": self._format_messages(messages),
            "options": options,
            "stream": False,
        }
        
        response = self._make_request(
            url=url,
            method="POST",
            headers={"Content-Type": "application/json"},
            data=payload,
        )
        
        return self._parse_completion_response(response)
    
    def stream_chat(
        self,
        model: str,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> Generator[str, None, None]:
        url = f"{self.base_url}/api/chat"
        
        options = {"temperature": temperature, "num_predict": max_tokens}
        
        for key in ["top_p", "frequency_penalty", "presence_penalty"]:
            if key in kwargs and kwargs[key] is not None:
                options[key] = kwargs[key]
        
        payload = {
            "model": model,
            "messages": self._format_messages(messages),
            "options": options,
            "stream": True,
        }
        
        response = self._make_request(
            url=url,
            method="POST",
            headers={"Content-Type": "application/json"},
            data=payload,
            stream=True,
        )
        
        for line in self._read_stream_lines(response):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                message = data.get("message", {})
                content = message.get("content", "")
                if content:
                    yield content
                if data.get("done", False):
                    break
            except json.JSONDecodeError:
                continue
    
    def _parse_completion_response(self, response: Dict[str, Any]) -> ChatCompletion:
        message = response.get("message", {})
        
        return ChatCompletion(
            content=message.get("content", ""),
            model=response.get("model", ""),
            role=message.get("role", "assistant"),
            finish_reason="stop" if response.get("done", False) else "unknown",
            total_tokens=response.get("eval_count", 0) + response.get("prompt_eval_count", 0),
            prompt_tokens=response.get("prompt_eval_count", 0),
            completion_tokens=response.get("eval_count", 0),
        )
    
    def _read_stream_lines(self, response) -> Generator[str, None, None]:
        buffer = b""
        for chunk in iter(lambda: response.read(1024), b""):
            buffer += chunk
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                try:
                    yield line.decode("utf-8")
                except UnicodeDecodeError:
                    continue
    
    def _extract_error_message(self, error_json: Dict[str, Any], status_code: int) -> str:
        error = error_json.get("error", "")
        if error:
            return error
        message = error_json.get("message", str(error_json))
        return message


def get_ai_provider(
    provider_name: str,
    api_key: str,
    base_url: Optional[str] = None,
    timeout: int = 60,
) -> AIProvider:
    provider_name = provider_name.lower().replace(" ", "")
    
    if provider_name in ["openai", "openai-provider"]:
        return OpenAIProvider(api_key=api_key, base_url=base_url, timeout=timeout)
    elif provider_name in ["anthropic", "anthropic-provider", "claude"]:
        return AnthropicProvider(api_key=api_key, base_url=base_url, timeout=timeout)
    elif provider_name in ["ollama", "local", "ollama-provider"]:
        return OllamaProvider(api_key=api_key, base_url=base_url, timeout=timeout)
    else:
        raise ValueError(f"Unknown provider: {provider_name}. Choose from: OpenAI, Anthropic, Ollama")
