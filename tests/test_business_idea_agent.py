import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add the parent directory to sys.path to allow importing business_idea_agent
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Conditional import for business_idea_agent to handle if it's run directly or via test runner
try:
    from business_idea_agent import check_name_availability, run_business_idea_pipeline, generate_idea, validate_idea, define_business_elements
except ImportError:
    # This is primarily for linters / IDEs; the sys.path modification should handle actual runtime.
    print("Error: Could not import from business_idea_agent. Ensure it's in the parent directory.")
    # Define dummy functions if import fails, so the rest of the test file can be parsed
    def check_name_availability(name): return {}
    def run_business_idea_pipeline(domain, key, retries): return {}
    def generate_idea(domain, key): return {}
    def validate_idea(name, desc, tag, key): return {}
    def define_business_elements(name, desc, key): return {}


class TestBusinessIdeaAgent(unittest.TestCase):

    def test_check_name_availability_sanitization(self):
        """Tests the name sanitization part of check_name_availability indirectly."""
        # This test is a bit indirect as sanitization is internal.
        # We mock whois to see what domain name it's called with.
        with patch('business_idea_agent.whois.whois') as mock_whois:
            mock_whois.side_effect = Exception("Mocked exception to stop further processing") # or return a mock response

            try:
                check_name_availability("My Awesome! Business??")
            except Exception:
                pass # Expected due to side_effect

            # Check if whois was called with the sanitized name
            # This assumes .com is appended by the function
            self.assertTrue(mock_whois.called)
            args, _ = mock_whois.call_args
            self.assertEqual(args[0], "myawesomebusiness.com")

        with patch('business_idea_agent.whois.whois') as mock_whois:
            mock_whois.side_effect = Exception("Mocked exception")
            try:
                check_name_availability("  leading and trailing spaces  ")
            except Exception:
                pass
            self.assertTrue(mock_whois.called)
            args, _ = mock_whois.call_args
            self.assertEqual(args[0], "leadingandtrailingspaces.com")

    def test_check_name_availability_empty_name(self):
        result = check_name_availability("  ") # Contains only spaces
        self.assertEqual(result.get("status"), "invalid_name")
        result_empty = check_name_availability("")
        self.assertEqual(result_empty.get("status"), "invalid_name")


    @patch('business_idea_agent.generate_idea')
    @patch('business_idea_agent.validate_idea')
    @patch('business_idea_agent.define_business_elements')
    @patch('business_idea_agent.check_name_availability')
    def test_run_business_idea_pipeline_structure(self, mock_check_name, mock_define_elements, mock_validate_idea, mock_generate_idea):
        """Tests the overall structure of the pipeline output with mocks."""

        # Configure mocks to return expected structures
        mock_generate_idea.return_value = {
            "businessName": "TestBiz",
            "businessDescription": "A test business.",
            "tagline": "Testing is fun!"
        }
        mock_check_name.return_value = {
            "domain_name": "testbiz.com",
            "status": "available",
            "details": "Mocked as available"
        }
        mock_validate_idea.return_value = {
            "validation_summary": "Looks good to mock!"
        }
        mock_define_elements.return_value = {
            "coreValueProposition": "Mock CVP",
            "primaryTargetAudience": "Mock Audience",
            "demographics": "Mock Demographics",
            "uniqueSellingPoints": ["Mock USP1"],
            "initialRevenueModel": "Mock Revenue"
        }

        # Call the pipeline
        result = run_business_idea_pipeline("test domain", "fake_api_key", max_name_checks=1)

        # Assert that the main keys are in the result
        self.assertIn("businessName", result)
        self.assertIn("BusinessDescription", result)
        self.assertIn("tagline", result)
        self.assertIn("coreValueProposition", result)
        self.assertIn("primaryTargetAudience", result)
        self.assertIn("demographics", result)
        self.assertIn("uniqueSellingPoints", result)
        self.assertIn("initialRevenueModel", result)
        self.assertIn("validationSummary", result)
        self.assertIn("nameAvailability", result)

        self.assertEqual(result["businessName"], "TestBiz")
        self.assertEqual(result["nameAvailability"]["status"], "available")

    @patch('business_idea_agent.openai.Completion.create')
    def test_generate_idea_api_error(self, mock_openai_create):
        """Test how generate_idea handles an OpenAI API error."""
        mock_openai_create.side_effect = Exception("OpenAI API is down")

        result = generate_idea("test domain", "fake_api_key")

        self.assertEqual(result["businessName"], "Error generating name")
        self.assertEqual(result["businessDescription"], "Error generating description")
        self.assertEqual(result["tagline"], "Error generating tagline")
        # Check that logging.error was called (requires business_idea_agent to use logging)
        # This part is harder to test without more setup or if logging isn't easily mockable from here.

if __name__ == '__main__':
    unittest.main()
