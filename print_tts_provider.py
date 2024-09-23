import os
from tts_provider import TTSProvider
from byte_queue_file import ByteQueueFile

class PrintTTSProvider(TTSProvider):
    def __init__(self):
        self.model_names = [ "printer" ]
        self.voice = [ "text" ]

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

    def default_voice(self):
        return self.voice[0]

    def default_model(self):
        return self.model_names[0]

    def _list_models(self):
        return self.model_names

    def _list_voices(self):
        return self.voices

    def get_response(self, text, model, voice_id, speed):
        pass

    def text_to_speech(self, text, model, voice_id, speed, audio_file):
        print(f'({len(text)}): {text}')
        if audio_file is not None and os.path.exists(audio_file):
            os.remove(audio_file)

    def text_to_speech_stream(self, text, model, voice_id, speed, virtual_audio_file: ByteQueueFile):
        print(f'({len(text)}): {text}')
        virtual_audio_file.close()