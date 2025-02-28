#!/usr/bin/python
# -*- coding: utf-8 -*-

import ast
import json
import responses
import unittest
from unittest.mock import *

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes


import plugins.modules.clusters as clusters

API_VERSION = "v2"
API_URL = f"https://api.openshift.com/api/assisted-install/{API_VERSION}"

TEST_JSON = {"test": ["test1", "test2"]}


def set_module_args(args):
    """prepare arguments so that they will be picked up during module creation"""
    args = json.dumps({"ANSIBLE_MODULE_ARGS": args})
    basic._ANSIBLE_ARGS = to_bytes(args)


class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json and caught by the test case"""

    pass


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the test case"""

    pass


def exit_json(*args, **kwargs):
    """function to patch over exit_json; package return data into an exception"""
    if "changed" not in kwargs:
        kwargs["changed"] = False
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):
    """function to patch over fail_json; package return data into an exception"""
    kwargs["failed"] = True
    raise AnsibleFailJson(kwargs)


def get_bin_path(self, arg, required=False):
    """Mock AnsibleModule.get_bin_path"""
    if arg.endswith("clusters"):
        return "/usr/bin/clusters"
    else:
        if required:
            fail_json(msg="%r not found !" % arg)


class TestClusters(unittest.TestCase):

    def setUp(self):
        self.mock_module_helper = patch.multiple(
            basic.AnsibleModule,
            exit_json=exit_json,
            fail_json=fail_json,
            get_bin_path=get_bin_path,
        )
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

    def test_module_fail_when_required_args_missing(self):
        with self.assertRaises(AnsibleFailJson):
            set_module_args({})
            clusters.main()

    @responses.activate
    def test_clusters_list(self):
        print("test_clusters_list:\n(http_code)")
        parameterized_list = [200, 404]
        for http_code in parameterized_list:
            print(http_code)
            responses.get(
                f"{API_URL}/clusters",
                json=TEST_JSON,
                status=http_code,
            )

            set_module_args({"with_hosts": True})

            if http_code == 200:
                with self.assertRaises(AnsibleExitJson) as result:
                    clusters.main()

                self.assertFalse(
                    result.exception.args[0]["changed"]
                )  # ensure result is changed
                self.assertEqual(
                    ast.literal_eval(str(result.exception))["clusters"], TEST_JSON
                )

            else:
                with self.assertRaises(AnsibleFailJson) as result:
                    clusters.main()

                self.assertTrue(
                    result.exception.args[0]["changed"]
                )  # ensure result is changed
                self.assertEqual(
                    ast.literal_eval(str(result.exception))["msg"],
                    "Error listing clusters",
                )

    @responses.activate
    def test_clusters_register(self):
        print("test_clusters_register:\n(http_code, correct_args)")
        # NOTE: The order of parameterization here seems to matter (for some reason
        # that is a mystery to me). In the current order it works as intended, but if
        # you set correct_args to False before the (404, True) tuple it causes an
        # incorrect response from the module. Literally no idea why this is happening
        # and haven't been able to track down a cause.
        parameterized_list = [(200, True), (404, True), (200, False), (404, False)]
        for http_code, correct_args in parameterized_list:
            print(http_code, " ", correct_args)
            responses.post(
                f"{API_URL}/clusters",
                json=TEST_JSON,
                status=http_code,
            )

            if correct_args:
                set_module_args(
                    {
                        "state": "present",
                        "name": "testcluster",
                        "openshift_version": "4.16",
                    }
                )
            elif not correct_args:
                set_module_args(
                    {
                        "state": "present",
                    }
                )

            if not correct_args:
                with self.assertRaises(AnsibleFailJson) as result:
                    clusters.main()

                self.assertEqual(
                    ast.literal_eval(str(result.exception))["msg"],
                    "state is present but all of the following are missing: name, openshift_version",
                )

            elif http_code == 200 and correct_args:
                with self.assertRaises(AnsibleExitJson) as result:
                    clusters.main()

                self.assertFalse(
                    result.exception.args[0]["changed"]
                )  # ensure result is changed
                self.assertEqual(
                    ast.literal_eval(str(result.exception))["clusters"], TEST_JSON
                )

            elif http_code == 404 and correct_args:
                with self.assertRaises(AnsibleFailJson) as result:
                    clusters.main()

                self.assertTrue(
                    result.exception.args[0]["changed"]
                )  # ensure result is changed
                self.assertEqual(
                    ast.literal_eval(str(result.exception))["msg"],
                    "Error registering cluster",
                )

    @responses.activate
    def test_clusters_delete(self):
        print("test_clusters_delete:\n(http_code, correct_args)")
        # NOTE: See note above in test_clusters_register
        parameterized_list = [(204, True), (404, True), (204, False), (404, False)]
        cluster_id = "test"
        for http_code, correct_args in parameterized_list:
            print(http_code, " ", correct_args)
            responses.delete(
                f"{API_URL}/clusters/{cluster_id}",
                json=TEST_JSON,
                status=http_code,
            )

            if correct_args:
                set_module_args({"state": "absent", "cluster_id": cluster_id})
            else:
                set_module_args({"state": "absent"})

            if not correct_args:
                with self.assertRaises(AnsibleFailJson) as result:
                    clusters.main()

                self.assertEqual(
                    ast.literal_eval(str(result.exception))["msg"],
                    "state is absent but all of the following are missing: cluster_id",
                )

            elif http_code == 204:
                with self.assertRaises(AnsibleExitJson) as result:
                    clusters.main()

                self.assertTrue(
                    result.exception.args[0]["changed"]
                )  # ensure result is changed
                self.assertEqual(
                    ast.literal_eval(str(result.exception))["clusters"], []
                )

            elif http_code == 404:
                with self.assertRaises(AnsibleFailJson) as result:
                    clusters.main()

                self.assertEqual(
                    ast.literal_eval(str(result.exception))["msg"],
                    f"Error deleting cluster_id: {cluster_id}",
                )
