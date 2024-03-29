#!/user/bin/env python3
"""Module for testing the console"""
import unittest
from unittest.mock import patch
from io import StringIO
from console import HBNBCommand
from models import storage
from models.engine.file_storage import FileStorage
import re
import os


class Helpers(unittest.TestCase):
    """Class to keep helper functions together"""
    models = "BaseModel User City Place Amenity Review State".split(" ")

    @classmethod
    def setUpClass(cls):
        """This runs once before any of the tests"""
        try:
            os.rename("file.json", "tmp.json")
        except IOError:
            pass
        FileStorage._FileStorage__objects = {}

    @classmethod
    def tearDownClass(cls):
        """This runs once after all of the tests are done"""
        try:
            os.unlink("file.json")
        except IOError:
            pass
        try:
            os.rename("tmp.json", "file.json")
        except IOError:
            pass

    def t_cmd_assert_false(self, cmd: str) -> str:
        """Run cmd and perform assert false on the output, return output
        Used to test if running a command is successful
        """
        with patch("sys.stdout", new=StringIO()) as f:
            self.assertFalse(HBNBCommand().onecmd(cmd))
            output = f.getvalue().strip()
        return output

    def t_cmd_assert_true(self, cmd: str) -> str:
        """Run cmd and perform assert true on the output, return output"""
        with patch("sys.stdout", new=StringIO()) as f:
            self.assertTrue(HBNBCommand().onecmd(cmd))
            output = f.getvalue().strip()
        return output

    def t_fetch_model(self, model):
        """Fetches all the available instances of model"""
        objs = storage.all()
        if model:  # fetch only required
            return [str(v) for k, v in objs.items() if model in k]
        return [str(v) for v in objs.values()]  # Fetch all

    def t_truncate_store(self):
        """Remove the store file for recreation"""
        reg = r"\[(\w+)] \(([\w-]+)\)"
        with patch("sys.stdout", new=StringIO()) as f:
            HBNBCommand().onecmd(f"all")
            matches = re.findall(reg, f.getvalue().strip())
            for model, uuid in matches:
                HBNBCommand().onecmd("destroy {} {}".format(model, uuid))
        FileStorage._FileStorage__objects = {}  # take care of the memory store

    def t_cmd_output_test(self, cmd: str, expected: str):
        """Test running a command and checking output against expected"""
        with patch("sys.stdout", new=StringIO()) as f:
            HBNBCommand().onecmd(cmd)
            output = f.getvalue().strip()
        self.assertIn(expected, output)

    def t_cmd_assert_equal(self, cmd: str, expected: str) -> str:
        """Run cmd and perform assert equal on the output, return output"""
        with patch("sys.stdout", new=StringIO()) as f:
            HBNBCommand().onecmd(cmd)
            output = f.getvalue().strip()
            self.assertEqual(output, expected)
        return output

    def t_cmd_output(self, cmd: str) -> str:
        """Runs a command and returns its output"""
        with patch("sys.stdout", new=StringIO()) as f:
            HBNBCommand().onecmd(cmd)
            output = f.getvalue().strip()
        return output

    def t_create_all_models(self):
        """Tests that showing all models is successful
        Returns the uuids of showed models for manipulation
        The uuids must be in the order of class attribute models"""
        # Create these models and test that creating is succeessful
        models = self.models
        return [self.t_cmd_assert_false(f"create {mdl}") for mdl in models]

    def t_test_uuids_present(self, uuids: str):
        """Test that all the uuids are present in the store
        The uuids must be in the order of the class attribute models"""
        for model, uuid in zip(self.models, uuids):
            self.t_cmd_assert_false(f"show {model} {uuid}")

    def t_test_uuids_absent(self, uuids: str):
        """Test that all the uuids are absent in the store
        The uuids must be in the order of the class attribute models"""
        for model, uuid in zip(self.models, uuids):
            expected = "** no instance found **"
            self.t_cmd_output_test(f"show {model} {uuid}", expected)

    def t_show_all_models(self, uuids: list) -> str:
        """Tests that showing all models is successful
        Returns a single combined output strings for testing
        The uuids must be in the order of class attribute models"""
        # Show these models and test that showing is succeessful
        outputs = [
            self.t_cmd_output(f"show {model} {uuid}")
            for model, uuid in zip(self.models, uuids)]
        return "".join(outputs)

    def t_destroy_all_models(self, uuids: list):
        """Tests that destroying all models is successful
        Returns the uuids of destroyed models for testing
        The returned uuids must be in the order of class attribute models"""
        # Destroy these models and test that destroying is succeessful
        for model, uuid in zip(self.models, uuids):
            self.t_cmd_assert_false(f"destroy {model} {uuid}")
        return uuids

    def t_create_model(self, modelname: str):
        """Creates a model and returns the UUID for testing"""
        with patch("sys.stdout", new=StringIO()) as f:
            HBNBCommand().onecmd(f"create {modelname}")
        return f.getvalue().strip()

    def t_destroy_model(self, name_id: str):
        """Destroys a model and returns the output for testing"""
        with patch("sys.stdout", new=StringIO()) as f:
            HBNBCommand().onecmd(f"destroy {name_id}")

        return f.getvalue().strip()

    def t_test_output_in_outputs(self, outputs: list, big_output: str):
        """Test if each of unit ouputs if found in a single larger one"""
        for output in outputs:
            self.assertIn(output, big_output)


