import time
from meta_ai_api import MetaAI
from ai_provider import AIProvider

class MetaAiProvider(AIProvider):
    def __init__(self):
        self.client = MetaAI()
        self.model_names = [ 'meta-ai-web' ]

    def name(self):
        return "meta-ai"

    def _list_models(self):
        return self.model_names

    def chat_completion(self, messages, model, stream=False):
        prompt = messages[-1].get('content', '')
        return self.client.prompt(message=prompt, stream=stream)

    def convert_result_to_text(self, result, sources, handle_metadata_func):
        text = result.get('message', '')
        sources = result.get('sources', [])
        if len(sources) > 0:
            text += "\n\nSources:"
        for s in sources:
            text += "\n"
            text += f"{s.get('title', '')}: {s.get('link', '')}\n"

    def convert_chunk_to_text(self, chunk, sources, handle_metadata_func):
        # TODO: chunks are iterative, need to handle that
        return chunk.get('message', '')

    def close(self):
        pass