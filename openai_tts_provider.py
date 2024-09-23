from openai import OpenAI
from tts_provider import TTSProvider
from byte_queue_file import ByteQueueFile

TTS_CHUNK_SIZE = 2048

class OpenAITTSProvider(TTSProvider):
    def __init__(self):
        self.client = OpenAI()
        self.model_names = []

    def name(self):
        return 'openai-tts'

    def channels(self):
        return 1

    def samplerate(self):
        return 24000

    def dtype(self):
        return 'float32'

    def format(self):
        return TTSProvider.Format.MP3

    def volumegain(self):
        return 8

    def blocksize(self):
        return TTS_CHUNK_SIZE

    def max_length(self):
        return 4096

    def default_voice(self):
        return 'nova'

    def default_model(self):
        return 'tts-1'

    def _list_models(self):
        if not self.model_names:
            models = self.client.models.list()
            models.data = [m for m in models.data if 'tts' in m.id]
            models.data.sort(key=lambda x: x.created, reverse=True)
            self.model_names = [m.id for m in models.data]
        return self.model_names

    def _list_voices(self):
        return [ 'alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer' ]

    def get_response(self, text, model, voice_id, speed):
        return self.client.audio.speech.with_streaming_response.create(
            model=model if model else self.default_model(),
            voice=voice_id,
            response_format='mp3',
            speed=str(speed),
            input=text
        )

    def text_to_speech(self, text, model, voice_id, speed, audio_file):
        with self.get_response(text, model, voice_id, speed) as response:
            with open(audio_file, "wb") as file:
                for chunk in response.iter_bytes(chunk_size=TTS_CHUNK_SIZE):
                    file.write(chunk)

    def text_to_speech_stream(self, text, model, voice_id, speed, virtual_audio_file: ByteQueueFile):
        with self.get_response(text, model, voice_id, speed) as response:
            for chunk in response.iter_bytes(chunk_size=TTS_CHUNK_SIZE):
                virtual_audio_file.write(chunk)
            virtual_audio_file.close()