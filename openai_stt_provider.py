from openai import OpenAI
from stt_provider import STTProvider

class OpenAISTTProvider(STTProvider):
    def __init__(self):
        self.client = OpenAI()
        self.model_names = []

    def list_models(self):
        if not self.model_names:
            models = self.client.models.list()
            models.data = [m for m in models.data if 'whisper' in m.id]
            models.data.sort(key=lambda x: x.created, reverse=True)
            self.model_names = [m.id for m in models.data]
        return self.model_names

    def speech_to_text(self, model, audio_file):
        with open(audio_file, "rb") as audio:
            transcript = self.client.audio.transcriptions.create(
                model=model if model else 'whisper-1',
                file=audio,
                response_format="text"
            )
        return str(transcript)