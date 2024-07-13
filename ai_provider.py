from abc import ABC, abstractmethod

class AIProvider(ABC):
    @abstractmethod
    def list_models(self):
        pass

    @abstractmethod
    def chat_completion(self, messages, model, stream=False):
        pass

    @abstractmethod
    def convert_result_to_text(self, result, handle_metadata_func):
        pass

    @abstractmethod
    def convert_chunk_to_text(self, chunk, handle_metadata_func):
        pass

def get_ai_providers():
    providers = []
    from openai_provider import OpenAIProvider
    providers.append(OpenAIProvider())
    return providers