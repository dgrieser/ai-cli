import os
import json
import re
import sys
import threading
from perplexity import Perplexity
from ai_provider import AIProvider

model_name_regular = 'perplexity'
model_name_pro = 'perplexity-pro'

mode_regular = 'concise'
mode_pro = 'copilot'

session_file = '.perplexity_session'

class PerplexityAiProvider(AIProvider):
    def __init__(self):
        # lazy init, see create_client()
        self.client = None
        self.model_names = [model_name_regular, model_name_pro]

    def create_client(self):
        if self.client is None:
            # HACK: beautiful code which we handle beautifully here :trollface:
            t = threading.Thread(target=self.init_perplexity)
            t.start()
            t.join(timeout=60)
            if t.is_alive():
                raise TimeoutError("Failed to initialize Perplexity API")

    def init_perplexity(self):
        original_dir = os.getcwd()
        retries = 0
        try:
            while retries < 3:
                try:
                    os.chdir(os.path.expanduser("~"))
                    email = os.environ.get('PERPLEXITY_EMAIL', '')
                    if email:
                        if not os.path.exists(session_file):
                            print(f'Perplexity login via {email}, ', end='')
                        self.client = Perplexity(email)
                    else:
                        self.client = Perplexity()

                    break
                except Exception as e:
                    print(f"ERROR: Failed to initialize Perplexity API: {e}, retrying...", file=sys.stderr)
                    if email and os.path.exists(session_file):
                        # delete .perplexity_session, maybe token expired
                        os.remove(session_file)
        finally:
            os.chdir(original_dir)

        if self.client is None:
            raise Exception("Failed to initialize Perplexity API")

    def name(self):
        return "perplexity"

    def _list_models(self):
        return self.model_names

    def chat_completion(self, messages, model, stream=False):
        self.create_client()

        prompt = messages[-1].get('content', '')
        mode = mode_regular
        if model == model_name_pro:
            mode = mode_pro
        result = self.client.search(query=prompt, mode=mode)
        if mode == mode_pro:
            # pro was reguested, check if API responded with it
            if not result is None:
                first_result = next(iter(result))
                if 'mode' in first_result:
                    used_mode = first_result.get('mode', '')
                    if used_mode is not None and used_mode != mode_pro:
                        print(f"WARNING: {model_name_pro} was requested but API responded with regular model. Either you are not logged in or your quota was reached. Set evnironment variable 'PERPLEXITY_EMAIL' to use {model_name_pro}.", file=sys.stderr)
                        print('', file=sys.stderr)

        return result

    def __handle_metadata(self, chunk, handle_metadata_func):
        if handle_metadata_func:
            handle_metadata_func("UUID", str(chunk.get('uuid', '')))
            handle_metadata_func("Status", str(chunk.get('status', '')))
            handle_metadata_func("Mode", str(chunk.get('mode', '')))
            handle_metadata_func("Focus", str(chunk.get('search_focus', '')))
            queries = str("', '".join(chunk.get('related_queries', [])))
            if queries:
                handle_metadata_func("Queries", "'" + queries + "'")

    def convert_result_to_text(self, result, sources, handle_metadata_func):
        text = ''
        last_chunk = None
        for chunk in result:
            if not last_chunk:
                self.__handle_metadata(chunk, handle_metadata_func)
            text += self.convert_chunk_to_text(chunk, sources, None)
            last_chunk = chunk
        if last_chunk:
            self.__handle_metadata(last_chunk, handle_metadata_func)

        return text

    def __extract_text_from_chunk(self, chunk):
        text = ''
        ok = False
        if isinstance(chunk, dict) and 'chunks' in chunk:
            ok = True
            chunks = chunk.get('chunks', [])
            if len(chunks) > 0:
                text = chunks[-1]
        return ok, text

    def remove_source_references(self, text):
        if not text is None and isinstance(text, str):
            # use regex to remove source references, e.g. '[1]'
            text = re.sub(r'\[[1-9][0-9]*\]', '', text)
        return text

    def __extract_copilot_answer(self, step):
        if 'content' in step:
            content = step.get('content', {})
            if 'answer' in content:
                answer = content.get('answer', {})
                if isinstance(answer, str):
                    answer = json.loads(answer)
                return answer
            else:
                return content

        return None

    def convert_chunk_to_text(self, chunk, sources, handle_metadata_func):
        text = ''
        self.__handle_metadata(chunk, handle_metadata_func)

        parts = [ chunk ]
        if 'copilot_answer' in chunk:
            # unpack copilot steps
            copilot_answer = chunk.get('copilot_answer', [])
            if len(copilot_answer) > 0:
                for step in copilot_answer:
                    extracted_part = self.__extract_copilot_answer(step)
                    if extracted_part:
                        parts.append(extracted_part)

        for part in parts:
            current_part = part
            ok, text = self.__extract_text_from_chunk(current_part)
            if not ok and 'text' in current_part:
                # for the last part, the remaining chunks and web_results seem to be in 'text'
                text_value = current_part.get('text', {})
                if isinstance(text_value, str):
                    try:
                        text_value = json.loads(text_value)
                    except:
                        pass
                if not text_value is None:
                    if isinstance(text_value, dict):
                        current_part = text_value
                        ok, text = self.__extract_text_from_chunk(current_part)
                    elif isinstance(text_value, list):
                        # looks like copilot steps
                        last_step = text_value[-1]
                        current_part = self.__extract_copilot_answer(last_step)
                        ok, text = self.__extract_text_from_chunk(current_part)

            if sources is not None:
                mode = current_part.get('mode', '')
                model_title = 'Perplexity'
                if mode == mode_pro:
                    model_title = 'Perplexity Pro'
                thread_url_slug = current_part.get('thread_url_slug', '')
                if thread_url_slug:
                    url = f'https://perplexity.ai/search/{thread_url_slug}'
                    thread_title = current_part.get('thread_title', '')
                    if not url in sources:
                        sources[url] = f'{model_title}: {thread_title}'

                web_results = current_part.get('web_results', [])
                web_results.extend(current_part.get('extra_web_results', []))
                if len(web_results) > 0:
                    for w in web_results:
                        url = w.get('url', '')
                        if not url in sources:
                            name = f'[{len(sources) + 1}] {w.get('name', '')}'
                            sources[url] = name
        return text

    def close(self):
        if self.client is not None:
            original_dir = os.getcwd()
            try:
                os.chdir(os.path.expanduser("~"))
                self.client.close()
                self.client = None
            finally:
                os.chdir(original_dir)