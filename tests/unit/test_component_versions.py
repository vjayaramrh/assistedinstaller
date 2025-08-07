#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# assisted-by: Claude 3.5 Sonnet (Cursor)

"""
Unit tests for component_versions module
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the plugins directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'plugins', 'modules'))

try:
    import component_versions
except ImportError:
    # Handle case where module dependencies aren't available
    component_versions = None


class TestComponentVersions(unittest.TestCase):
    """Test cases for component_versions module"""

    def setUp(self):
        """Set up test fixtures"""
        if component_versions is None:
            self.skipTest("component_versions module not available")
        
        self.mock_module_args = {
            'openshift_version': None,
            'cpu_architecture': None,
        }

    @patch('component_versions.apitoken.GetToken')
    @patch('component_versions.apiurl.GetURL')
    @patch('component_versions.requests.get')
    @patch('component_versions.AnsibleModule')
    def test_run_module_success(self, mock_ansible_module, mock_requests_get, mock_get_url, mock_get_token):
        """Test successful API call"""
        # Mock the token and URL
        mock_get_token.return_value = "fake-token"
        mock_get_url.return_value = "https://api.openshift.com/api/assisted-install/v2/component-versions"
        
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "4.18.1": {
                "components": {
                    "cluster-version-operator": "4.18.1",
                    "machine-config-operator": "4.18.1"
                },
                "openshift_version": "4.18.1",
                "cpu_architecture": "x86_64"
            }
        }
        mock_requests_get.return_value = mock_response
        
        # Mock AnsibleModule
        mock_module_instance = MagicMock()
        mock_module_instance.params = self.mock_module_args
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        component_versions.run_module()
        
        # Verify API call was made with correct parameters
        mock_requests_get.assert_called_once()
        call_args = mock_requests_get.call_args
        self.assertIn('headers', call_args.kwargs)
        self.assertEqual(call_args.kwargs['headers']['Authorization'], 'Bearer fake-token')
        
        # Verify exit_json was called with success
        mock_module_instance.exit_json.assert_called_once()
        exit_args = mock_module_instance.exit_json.call_args[1]
        self.assertFalse(exit_args['changed'])
        self.assertIn('component_versions', exit_args)

    @patch('component_versions.apitoken.GetToken')
    @patch('component_versions.apiurl.GetURL')
    @patch('component_versions.requests.get')
    @patch('component_versions.AnsibleModule')
    def test_run_module_with_filters(self, mock_ansible_module, mock_requests_get, mock_get_url, mock_get_token):
        """Test API call with filters"""
        # Mock the token and URL
        mock_get_token.return_value = "fake-token"
        mock_get_url.return_value = "https://api.openshift.com/api/assisted-install/v2/component-versions"
        
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {}
        mock_requests_get.return_value = mock_response
        
        # Mock AnsibleModule with parameters
        mock_module_instance = MagicMock()
        mock_module_instance.params = {
            'openshift_version': '4.18',
            'cpu_architecture': 'x86_64',
        }
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        component_versions.run_module()
        
        # Verify API call was made with query parameters
        mock_requests_get.assert_called_once()
        call_args = mock_requests_get.call_args
        self.assertIn('params', call_args.kwargs)
        self.assertEqual(call_args.kwargs['params']['openshift_version'], '4.18')
        self.assertEqual(call_args.kwargs['params']['cpu_architecture'], 'x86_64')

    @patch('component_versions.apitoken.GetToken')
    @patch('component_versions.apiurl.GetURL')
    @patch('component_versions.requests.get')
    @patch('component_versions.AnsibleModule')
    def test_run_module_api_failure(self, mock_ansible_module, mock_requests_get, mock_get_url, mock_get_token):
        """Test API failure handling"""
        # Mock the token and URL
        mock_get_token.return_value = "fake-token"
        mock_get_url.return_value = "https://api.openshift.com/api/assisted-install/v2/component-versions"
        
        # Mock failed API response
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.json.return_value = {"error": "Not found"}
        mock_requests_get.return_value = mock_response
        
        # Mock AnsibleModule
        mock_module_instance = MagicMock()
        mock_module_instance.params = self.mock_module_args
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        component_versions.run_module()
        
        # Verify fail_json was called
        mock_module_instance.fail_json.assert_called_once()
        fail_args = mock_module_instance.fail_json.call_args[1]
        self.assertEqual(fail_args['msg'], "Error querying component versions")
        self.assertFalse(fail_args['changed'])
        self.assertEqual(fail_args['component_versions'], {})

    @patch('component_versions.HAS_REQUESTS', False)
    @patch('component_versions.AnsibleModule')
    def test_run_module_missing_requests(self, mock_ansible_module):
        """Test handling of missing requests library"""
        # Mock AnsibleModule
        mock_module_instance = MagicMock()
        mock_module_instance.params = self.mock_module_args
        mock_ansible_module.return_value = mock_module_instance
        
        # Run the module
        component_versions.run_module()
        
        # Verify fail_json was called due to missing requests
        mock_module_instance.fail_json.assert_called_once()
        fail_args = mock_module_instance.fail_json.call_args[1]
        self.assertIn("requests", fail_args['msg'])


if __name__ == '__main__':
    unittest.main()
