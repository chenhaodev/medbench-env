# runner/clients.py
import anthropic
import openai


class AnthropicClient:
    def __init__(self, api_key: str):
        self._client = anthropic.Anthropic(api_key=api_key)

    def query(self, question: str, model: str, max_tokens: int = 2048) -> str:
        try:
            response = self._client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": question}],
            )
            return response.content[0].text
        except Exception as e:
            return f"ERROR: {e}"


class DeepSeekClient:
    DEEPSEEK_BASE_URL = "https://api.deepseek.com"

    def __init__(self, api_key: str):
        self._client = openai.OpenAI(
            api_key=api_key,
            base_url=self.DEEPSEEK_BASE_URL,
        )

    def query(self, question: str, model: str, max_tokens: int = 2048) -> str:
        try:
            response = self._client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": question}],
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"ERROR: {e}"
