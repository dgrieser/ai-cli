from elevenlabs.client import ElevenLabs
from tts_provider import TTSProvider
from byte_queue_file import ByteQueueFile

TTS_CHUNK_SIZE = 1024

class ElevenLabsTTSProvider(TTSProvider):
    def __init__(self):
        # reads API key from ELEVEN_API_KEY env variable
        self.client = ElevenLabs()
        self.model_names = []
        self.voices = []

    def name(self):
        return 'elevenlabs'

    def channels(self):
        return 1

    def samplerate(self):
        return 44100

    def dtype(self):
        return 'float32'

    def format(self):
        return TTSProvider.Format.MP3

    def volumegain(self):
        return 0

    def blocksize(self):
        return TTS_CHUNK_SIZE

    def max_length(self):
        return 5000

    def default_voice(self):
        return 'Brian'

    def default_model(self):
        return 'eleven_multilingual_v2'

    def _list_models(self):
        if not self.model_names:
            models = self.client.models.get_all()
            models.sort(key=lambda x: x.model_id, reverse=True)
            self.model_names = [m.model_id for m in models]
        return self.model_names

    def _list_voices(self):
        if not self.voices:
            items = self.client.voices.get_all().voices
            self.voices = [i.name for i in items]
            self.voices.sort()
        return self.voices

    def get_response(self, text, model, voice_id, speed, stream):
        if speed != 1.0:
            print(f"WARNING: {self.name()} provider does not support adjustable speed.")
        return self.client.generate(
            text=text,
            voice=voice_id,
            stream=stream,
            model=model if model else self.default_model(),
            output_format='mp3_44100_128'
        )

    def text_to_speech(self, text, model, voice_id, speed, audio_file):
        response = self.get_response(text, model, voice_id, speed, False)
        with open(audio_file, "wb") as f:
            for chunk in response:
                if chunk:
                    f.write(chunk)

    def text_to_speech_stream(self, text, model, voice_id, speed, virtual_audio_file: ByteQueueFile):
        response = self.get_response(text, model, voice_id, speed, True)
        for chunk in response:
            virtual_audio_file.write(chunk)
        virtual_audio_file.close()