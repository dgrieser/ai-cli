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
    def max_length(self):
        pass

    @abstractmethod
    def _list_models(self):
        pass

    @abstractmethod
    def default_voice(self):
        pass

    @abstractmethod
    def default_model(self):
        pass

    @abstractmethod
    def _list_voices(self):
        pass

    def allows_list_caching(self):
        return True

    def list_models(self, cache_directory_path):
        return utils.list_models(self.name(), self._list_models, self.allows_list_caching(), cache_directory_path)

    def list_voices(self, cache_directory_path):
        return utils.list_voices(self.name(), self._list_voices, self.allows_list_caching(), cache_directory_path)

    def get_voice_name(self, voice):
        return voice.split('\t')[1] if '\t' in voice else voice

    def get_voice_id(self, voice):
        return voice.split('\t')[0] if '\t' in voice else voice

    def get_voice_by_name(self, voice_name, cache_directory_path):
        if voice_name:
            for voice in self.list_voices(cache_directory_path):
                name = self.get_voice_name(voice)
                if name == voice_name:
                    return voice
        return self.default_voice()

    @abstractmethod
    def text_to_speech(self, text, model, voice_id, speed, audio_file):
        pass

    @abstractmethod
    def text_to_speech_stream(self, text, model, voice_id, speed, virtual_audio_file):
        pass

    @abstractmethod
    def get_response(self, text, model, voice_id, speed):
        pass

    def close(self):
        pass

def get_tts_providers():
    providers = []
    from openai_tts_provider import OpenAITTSProvider
    providers.append(OpenAITTSProvider())
    from elevenlabs_tts_provider import ElevenLabsTTSProvider
    providers.append(ElevenLabsTTSProvider())
    from playht_tts_provider import PlayHTProvider
    providers.append(PlayHTProvider())
    from print_tts_provider import PrintTTSProvider
    providers.append(PrintTTSProvider())
    return providers