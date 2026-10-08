import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx
import ollama

from ai import AIError, ask_ai
from app import create_app
from database import ConversationChanged, load_messages, save_turn


class ChatTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = str(Path(self.tmp.name) / 'nested' / 'chat.db')
        self.app = create_app({'TESTING': True, 'SECRET_KEY': 'test-only', 'DATABASE': self.path})
        self.client = self.app.test_client()

    def post(self, client=None, **fields):
        return (client or self.client).post('/chat', json={'message': 'hello', 'mode': 'assistant', **fields})

    def test_isolation_history_and_new_chat(self):
        other = self.app.test_client()
        with patch('app.ask_ai', return_value='Hi') as model:
            self.assertEqual(self.post().status_code, 200)
            self.assertEqual(len(self.client.get('/history').json['messages']), 2)
            self.assertEqual(other.get('/history').json['messages'], [])
            self.post(other, message='separate')
            self.assertEqual(model.call_args.args[0], [{'role': 'user', 'content': 'separate'}])
            self.client.post('/new-chat')
            self.assertEqual(self.client.get('/history').json['messages'], [])
            self.assertEqual(len(other.get('/history').json['messages']), 2)

    def test_invalid_inputs_do_not_call_model(self):
        with patch('app.ask_ai') as model:
            for data in [None, [], {}, {'message': ''}, {'message': 12}, {'message': 'a'*8001},
                         {'message': 'hi', 'mode': []}, {'message': 'hi', 'mode': 'unknown'}]:
                self.assertEqual(self.client.post('/chat', json=data).status_code, 400)
            model.assert_not_called()

    def test_ai_failure_does_not_save_turn(self):
        with patch('app.ask_ai', side_effect=AIError('unavailable')):
            response = self.post()
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json, {'error': 'unavailable'})
        self.assertEqual(self.client.get('/history').json['messages'], [])

    def test_stale_turn_is_not_saved(self):
        save_turn(self.path, 'test', 'one', 'reply', 0)
        with self.assertRaises(ConversationChanged):
            save_turn(self.path, 'test', 'two', 'reply', 0)
        self.assertEqual(len(load_messages(self.path, 'test')), 2)

    def test_prompt_is_not_mutated_and_mode_has_one_system_prompt(self):
        messages = [{'role': 'user', 'content': 'hello'}]
        original = copy.deepcopy(messages)
        with patch('ai.ollama.Client') as client:
            client.return_value.chat.return_value = {'message': {'content': 'reply'}}
            ask_ai(messages, 'assistant')
            ask_ai(messages, 'coder')
            sent = client.return_value.chat.call_args.kwargs
            self.assertFalse(sent['stream'])
            self.assertEqual(len([m for m in sent['messages'] if m['role']=='system']), 1)
            self.assertIn('programming mentor', sent['messages'][0]['content'])
        self.assertEqual(messages, original)

    def test_ollama_errors_are_actionable(self):
        for error, status in [(ConnectionError('offline'), 503),
                              (ollama.ResponseError('missing', 404), 503),
                              (httpx.ReadTimeout('slow'), 504)]:
            with patch('ai.ollama.Client') as client:
                client.return_value.chat.side_effect = error
                with self.assertRaises(AIError) as caught:
                    ask_ai([{'role': 'user', 'content': 'hello'}])
                self.assertEqual(caught.exception.status, status)

    def test_home_and_assets(self):
        for url in ['/', '/static/script.js', '/static/vendor/marked.min.js', '/static/vendor/purify.min.js']:
            with self.client.get(url) as response:
                self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
