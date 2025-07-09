#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for infra_envs module
"""

import json
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add the module path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'plugins', 'modules'))

from infra_envs import (
    create_infra_env,
    list_infra_envs,
    get_infra_env,
    update_infra_env,
    delete_infra_env,
    prepare_infra_env_data,
    handle_error_response,
    run_module
)


class TestInfraEnvs:
    """Test class for infra_envs module"""

    def setup_method(self):
        """Setup test fixtures"""
        self.mock_module = Mock()
        self.mock_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer test-token"
        }
        self.sample_infra_env_data = {
            "id": "test-infra-env-id",
            "name": "test-infra-env",
            "cpu_architecture": "x86_64",
            "created_at": "2025-02-28T15:39:40.008442Z",
            "download_url": "https://api.openshift.com/api/assisted-images/test.iso",
            "openshift_version": "4.19",
            "proxy": {},
            "pull_secret_set": True,
            "type": "minimal-iso",
            "updated_at": "2025-02-28T15:39:40.035846Z"
        }

    @patch('infra_envs.requests.post')
    def test_create_infra_env_success(self, mock_post):
        """Test successful infra-env creation"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = self.sample_infra_env_data
        mock_post.return_value = mock_response
        
        self.mock_module.params = {
            "name": "test-infra-env",
            "pull_secret": "test-pull-secret",
            "openshift_version": "4.19",
            "cpu_architecture": "x86_64"
        }
        
        with patch('infra_envs.prepare_infra_env_data') as mock_prepare:
            mock_prepare.return_value = {"name": "test-infra-env", "pull_secret": "test-pull-secret"}
            
            result = create_infra_env(self.mock_module, self.mock_headers)
            
            assert result["changed"] is True
            assert result["infra_envs"] == self.sample_infra_env_data
            mock_post.assert_called_once()

    @patch('infra_envs.requests.post')
    def test_create_infra_env_failure(self, mock_post):
        """Test failed infra-env creation"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Bad request"}
        mock_post.return_value = mock_response
        
        self.mock_module.params = {
            "name": "test-infra-env",
            "pull_secret": "test-pull-secret"
        }
        
        with patch('infra_envs.prepare_infra_env_data') as mock_prepare:
            mock_prepare.return_value = {"name": "test-infra-env", "pull_secret": "test-pull-secret"}
            
            with patch('infra_envs.handle_error_response') as mock_handle_error:
                create_infra_env(self.mock_module, self.mock_headers)
                mock_handle_error.assert_called_once()

    @patch('infra_envs.requests.get')
    def test_list_infra_envs_success(self, mock_get):
        """Test successful infra-envs listing"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [self.sample_infra_env_data]
        mock_get.return_value = mock_response
        
        result = list_infra_envs(self.mock_module, self.mock_headers)
        
        assert result["changed"] is False
        assert result["infra_envs"] == [self.sample_infra_env_data]
        mock_get.assert_called_once()

    @patch('infra_envs.requests.get')
    def test_list_infra_envs_failure(self, mock_get):
        """Test failed infra-envs listing"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal server error"}
        mock_get.return_value = mock_response
        
        with patch('infra_envs.handle_error_response') as mock_handle_error:
            list_infra_envs(self.mock_module, self.mock_headers)
            mock_handle_error.assert_called_once()

    @patch('infra_envs.requests.get')
    def test_get_infra_env_success(self, mock_get):
        """Test successful infra-env retrieval"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_infra_env_data
        mock_get.return_value = mock_response
        
        result = get_infra_env(self.mock_module, self.mock_headers, "test-infra-env-id")
        
        assert result["changed"] is False
        assert result["infra_envs"] == self.sample_infra_env_data
        mock_get.assert_called_once()

    @patch('infra_envs.requests.get')
    def test_get_infra_env_not_found(self, mock_get):
        """Test infra-env not found"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        self.mock_module.fail_json = Mock()
        
        get_infra_env(self.mock_module, self.mock_headers, "non-existent-id")
        
        self.mock_module.fail_json.assert_called_once()

    @patch('infra_envs.requests.patch')
    def test_update_infra_env_success(self, mock_patch):
        """Test successful infra-env update"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_infra_env_data
        mock_patch.return_value = mock_response
        
        self.mock_module.params = {
            "ssh_authorized_key": "ssh-rsa test-key",
            "proxy": {"http_proxy": "http://proxy.example.com:8080"}
        }
        
        with patch('infra_envs.prepare_infra_env_data') as mock_prepare:
            mock_prepare.return_value = {"ssh_authorized_key": "ssh-rsa test-key"}
            
            result = update_infra_env(self.mock_module, self.mock_headers, "test-infra-env-id")
            
            assert result["changed"] is True
            assert result["infra_envs"] == self.sample_infra_env_data
            mock_patch.assert_called_once()

    @patch('infra_envs.requests.patch')
    def test_update_infra_env_not_found(self, mock_patch):
        """Test update infra-env not found"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_patch.return_value = mock_response
        
        self.mock_module.fail_json = Mock()
        
        with patch('infra_envs.prepare_infra_env_data') as mock_prepare:
            mock_prepare.return_value = {"ssh_authorized_key": "ssh-rsa test-key"}
            
            update_infra_env(self.mock_module, self.mock_headers, "non-existent-id")
            
            self.mock_module.fail_json.assert_called_once()

    @patch('infra_envs.requests.delete')
    def test_delete_infra_env_success(self, mock_delete):
        """Test successful infra-env deletion"""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response
        
        result = delete_infra_env(self.mock_module, self.mock_headers, "test-infra-env-id")
        
        assert result["changed"] is True
        assert result["infra_envs"] == []
        mock_delete.assert_called_once()

    @patch('infra_envs.requests.delete')
    def test_delete_infra_env_not_found(self, mock_delete):
        """Test delete infra-env not found"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_delete.return_value = mock_response
        
        self.mock_module.fail_json = Mock()
        
        delete_infra_env(self.mock_module, self.mock_headers, "non-existent-id")
        
        self.mock_module.fail_json.assert_called_once()

    def test_prepare_infra_env_data_create(self):
        """Test prepare_infra_env_data for creation"""
        self.mock_module.params = {
            "name": "test-infra-env",
            "pull_secret": "test-pull-secret",
            "openshift_version": "4.19",
            "cpu_architecture": "x86_64",
            "ssh_authorized_key": "ssh-rsa test-key",
            "proxy": {"http_proxy": "http://proxy.example.com:8080"},
            "static_network_config": [{"interface": "eth0", "ip": "192.168.1.100"}],
            "kernel_arguments": [{"operation": "append", "value": "console=ttyS0"}],
            "state": "present"
        }
        
        self.mock_module.params.get = Mock(side_effect=lambda x: self.mock_module.params.get(x))
        
        result = prepare_infra_env_data(self.mock_module, update=False)
        
        assert result["name"] == "test-infra-env"
        assert result["pull_secret"] == "test-pull-secret"
        assert result["openshift_version"] == "4.19"
        assert result["cpu_architecture"] == "x86_64"
        assert result["ssh_authorized_key"] == "ssh-rsa test-key"
        assert result["proxy"] == {"http_proxy": "http://proxy.example.com:8080"}

    def test_prepare_infra_env_data_update(self):
        """Test prepare_infra_env_data for update"""
        self.mock_module.params = {
            "name": "test-infra-env",  # Should be ignored for updates
            "pull_secret": "test-pull-secret",  # Should be ignored for updates
            "ssh_authorized_key": "ssh-rsa updated-key",
            "proxy": {"http_proxy": "http://newproxy.example.com:8080"},
            "state": "present"
        }
        
        self.mock_module.params.get = Mock(side_effect=lambda x: self.mock_module.params.get(x))
        
        result = prepare_infra_env_data(self.mock_module, update=True)
        
        assert "name" not in result  # Should not be included for updates
        assert "pull_secret" not in result  # Should not be included for updates
        assert result["ssh_authorized_key"] == "ssh-rsa updated-key"
        assert result["proxy"] == {"http_proxy": "http://newproxy.example.com:8080"}

    def test_handle_error_response_json(self):
        """Test handle_error_response with JSON response"""
        mock_response = Mock()
        mock_response.json.return_value = {"error": "Test error"}
        mock_response.status_code = 400
        
        self.mock_module.fail_json = Mock()
        
        handle_error_response(self.mock_module, mock_response, "Test error message")
        
        self.mock_module.fail_json.assert_called_once()
        call_args = self.mock_module.fail_json.call_args
        assert call_args[1]["msg"] == "Test error message"
        assert call_args[1]["status_code"] == 400
        assert call_args[1]["response"] == {"error": "Test error"}

    def test_handle_error_response_text(self):
        """Test handle_error_response with text response"""
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "Error response text"
        mock_response.status_code = 500
        
        self.mock_module.fail_json = Mock()
        
        handle_error_response(self.mock_module, mock_response, "Test error message")
        
        self.mock_module.fail_json.assert_called_once()
        call_args = self.mock_module.fail_json.call_args
        assert call_args[1]["msg"] == "Test error message"
        assert call_args[1]["status_code"] == 500
        assert call_args[1]["response"] == "Error response text"

    @patch('infra_envs.apitoken.GetToken')
    @patch('infra_envs.AnsibleModule')
    def test_run_module_create_operation(self, mock_ansible_module, mock_get_token):
        """Test run_module for create operation"""
        mock_get_token.return_value = "test-token"
        
        mock_module_instance = Mock()
        mock_module_instance.params = {
            "state": "present",
            "name": "test-infra-env",
            "pull_secret": "test-pull-secret",
            "infra_env_id": None
        }
        mock_module_instance.params.get = Mock(side_effect=lambda x: mock_module_instance.params.get(x))
        mock_ansible_module.return_value = mock_module_instance
        
        with patch('infra_envs.create_infra_env') as mock_create:
            mock_create.return_value = {"changed": True, "infra_envs": self.sample_infra_env_data}
            
            run_module()
            
            mock_create.assert_called_once()
            mock_module_instance.exit_json.assert_called_once()

    @patch('infra_envs.apitoken.GetToken')
    @patch('infra_envs.AnsibleModule')
    def test_run_module_list_operation(self, mock_ansible_module, mock_get_token):
        """Test run_module for list operation"""
        mock_get_token.return_value = "test-token"
        
        mock_module_instance = Mock()
        mock_module_instance.params = {
            "state": None,
            "infra_env_id": None
        }
        mock_module_instance.params.get = Mock(side_effect=lambda x: mock_module_instance.params.get(x))
        mock_ansible_module.return_value = mock_module_instance
        
        with patch('infra_envs.list_infra_envs') as mock_list:
            mock_list.return_value = {"changed": False, "infra_envs": [self.sample_infra_env_data]}
            
            run_module()
            
            mock_list.assert_called_once()
            mock_module_instance.exit_json.assert_called_once()

    @patch('infra_envs.apitoken.GetToken')
    @patch('infra_envs.AnsibleModule')
    def test_run_module_get_operation(self, mock_ansible_module, mock_get_token):
        """Test run_module for get operation"""
        mock_get_token.return_value = "test-token"
        
        mock_module_instance = Mock()
        mock_module_instance.params = {
            "state": None,
            "infra_env_id": "test-infra-env-id"
        }
        mock_module_instance.params.get = Mock(side_effect=lambda x: mock_module_instance.params.get(x))
        mock_ansible_module.return_value = mock_module_instance
        
        with patch('infra_envs.get_infra_env') as mock_get:
            mock_get.return_value = {"changed": False, "infra_envs": self.sample_infra_env_data}
            
            run_module()
            
            mock_get.assert_called_once()
            mock_module_instance.exit_json.assert_called_once()

    @patch('infra_envs.apitoken.GetToken')
    @patch('infra_envs.AnsibleModule')
    def test_run_module_update_operation(self, mock_ansible_module, mock_get_token):
        """Test run_module for update operation"""
        mock_get_token.return_value = "test-token"
        
        mock_module_instance = Mock()
        mock_module_instance.params = {
            "state": "present",
            "infra_env_id": "test-infra-env-id"
        }
        mock_module_instance.params.get = Mock(side_effect=lambda x: mock_module_instance.params.get(x))
        mock_ansible_module.return_value = mock_module_instance
        
        with patch('infra_envs.update_infra_env') as mock_update:
            mock_update.return_value = {"changed": True, "infra_envs": self.sample_infra_env_data}
            
            run_module()
            
            mock_update.assert_called_once()
            mock_module_instance.exit_json.assert_called_once()

    @patch('infra_envs.apitoken.GetToken')
    @patch('infra_envs.AnsibleModule')
    def test_run_module_delete_operation(self, mock_ansible_module, mock_get_token):
        """Test run_module for delete operation"""
        mock_get_token.return_value = "test-token"
        
        mock_module_instance = Mock()
        mock_module_instance.params = {
            "state": "absent",
            "infra_env_id": "test-infra-env-id"
        }
        mock_module_instance.params.get = Mock(side_effect=lambda x: mock_module_instance.params.get(x))
        mock_ansible_module.return_value = mock_module_instance
        
        with patch('infra_envs.delete_infra_env') as mock_delete:
            mock_delete.return_value = {"changed": True, "infra_envs": []}
            
            run_module()
            
            mock_delete.assert_called_once()
            mock_module_instance.exit_json.assert_called_once()

    @patch('infra_envs.apitoken.GetToken')
    @patch('infra_envs.AnsibleModule')
    def test_run_module_no_token(self, mock_ansible_module, mock_get_token):
        """Test run_module when no token is available"""
        mock_get_token.return_value = None
        
        mock_module_instance = Mock()
        mock_ansible_module.return_value = mock_module_instance
        
        run_module()
        
        mock_module_instance.fail_json.assert_called_once()
        call_args = mock_module_instance.fail_json.call_args
        assert "API token is required" in call_args[1]["msg"]

    @patch('infra_envs.apitoken.GetToken')
    @patch('infra_envs.AnsibleModule')
    def test_run_module_exception_handling(self, mock_ansible_module, mock_get_token):
        """Test run_module exception handling"""
        mock_get_token.return_value = "test-token"
        
        mock_module_instance = Mock()
        mock_module_instance.params = {
            "state": "present",
            "infra_env_id": None
        }
        mock_module_instance.params.get = Mock(side_effect=lambda x: mock_module_instance.params.get(x))
        mock_ansible_module.return_value = mock_module_instance
        
        with patch('infra_envs.create_infra_env') as mock_create:
            mock_create.side_effect = Exception("Test exception")
            
            run_module()
            
            mock_module_instance.fail_json.assert_called_once()
            call_args = mock_module_instance.fail_json.call_args
            assert "Unexpected error" in call_args[1]["msg"]


if __name__ == '__main__':
    pytest.main([__file__]) 