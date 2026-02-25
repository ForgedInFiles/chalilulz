"""
test_schema — Tool schema generation and structure
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chalilulz import mk_schema, TOOLS, SCHEMA, OPT, OPT_PARAMS


class TestSchemaGeneration(unittest.TestCase):
    def test_schema_is_list(self):
        self.assertIsInstance(SCHEMA, list)

    def test_schema_contains_tools(self):
        self.assertEqual(len(SCHEMA), len(TOOLS))

    def test_each_tool_has_required_fields(self):
        for tool in SCHEMA:
            self.assertIn("type", tool)
            self.assertEqual(tool["type"], "function")
            self.assertIn("function", tool)
            func = tool["function"]
            self.assertIn("name", func)
            self.assertIn("description", func)
            self.assertIn("parameters", func)

    def test_parameters_structure(self):
        for tool in SCHEMA:
            params = tool["function"]["parameters"]
            self.assertIn("type", params)
            self.assertEqual(params["type"], "object")
            self.assertIn("properties", params)
            self.assertIn("required", params)

    def test_optional_params(self):
        # Check that optional params are not in required list
        for tool in SCHEMA:
            name = tool["function"]["name"]
            tool_opt = OPT | OPT_PARAMS.get(name, set())
            required = tool["function"]["parameters"]["required"]
            for param in required:
                self.assertNotIn(
                    param, tool_opt, f"Optional param {param} incorrectly marked required"
                )

    def test_read_tool_schema(self):
        read_tool = next(t for t in SCHEMA if t["function"]["name"] == "read")
        desc = read_tool["function"]["description"]
        self.assertIn("Read file", desc)
        props = read_tool["function"]["parameters"]["properties"]
        self.assertIn("path", props)
        self.assertIn("offset", props)
        self.assertIn("limit", props)
        # offset and limit should be optional
        self.assertNotIn("offset", read_tool["function"]["parameters"]["required"])
        self.assertNotIn("limit", read_tool["function"]["parameters"]["required"])

    def test_write_tool_schema(self):
        write_tool = next(t for t in SCHEMA if t["function"]["name"] == "write")
        props = write_tool["function"]["parameters"]["properties"]
        self.assertIn("path", props)
        self.assertIn("content", props)
        # content and path required
        required = write_tool["function"]["parameters"]["required"]
        self.assertIn("content", required)
        self.assertIn("path", required)

    def test_edit_tool_schema(self):
        edit_tool = next(t for t in SCHEMA if t["function"]["name"] == "edit")
        props = edit_tool["function"]["parameters"]["properties"]
        self.assertIn("path", props)
        self.assertIn("old", props)
        self.assertIn("new", props)
        self.assertIn("all", props)
        # old, new, and path required; all optional
        required = edit_tool["function"]["parameters"]["required"]
        self.assertIn("old", required)
        self.assertIn("new", required)
        self.assertIn("path", required)
        self.assertNotIn("all", required)

    def test_bash_tool_schema(self):
        bash_tool = next(t for t in SCHEMA if t["function"]["name"] == "bash")
        props = bash_tool["function"]["parameters"]["properties"]
        self.assertIn("cmd", props)
        self.assertIn("cwd", props)
        required = bash_tool["function"]["parameters"]["required"]
        self.assertIn("cmd", required)
        self.assertNotIn("cwd", required)  # optional


class TestToolFunctions(unittest.TestCase):
    def test_mk_schema_consistency(self):
        # All tools in TOOLS should be in SCHEMA
        tool_names = set(TOOLS.keys())
        schema_names = set(t["function"]["name"] for t in SCHEMA)
        self.assertEqual(tool_names, schema_names)


if __name__ == "__main__":
    unittest.main()
