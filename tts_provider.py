# ai_provider_base.py

from abc import ABC, abstractmethod

class TTSProvider(ABC):
    @abstractmethod
    def list_models(self):
        pass

    @abstractmethod
    def text_to_speech(self, text, model, voice, speed, audio_file):
        pass

def get_tts_providers():
    providers = []
    from openai_tts_provider import OpenAITTSProvider
    providers.append(OpenAITTSProvider())
    return providers