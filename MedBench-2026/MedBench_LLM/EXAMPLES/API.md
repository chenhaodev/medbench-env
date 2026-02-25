import openai

client = openai.OpenAI(
    api_key = "YOUR_POE_API_KEY",  # or os.getenv("POE_API_KEY")
    base_url = "https://api.poe.com/v1",
)

chat = client.chat.completions.create(
    model = "claude-sonnet-4.5", #or gpt-5.1, gemini-3-pro
    messages = [{"role": "user", "content": "Hello world"}]
)

print(chat.choices[0].message.content)
