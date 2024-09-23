import utils
from abc import ABC, abstractmethod

class STTProvider(ABC):

    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def _list_models(self):
        pass

    def list_models(self, cache_directory_path):
        return utils.list_models(self.name(), self._list_models, True, cache_directory_path)

    @abstractmethod
    def speech_to_text(self, model, audio_file):
        pass

def get_stt_providers():
    providers = []
    from openai_stt_provider import OpenAISTTProvider
    providers.append(OpenAISTTProvider())
    return providers