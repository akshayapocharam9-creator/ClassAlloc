import unittest
from unittest.mock import patch, MagicMock

# Import the UI to ensure no syntax/import errors
import ui.what_if as what_if
import app

class TestUIWhatIfIntegration(unittest.TestCase):
    def test_import_succeeds(self):
        self.assertTrue(hasattr(what_if, 'render_what_if_lab'))
        
    @patch('streamlit.session_state', {})
    @patch('streamlit.title')
    def test_render_aborts_if_no_baseline(self, mock_title):
        # Should gracefully abort if solver_result is missing
        what_if.render_what_if_lab()
        mock_title.assert_called_with("What-If Optimization Lab")
        
    def test_app_py_exposes_what_if_page(self):
        # We can physically inspect the app.py text to verify the routing exists
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('"What-If Optimization Lab"', content)
            self.assertIn('import ui.what_if', content)

if __name__ == '__main__':
    unittest.main()
