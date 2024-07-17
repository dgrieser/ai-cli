import utils
from abc import ABC, abstractmethod

class TTSProvider(ABC):

    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def _list_models(self):
        pass

    def list_models(self, cache_directory_path):
        return utils.list_models(self.name(), self._list_models, cache_directory_path)

    @abstractmethod
    def text_to_speech(self, text, model, voice, speed, audio_file):
        pass

def get_tts_providers():
    providers = []
    from openai_tts_provider import OpenAITTSProvider
    providers.append(OpenAITTSProvider())
    return providers