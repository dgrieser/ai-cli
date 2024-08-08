from ai_provider import AIProvider

class PassthroughProvider(AIProvider):
    def __init__(self):
        self.model_names = [ 'passthrough' ]

    def name(self):
        return 'passthrough'

    def _list_models(self):
        return self.model_names

    def supports_sessions(self):
        return False

    def chat_completion(self, messages, model, stream=False):
        result = []
        for m in messages:
            if m.get('role', '') == 'user':
                result.append(m.get('content', ''))
        return result

    def convert_result_to_text(self, result, sources, handle_metadata_func):
        text = '\n'.join(result)
        return text

    def convert_chunk_to_text(self, chunk, sources, handle_metadata_func):
        return chunk

    def close(self):
        pass