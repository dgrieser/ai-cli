import utils
from abc import ABC, abstractmethod

class AIProvider(ABC):

    @abstractmethod
    def name(self):
        pass

    def supports_sessions(self):
        return False

    @abstractmethod
    def _list_models(self):
        pass

    def list_models(self, cache_directory_path):
        return utils.list_models(self.name(), self._list_models, True, cache_directory_path)

    @abstractmethod
    def chat_completion(self, messages, model, stream=False):
        pass

    @abstractmethod
    def convert_result_to_text(self, result, sources, handle_metadata_func):
        pass

    @abstractmethod
    def convert_chunk_to_text(self, chunk, sources, handle_metadata_func):
        pass

    def remove_source_references(self, text):
        return text

    @abstractmethod
    def close(self):
        pass

def get_ai_providers():
    providers = []
    from passthrough_ai_provider import PassthroughProvider
    providers.append(PassthroughProvider())
    from openai_ai_provider import OpenAIProvider
    providers.append(OpenAIProvider())
    from anthropic_ai_provider import AnthropicAIProvider
    providers.append(AnthropicAIProvider())
    from perplexity_ai_provider import PerplexityAiProvider
    providers.append(PerplexityAiProvider())
    return providers