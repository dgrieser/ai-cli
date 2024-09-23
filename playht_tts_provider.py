import utils
import os
import re
import requests
from pyht import Client, TTSOptions, Format
from tts_provider import TTSProvider
from byte_queue_file import ByteQueueFile

TTS_CHUNK_SIZE = 1024
VOICES_V1_URL = "https://api.play.ht/api/v1/getVoices"
VOICES_V2_URL = "https://api.play.ht/api/v2/voices"

class PlayHTProvider(TTSProvider):
    def __init__(self):
        self.client = None
        self.model_names = [ 'PlayHT2.0-turbo', 'PlayHT2.0', 'PlayHT1.0', 'Standard' ]
        self.voices = []

    def init(self):
        if not self.client:
            self.client = Client(os.environ['PLAY_HT_USER_ID'], os.environ['PLAY_HT_API_KEY'])

    def name(self):
        return 'playht'

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

    def _list_models(self):
        return self.model_names

    def _normalize_voice_name(self, name):
        name = re.sub(r"\s\([^)]*\)$", "", name)
        name = name.replace(" ", "-")
        return name

    def _extract_style(self, name):
        match = re.match(r"^.+\(([^)]+)\)$", name)
        if match:
            return match.group(1).strip().lower()

        return None

    def _has_attribute(self, voice, attribute):
        return attribute in voice and voice[attribute]

    def _list_voices(self):
        if not self.voices:
            headers = {
                "accept": "application/json",
                "AUTHORIZATION": os.environ['PLAY_HT_API_KEY'],
                "X-USER-ID": os.environ['PLAY_HT_USER_ID']
            }
            id_set = set()
            name_set = set()
            try:
                for voice in requests.get(VOICES_V2_URL, headers=headers).json():
                    ok, id, name = self._generate_id_and_name(id_set=id_set, name_set=name_set, dict=voice, id_key='id', lang_key='language_code', name_key='name', style_key='style', name_keys=[ 'voice_engine' ])
                    if not ok: continue
                    self.voices.append(f'{id}\t{name}')
                for voice in requests.get(VOICES_V1_URL, headers=headers).json().get('voices', []):
                    suffix = None
                    if self._has_attribute(voice, 'isNew'): suffix = 'new'
                    ok, id, name = self._generate_id_and_name(id_set=id_set, name_set=name_set, dict=voice, id_key='value', lang_key='languageCode', name_key='name', style_key=None, name_keys=[ 'voiceType', 'service' ], suffix=suffix)
                    if not ok: continue
                    self.voices.append(f'{id}\t{name}')
            except Exception as e:
                utils.print_error('Failed to list available voices:', e)

            self.voices.sort(key=lambda x: x.split('\t')[1])
        return self.voices

    def _generate_id_and_name(self, id_set: set, name_set: set, dict: dict, id_key: str, lang_key: str, name_key: str, style_key: str, name_keys: list, suffix: str = None) -> tuple[bool, str, str]:
        if not self._has_attribute(dict, id_key): return False, None, None
        id = dict[id_key]
        if id in id_set: return False, None, None

        name = []
        if self._has_attribute(dict, lang_key):
            name.append(dict[lang_key])
        style = None
        if self._has_attribute(dict, name_key):
            voice_name = dict[name_key]
            name.append(self._normalize_voice_name(voice_name))
            if style_key: # if style is requested, try to extract it from the name first
                style_from_name = self._extract_style(voice_name)
                if style_from_name and len(style_from_name) > 0:
                    style = style_from_name
        if style_key:
            if not style and self._has_attribute(dict, style_key): style = dict[style_key].lower()

        if style:
            name.append(style)

        for name_key in name_keys:
            if self._has_attribute(dict, name_key): name.append(dict[name_key].lower())

        if suffix:
            name.append(suffix)

        unique_name = self._get_unique_name(name_set, '-'.join(name))
        return True, id, unique_name

    def _get_unique_name(self, name_set, name_candidate):
        unique_name = name_candidate
        appendix = 1
        while unique_name in name_set:
            appendix += 1
            unique_name = f'{name_candidate}-{appendix}'
        name_set.add(unique_name)
        return unique_name

    def default_voice(self):
        return 's3://voice-cloning-zero-shot/ac9e2984-c7bb-44c8-8b6b-5c10728ad5cf/original/manifest.json'

    def default_model(self):
        return 'PlayHT2.0-turbo'

    def close(self):
        if self.client:
            self.client.close()
            self.client = None

    def get_response(self, text, model, voice_id, speed):
        self.init()
        return self.client.tts(
            text=text,
            voice_engine=model if model else self.default_model(),
            options=TTSOptions(
                format=Format.FORMAT_MP3,
                sample_rate=self.samplerate(),
                speed=speed,
                voice=voice_id
            )
        )

    def text_to_speech(self, text, model, voice_id, speed, audio_file):
        response = self.get_response(text, model, voice_id, speed)
        with open(audio_file, "wb") as f:
            for chunk in response:
                if chunk:
                    f.write(chunk)

    def text_to_speech_stream(self, text, model, voice_id, speed, virtual_audio_file: ByteQueueFile):
        response = self.get_response(text, model, voice_id, speed)
        for chunk in response:
            virtual_audio_file.write(chunk)
        virtual_audio_file.close()