import os
import json
from perplexity import Perplexity
from ai_provider import AIProvider

pro_model = 'perplexity-pro'

class PerplexityAiProvider(AIProvider):
    def __init__(self):
        email = os.environ.get('PERPLEXITY_EMAIL', '')
        if email:
            self.client = Perplexity(email)
        else:
            self.client = Perplexity()
        self.model_names = [ 'perplexity', pro_model ]

    def list_models(self):
        return self.model_names

    def chat_completion(self, messages, model, stream=False):
        prompt = messages[-1].get('content', '')
        mode = 'concise'
        if model == pro_model:
            mode = 'copilot'
        return self.client.search(query=prompt, mode=mode)
    
    def __handle_metadata(self, chunk, handle_metadata_func):
        if handle_metadata_func:
            handle_metadata_func("UUID", str(chunk.get('uuid', '')))
            handle_metadata_func("Status", str(chunk.get('status', '')))
            handle_metadata_func("Mode", str(chunk.get('mode', '')))
            handle_metadata_func("Focus", str(chunk.get('search_focus', '')))
            plan = str(chunk.get('plan', ''))
            if plan and plan != 'None':
                handle_metadata_func("Plan", str(chunk.get('plan', '')))
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
    
    def convert_chunk_to_text(self, chunk, sources, handle_metadata_func):
        text = ''
        self.__handle_metadata(chunk, handle_metadata_func)

        # TODO: fix copilot mode

        parts = [ chunk ]
        if 'copilot_answer' in chunk:
            copilot_answer = chunk.get('copilot_answer', [])
            if len(copilot_answer) > 0:
                for a in copilot_answer:
                    if 'content' in a:
                        content = a.get('content', {})
                        if 'answer' in content:
                            parts.append(content.get('answer', {}))
                        else:
                            parts.append(content)

        for part in parts:
            text_chunks = part.get('chunks', [])
            if len(text_chunks) > 0:
                text = text_chunks[-1]

            if sources is not None:
                thread_url_slug = part.get('thread_url_slug', '')
                if thread_url_slug:
                    url = f'https://perplexity.ai/search/{thread_url_slug}'
                    thread_title = part.get('thread_title', '')
                    if not url in sources:
                        sources[url] = f'Perplexity: {thread_title}'

                web_results = part.get('web_results', [])
                web_results.extend(part.get('extra_web_results', []))
                if len(web_results) > 0:
                    for w in web_results:
                        url = w.get('url', '')
                        if not url in sources:
                            name = f'[{len(sources) + 1}] {w.get('name', '')}'
                            sources[url] = name
        return text

    def close(self):
        self.client.close()