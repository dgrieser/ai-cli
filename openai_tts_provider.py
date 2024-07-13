# openai_provider.py

import subprocess
from openai import OpenAI
from tts_provider import TTSProvider

TTS_CHUNK_SIZE = 1024

class OpenAITTSProvider(TTSProvider):
    def __init__(self):
        self.client = OpenAI()
        self.model_names = []

    def list_models(self):
        if not self.model_names:
            models = self.client.models.list()
            models.data = [m for m in models.data if 'tts' in m.id]
            models.data.sort(key=lambda x: x.created, reverse=True)
            self.model_names = [m.id for m in models.data]
        return self.model_names
    
    def text_to_speech(self, text, model, voice, speed, audio_file):
        with self.client.audio.speech.with_streaming_response.create(
            model=model if model else 'tts-1',
            voice=voice if voice else 'nova',
            speed=str(speed),
            input=text
        ) as response:
            with open(audio_file, "wb") as file:
                for chunk in response.iter_bytes(chunk_size=TTS_CHUNK_SIZE):
                    file.write(chunk)

        try:
            subprocess.run(["mp3gain", "-g", "8", audio_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"WARNING: Failed to run mp3gain: {e}")