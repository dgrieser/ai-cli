from num2words import num2words
from langdetect import detect_langs, detect
from num2words import CONVERTER_CLASSES
import re

URL_PATTERN = re.compile(r'https*:[^ ]+')

def get_supported_languages():
    return list(CONVERTER_CLASSES.keys())

def is_digit(char):
    return char.isdigit()

def detect_language(text):
    return detect(text)

def optimize_for_tts(text, lang_hint=None) -> tuple[str, str]:
    # Detect the language
    detected_lang = detect(text)

    for lang in detect_langs(text):
        print(lang.lang)
        print(type(lang.prob))
        print(lang.prob)

    # Get supported languages
    supported_langs = get_supported_languages()

    # Check if the detected language is supported by num2words
    if detected_lang in supported_langs:
        lang = detected_lang
    else:
        print(f"WARNING: Language '{detected_lang}' not supported, skipping TTS optimization.")
        return text, None

    lines = []
    lines.extend(text.splitlines())
    for i in range(len(lines)):
        lines[i] = convert_numbers_to_words_in_line(lines[i], lang)
        lines[i] = convert_symbols_to_words(lines[i], lang)
        lines[i] = replace_urls(lines[i], lang)

    return '\n'.join(lines), detected_lang

def replace_urls(text, lang):
    if lang == 'en':
        return URL_PATTERN.sub('(see link in the text)', text)
    elif lang == 'de':
        return URL_PATTERN.sub('(siehe Link im Text)', text)

    return text

def convert_symbols_to_words(text, lang):
    if lang == 'en':
        return text.replace('°C', 'degrees Celsius').replace('°F', 'degrees Fahrenheit')
    elif lang == 'de':
        return text.replace('°C', 'Grad Celsius').replace('°F', 'Grad Fahrenheit')

    return text

def convert_numbers_to_words_in_line(text, lang):
    result = []
    i = 0
    while i < len(text):
        if is_digit(text[i]):
            # Found a digit, let's extract the full number
            start = i
            while i < len(text) and is_digit(text[i]):
                i += 1

            before = text[start-1:start] if start > 0 else ''
            before_text = text[:start]
            next = text[i] if i < len(text) else ''
            next_next = text[i+1] if i+1 < len(text) else ''
            next_is_last = i == len(text) - 1 or text[i+1:].strip() == ''

            is_ordinal = next == '.' and not is_digit(next_next)
            is_start_ordinal = is_ordinal and (start == 0 or before_text.strip() == '')
            is_cardinal = (start == 0 or before_text.strip() == '' or before.isspace()) and (next.isspace() or (next_is_last and not next.isalpha()))

            number = text[start:i]
            ok = True

            try:
                num = int(number)
                if is_start_ordinal:
                    word = num2words(num, to='ordinal', lang=lang)
                    if lang == 'de':
                        # German ends with 'ns', e.g. 'erste' -> 'erstens'
                        word = word + 'ns'
                elif is_cardinal:
                    if num > 1000 and num < 2200:
                        word = num2words(num, to='year', lang=lang)
                    else:
                        word = num2words(num, to='cardinal', lang=lang)
                else:
                    ok = False

                if ok:
                    # Add a space before the word if it's not at the start and the previous char isn't a space
                    if result and not result[-1].isspace():
                        result.append(' ')
                    result.append(word)
            except (ValueError, NotImplementedError):
                ok = False

            if not ok:
                # keep the original number
                result.append(text[start:i])
        else:
            # Not a number, just add the character
            result.append(text[i])
            i += 1

    return ''.join(result)