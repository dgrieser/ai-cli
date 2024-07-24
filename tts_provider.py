import utils
from enum import Enum
from abc import ABC, abstractmethod

class TTSProvider(ABC):

    class Format(Enum):
        WAV = 1
        MP3 = 2

    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def channels(self):
        pass

    @abstractmethod
    def samplerate(self):
        pass

    @abstractmethod
    def dtype(self):
        pass

    @abstractmethod
    def volumegain(self):
        return 8

    @abstractmethod
    def blocksize(self):
        pass

    @abstractmethod
    def format(self) -> Format:
        pass

    @abstractmethod
    def _list_models(self):
        pass

    def list_models(self, cache_directory_path):
        return utils.list_models(self.name(), self._list_models, cache_directory_path)

    @abstractmethod
    def text_to_speech(self, text, model, voice, speed, audio_file):
        pass

    @abstractmethod
    def text_to_speech_stream(self, text, model, voice, speed, virtual_audio_file):
        pass

def get_tts_providers():
    providers = []
    from openai_tts_provider import OpenAITTSProvider
    providers.append(OpenAITTSProvider())
    return providers