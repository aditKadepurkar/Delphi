"""
This file contains the unit tests for the create_function tool in the default tools file.
"""
import sys
import unittest
from unittest.mock import patch, MagicMock
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from default_tools import create_function 
from GPT_function_calling import OpenAI

class TestCreateFunction(unittest.TestCase):
    @patch('GPT_function_calling.OpenAI')
    def test_create_file_success(self, MockOpenAI):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = """def helloWorld():
        return "Hello, World!"
        """
        MockOpenAI.return_value.chat.completions.create.return_value = mock_response
        ret = create_function('add', 'takes two integers and returns their sum')
        exec(ret, globals())
        # self.assertIsNotNone(add)  
        self.assertEqual(add(2, 3), 5)
if __name__ == '__main__':
    unittest.main()
