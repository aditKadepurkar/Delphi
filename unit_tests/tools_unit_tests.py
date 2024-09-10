"""
This file contains the unit tests for the tools functions in default_tools file except for create_function.
"""

import sys
import unittest
from unittest.mock import patch, MagicMock, mock_open
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from default_tools import * 
del globals()['create_function']
from database import Database

class TestCreateFile(unittest.TestCase):
    @patch('builtins.open', new_callable=mock_open)
    def test_create_file_success(self, mock_open):
        
        result = (create_file('test_file.txt', 'Hello, World!'))
        mock_open.assert_called()  
        mock_open().write.assert_called()  
        self.assertEqual(result, 'Success')
    
    @patch('builtins.open', side_effect=Exception("File creation failed"))
    def test_create_file_failure(self, mock_open):
        
        result = create_file('test_file.txt', 'Hello, World!')
        self.assertEqual(result, "Failed")

if __name__ == '__main__':
    unittest.main()