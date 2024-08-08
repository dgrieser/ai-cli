import requests
from bs4 import BeautifulSoup
from anthropic import *
from ai_provider import AIProvider

class AnthropicAIProvider(AIProvider):
    def __init__(self):
        self.client = Anthropic()
        self.model_names = []

    def name(self):
        return "anthropic"

    def supports_sessions(self):
        return True

    def _list_models(self):
        if not self.model_names:
            # no api function, so hack
            try:
                response = requests.get('https://docs.anthropic.com/en/docs/about-claude/models')
                soup = BeautifulSoup(response.text, 'html.parser')
                code_elements = soup.find_all('code')
                modelSet = set()
                for code in code_elements:
                    text = code.get_text()
                    if ':' not in text and '@' not in text:
                        modelSet.add(text)
                self.model_names = list(reversed(sorted(modelSet)))
            except Exception as e:
                print(f"WARNING: Failed to retrieve anthropic model list: {e}")
        return self.model_names

    def chat_completion(self, messages, model, stream=False):
        system_message = ''
        conversation_messages = []
        for m in messages:
            if m.get('role', '') == 'system':
                system_message = m.get('content', '')
            else:
                conversation_messages.append(m)

        return self.client.messages.create(
            max_tokens=1024,
            model=model,
            messages=conversation_messages,
            system=system_message,
            stream=stream,
        )

    def convert_result_to_text(self, result, sources, handle_metadata_func):
        text = result.content[0].text if result and result.content and len(result.content) > 0 else ''
        if handle_metadata_func:
            handle_metadata_func("ID", str(result.id))
            handle_metadata_func("Model", result.model)
            handle_metadata_func("Usage", str(result.usage))
        return text

    def convert_chunk_to_text(self, event, sources, handle_metadata_func):
        text = ''
        if hasattr(event, 'message'):
            event = event.message

        if hasattr(event, 'delta'):
            if hasattr(event.delta, 'text'):
                text = event.delta.text
            elif hasattr(event.delta, 'partial_json'):
                text = event.delta.partial_json

        if handle_metadata_func:
            if hasattr(event, 'id'):
                handle_metadata_func("ID", str(event.id))
            if hasattr(event, 'model'):
                handle_metadata_func("Model", event.model)
            if hasattr(event, 'type'):
                handle_metadata_func("Type", event.type)
            if hasattr(event, 'usage'):
                handle_metadata_func("Usage", str(event.usage))
        return text

    def close(self):
        pass