# tests/test_clients.py
from unittest.mock import patch, MagicMock
import pytest
from runner.clients import AnthropicClient, DeepSeekClient


def test_anthropic_client_returns_string():
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="test answer")]
    with patch("anthropic.Anthropic") as MockAnthropic:
        MockAnthropic.return_value.messages.create.return_value = mock_response
        client = AnthropicClient(api_key="test")
        result = client.query("What is 1+1?", model="claude-sonnet-4-6")
        assert result == "test answer"


def test_anthropic_client_error_returns_error_string():
    with patch("anthropic.Anthropic") as MockAnthropic:
        MockAnthropic.return_value.messages.create.side_effect = Exception("API error")
        client = AnthropicClient(api_key="test")
        result = client.query("question", model="claude-sonnet-4-6")
        assert result.startswith("ERROR:")


def test_deepseek_client_returns_string():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="deepseek answer"))]
    with patch("openai.OpenAI") as MockOpenAI:
        MockOpenAI.return_value.chat.completions.create.return_value = mock_response
        client = DeepSeekClient(api_key="test")
        result = client.query("What is 1+1?", model="deepseek-chat")
        assert result == "deepseek answer"


def test_deepseek_client_error_returns_error_string():
    with patch("openai.OpenAI") as MockOpenAI:
        MockOpenAI.return_value.chat.completions.create.side_effect = Exception("timeout")
        client = DeepSeekClient(api_key="test")
        result = client.query("question", model="deepseek-chat")
        assert result.startswith("ERROR:")
