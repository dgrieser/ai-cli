import time
from openai import OpenAI
from ai_provider import AIProvider

class OpenAIProvider(AIProvider):
    def __init__(self):
        self.client = OpenAI()
        self.model_names = []

    def name(self):
        return 'openai'

    def supports_sessions(self):
        return True

    def _list_models(self):
        if not self.model_names:
            models = self.client.models.list()
            models.data = [m for m in models.data if 'gpt' in m.id]
            models.data.sort(key=lambda x: x.created, reverse=True)
            self.model_names = [m.id for m in models.data]
        return self.model_names

    def chat_completion(self, messages, model, stream=False):
        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            stream=stream,
        )

    def convert_result_to_text(self, result, sources, handle_metadata_func):
        text = result.choices[0].message.content
        if handle_metadata_func:
            handle_metadata_func("ID", str(result.id))
            handle_metadata_func("Creation", time.strftime('%Y-%m-%dT%H:%M:%S%z', time.gmtime(result.created)))
            handle_metadata_func("Choices", str(len(result.choices)))
            handle_metadata_func("Model", result.model)
            handle_metadata_func("Tokens", str(result.usage.total_tokens))
        return text

    def convert_chunk_to_text(self, chunk, sources, handle_metadata_func):
        if handle_metadata_func:
            handle_metadata_func("ID", str(chunk.id))
            handle_metadata_func("Creation", time.strftime('%Y-%m-%dT%H:%M:%S%z', time.gmtime(chunk.created)))
            handle_metadata_func("Choices", str(len(chunk.choices)))
            handle_metadata_func("Model", chunk.model)
        return chunk.choices[0].delta.content

    def close(self):
        pass