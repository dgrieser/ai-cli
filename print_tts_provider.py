import os
from tts_provider import TTSProvider
from byte_queue_file import ByteQueueFile

class PrintTTSProvider(TTSProvider):
    def __init__(self):
        self.model_names = [ "printer" ]

    def name(self):
        return 'printer'

    def channels(self):
        raise NotImplementedError()

    def samplerate(self):
        raise NotImplementedError()

    def dtype(self):
        raise NotImplementedError()

    def format(self):
        raise NotImplementedError()

    def volumegain(self):
        raise NotImplementedError()

    def blocksize(self):
        raise NotImplementedError()

    def max_length(self):
        return 4096

    def _list_models(self):
        return self.model_names

    def get_response(self, text, model, voice, speed):
        print(len(text))
        return self.client.audio.speech.with_streaming_response.create(
            model=model if model else 'tts-1',
            voice=voice if voice else 'nova',
            response_format='mp3',
            speed=str(speed),
            input=text
        )

    def text_to_speech(self, text, model, voice, speed, audio_file):
        print(f'({len(text)}): {text}')
        if audio_file is not None and os.path.exists(audio_file):
            os.remove(audio_file)

    def text_to_speech_stream(self, text, model, voice, speed, virtual_audio_file: ByteQueueFile):
        print(f'({len(text)}): {text}')
        virtual_audio_file.close()