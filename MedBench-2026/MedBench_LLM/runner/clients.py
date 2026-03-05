# runner/clients.py
import time
import anthropic
import openai

_RETRY_DELAYS = [5, 15, 30]  # seconds between retries


class AnthropicClient:
    def __init__(self, api_key: str):
        self._client = anthropic.Anthropic(api_key=api_key)

    def query(self, question: str, model: str, max_tokens: int = 4096) -> str:
        for attempt, delay in enumerate([0] + _RETRY_DELAYS):
            if delay:
                time.sleep(delay)
            try:
                response = self._client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": question}],
                )
                return response.content[0].text
            except anthropic.RateLimitError as e:
                if attempt == len(_RETRY_DELAYS):
                    return f"ERROR: {e}"
            except anthropic.APIStatusError as e:
                if e.status_code == 403 and attempt < len(_RETRY_DELAYS):
                    continue  # retry on transient 403
                return f"ERROR: {e}"
            except Exception as e:
                return f"ERROR: {e}"
        return "ERROR: max retries exceeded"


class DeepSeekClient:
    DEEPSEEK_BASE_URL = "https://api.deepseek.com"

    def __init__(self, api_key: str):
        self._client = openai.OpenAI(
            api_key=api_key,
            base_url=self.DEEPSEEK_BASE_URL,
        )

    def query(self, question: str, model: str, max_tokens: int = 4096) -> str:
        try:
            response = self._client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": question}],
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"ERROR: {e}"
