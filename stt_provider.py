# ai_provider_base.py

from abc import ABC, abstractmethod

class STTProvider(ABC):
    @abstractmethod
    def list_models(self):
        pass

    @abstractmethod
    def speech_to_text(self, model, audio_file):
        pass

def get_stt_providers():
    providers = []
    from openai_stt_provider import OpenAISTTProvider
    providers.append(OpenAISTTProvider())
    return providers