class TestHBNBCommand(Helpers):
    """The HBNHCommand tests class"""

    def test_empty_line(self):
        output = self.t_cmd_assert_false("")
        self.assertEqual(output, "")

    def test_prompt_string(self):
        """Test if the prompt string is in order"""
        self.assertEqual("(hbnb) ", HBNBCommand.prompt)

    def test_quit(self):
        """Test the quit command"""
        self.t_cmd_assert_true("quit")

    def test_EOF(self):
        """Test the EOF command"""
        self.t_cmd_assert_true("EOF")

    def test_cls(self):
        """Test the cls command"""
        self.t_cmd_assert_false("cls")
        uuid = self.t_create_model("User")
        output = self.t_cmd_output("all")
        self.assertTrue(output)  # True means the string is not empty
        output = self.t_cmd_assert_false("cls")
        self.assertFalse(output)  # The string is empty
        self.t_destroy_model(f"User {uuid}")  # Destroy the User

    def test_help(self):
        """Test the help"""
        txt = "Documented commands (type help <topic>):\n"
        txt += "========================================\n"
        self.t_cmd_output_test("help", txt)  # uses self.assertIn
        self.t_cmd_output_test("?", txt)  # uses self.assertIn
        self.t_cmd_assert_false("help all")
        self.t_cmd_assert_false("help EOF")
        self.t_cmd_assert_false("help count")
        self.t_cmd_assert_false("help create")
        self.t_cmd_assert_false("help destroy")
        self.t_cmd_assert_false("help help")
        self.t_cmd_assert_false("help quit")
        self.t_cmd_assert_false("help show")
        self.t_cmd_assert_false("help update")

    def test_update_command(self):
        """Tests update command"""
        self.t_cmd_output_test("update", "* class name missing **")
        self.t_cmd_output_test("update xyz", "** class doesn't exist **")
        self.t_cmd_output_test("update User", "** instance id missing **")
        self.t_cmd_output_test("update User d6c62c", "** no instance found **")

        # Create these models and test that creating is succeessful
        uuids = self.t_create_all_models()
        m0, u0 = self.models[0], uuids[0]
        self.t_cmd_output_test(f"update {m0} {u0}", "attribute name missing")
        self.t_cmd_output_test(f"update {m0} {u0} name", "value missing")
        # Test that each object can be retrieved
        outputs = self.t_show_all_models(uuids)
        # Test against the sort of the output of the all command
        self.t_test_output_in_outputs(uuids, outputs)

        # TEST FOR DIFFERENT WAYS OF USING THE UPDATE COMMAND

        # comamnd type: update User name "michael"
        expected = """'email': 'abc@gmail'"""  # Update the nomal way
        for model, id_ in zip(self.models, uuids):
            self.t_cmd_assert_false(f'update {model} {id_} email "abc@gmail"')
            # Did it work?
            self.t_cmd_output_test(f"show {model} {id_}", expected)

        # comamnd type: User.update("uuid", "name", "michael")
        for model, id_ in zip(self.models, uuids):
            expected = """'age': 36"""
            self.t_cmd_assert_false(f'{model}.update("{id_}", "age", 36)')
            # Did it work?
            self.t_cmd_output_test(f"show {model} {id_}", expected)

        # command type: User.update("uuid", {"name": "Michael"})
        for model, id_ in zip(self.models, uuids):
            expected = """'name': 'Michael'"""
            command = f'{model}.update("{id_}", {{"name": "Michael"}})'
            self.t_cmd_assert_false(command)
            # Did it work?
            self.t_cmd_output_test(f"show {model} {id_}", expected)

        # Test deleting all
        self.t_destroy_all_models(uuids)
        # Test that deletion succeeded
        self.t_test_uuids_absent(uuids)

    def test_create_command(self):
        """Tests for the create command"""
        self.t_cmd_output_test("create", "** class name missing **")
        self.t_cmd_output_test("create xyz", "** class doesn't exist **")

        # Create these models and test that creating is succeessful
        uuids = self.t_create_all_models()
        # Test that each object can be retrieved
        outputs = self.t_show_all_models(uuids)
        # Test against the sort of the output of the all command
        self.t_test_output_in_outputs(uuids, outputs)
        # Test deleting all
        self.t_destroy_all_models(uuids)
        # Test that deletion succeeded
        self.t_test_uuids_absent(uuids)

    def test_show_command(self):
        """Tests for the show command"""
        self.t_cmd_output_test("show", "* class name missing **")
        self.t_cmd_output_test("show User", "** instance id missing **")
        self.t_cmd_output_test("show xyz", "** class doesn't exist **")

        # Create these models and test that creating is succeessful
        uuids = self.t_create_all_models()

        # Testing of outputs
        # SHOW User uuid
        outputs = self.t_show_all_models(uuids)
        # User.show("uuid")
        for model, uuid in zip(self.models, uuids):
            self.t_cmd_output_test(f'{model}.show("{uuid}")', uuid)

        # Testing that all are present
        self.t_test_output_in_outputs(uuids, outputs)
        # Test deleting all
        self.t_destroy_all_models(uuids)
        # Test that deletion succeeded
        self.t_test_uuids_absent(uuids)

    def test_destroy_command(self):
        """Tests for the destroy command"""
        self.t_cmd_output_test("destroy", "** class name missing **")
        self.t_cmd_output_test("destroy User", "** instance id missing **")
        self.t_cmd_output_test("destroy xyz", "** class doesn't exist **")

        # Create these models and test that creating is succeessful
        uuids = self.t_create_all_models()
        outputs = self.t_show_all_models(uuids)  # like the all command
        # Test that the uuids are present
        self.t_test_output_in_outputs(uuids, outputs)  # Test deleting all
        self.t_destroy_all_models(uuids)  # Test that deletion succeeded
        self.t_test_uuids_absent(uuids)

        # create again
        uuids = self.t_create_all_models()
        # User.destroy("uuid")
        for model, uuid in zip(self.models, uuids):
            self.t_cmd_assert_false(f'{model}.destroy("{uuid}")')
        self.t_test_uuids_absent(uuids)  # test that destroy succeeded

    def test_all_command(self):
        """Tests for the all command"""
        self.t_cmd_output_test("all xyz", "** class doesn't exist **")
        self.t_cmd_output_test("User.all", "*** Unknown syntax:")
        self.t_cmd_output_test("User.all(aca9)", "class doesn't exist")
        self.t_cmd_output_test('User.all("aca9")', "class doesn't exist")

        # Test that all returns a string bounded by a '[' and a ']'
        self.assertRegex(self.t_cmd_output("all"), r"(^\[.*]$)")
        uuids = self.t_create_all_models()  # create all model forms
        outputs = self.t_show_all_models(uuids)  # like the all command
        self.t_test_output_in_outputs(uuids, outputs)  # uuids are present

        # command type: User.all()
        for model, uuid in zip(self.models, uuids):
            self.t_cmd_output_test(f'{model}.all()', uuid)
        # command type: all User
        for model, uuid in zip(self.models, uuids):
            self.t_cmd_output_test(f'all {model}', uuid)

    def test_count_command(self):
        """Tests for the count command"""

        # Truncate the store to start on a clean slate
        self.t_truncate_store()

        self.t_cmd_output_test("count", "* class name missing **")
        self.t_cmd_output_test("count xyz", "** class doesn't exist **")
        self.t_cmd_output_test("User.count", "*** Unknown syntax:")
        self.t_cmd_output_test("User.count(aca9)", "class doesn't exist")
        self.t_cmd_output_test('User.count("aca9")', "class doesn't exist")

        uuids = self.t_create_all_models()  # create all model forms
        outputs = self.t_show_all_models(uuids)  # like the all command
        self.t_test_output_in_outputs(uuids, outputs)  # uuids are present

        # command type: User.all()
        for model in self.models:
            self.t_cmd_output_test(f'{model}.count()', "1")
        # command type: all User
        for model in self.models:
            self.t_cmd_output_test(f'count {model}', "1")

        self.t_truncate_store()

        # command type: User.all()
        for model in self.models:
            self.t_cmd_output_test(f'{model}.count()', "0")
        # command type: all User
        for model in self.models:
            self.t_cmd_output_test(f'count {model}', "0")


if __name__ == "__main__":
    unittest.main()
