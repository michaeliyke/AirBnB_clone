#!/user/bin/env python3
"""Module for testing the console"""
import unittest
from unittest.mock import patch
from io import StringIO
from console import HBNBCommand
from models import storage
import re


class Helpers(unittest.TestCase):
    """Class to keep helper functions together"""

    def setUp(self):
        """For each test: startup settings happen here"""
        # self.hbnb = HBNBCommand()
        # self.stdout_ = StringIO()
        # self.t_trucate_store()  # Truncate file.json
        pass

    def tearDown(self):
        """For each test: final cleanups happen here"""
        # self.stdout_.close()
        pass

    def clear_stdout(self):
        """Clears the stdout buffer - Use is discouraged"""
        self.stdout_.truncate(0)
        self.stdout_.seek(0)

    def t_fetch_model(self, model):
        """Fetches all the available instances of model"""
        objs = storage.all()
        return [str(v) for k, v in objs.items() if model in k]

    def t_trucate_store(self):
        """Truncates the store file if called. Use is discouraged"""
        reg = r"\[(\w+)] \(([\w-]+)\)"
        with patch("sys.stdout", new=StringIO()) as f:
            HBNBCommand().onecmd(f"all")
            matches = re.findall(reg, f.getvalue().strip())
            for model, uuid in matches:
                HBNBCommand().onecmd("destroy {} {}".format(model, uuid))

    def t_create_model(self, modelname: str):
        """Creates a model and returns the UUID for testing"""
        with patch("sys.stdout", new=StringIO()) as f:
            HBNBCommand().onecmd(f"create {modelname}")
            output = f.getvalue().strip()
        return output

    def t_destroy_model(self, name_id: str):
        """Destroys a model and returns the output for testing"""
        with patch("sys.stdout", new=StringIO()) as f:
            HBNBCommand().onecmd(f"destroy {name_id}")
            output = f.getvalue().strip()

        return output

    def t_cmd_output_test(self, cmd: str, expected: str):
        """Test running a command and checking output against expected"""
        with patch("sys.stdout", new=StringIO()) as f:
            HBNBCommand().onecmd(cmd)
        self.assertIn(expected, f.getvalue().strip())

    def t_cmd_output(self, cmd: str) -> str:
        """Runs a command and returns its output"""
        with patch("sys.stdout", new=StringIO()) as f:
            HBNBCommand().onecmd(cmd)
            ouput = f.getvalue().strip()
        return ouput


class TestHBNBCommand(Helpers):
    """The HBNHCommand tests class"""

    def test_show_command(self):
        """Tests for the show command"""
        self.t_cmd_output_test("show", "* class name missing **")
        self.t_cmd_output_test("show User", "** instance id missing **")
        self.t_cmd_output_test("show xyz", "** class doesn't exist **")

        uuid = self.t_create_model("User")
        self.t_cmd_output_test(f"show User {uuid}", uuid)
        self.t_cmd_output_test(f'User.show("{uuid}")', uuid)
        self.t_destroy_model(f"User {uuid}")

    def test_create_command(self):
        """Tests for the create command"""
        self.t_cmd_output_test("create", "** class name missing **")
        self.t_cmd_output_test("create xyz", "** class doesn't exist **")

        uuid = self.t_create_model("City")  # creating known model
        self.t_cmd_output_test(f"show City {uuid}", uuid)
        self.t_destroy_model(f"City {uuid}")

    def test_destroy_command(self):
        """Tests for the destroy command"""
        self.t_cmd_output_test("destroy", "** class name missing **")
        self.t_cmd_output_test("destroy User", "** instance id missing **")
        self.t_cmd_output_test("destroy xyz", "** class doesn't exist **")

        uuid = self.t_create_model("City")  # creating known model
        self.t_cmd_output_test(f"show City {uuid}", uuid)  # exists
        self.t_cmd_output_test(f"destroy City {uuid}", "")  # destroy it
        self.t_cmd_output_test(f"show City {uuid}", "** no instance found **")

        uuid = self.t_create_model("Place")  # creating known model
        self.t_cmd_output_test(f"show Place {uuid}", uuid)  # exists
        self.t_cmd_output_test(f'Place.destroy("{uuid}")', "")  # destroy it
        self.t_cmd_output_test(f"show Place {uuid}", "** no instance found **")

    def test_all_command(self):
        """Tests for the all command"""
        # Test the all command: output is bounded by '[' and ']'
        self.assertRegex(self.t_cmd_output("all"), r"(^\[.*]$)")

        # Create a user, place, city, and test they exists
        uuids, models = [], ("City", "User", "User", "User", "Place")
        for model in models:  # create them
            uuids.append(self.t_create_model(model))

        output = self.t_cmd_output("all")
        for uuid in uuids:  # test that the each uuid is present in the output
            self.assertIn(uuid, output)

        output = self.t_cmd_output("all User")
        for uuid in uuids[1:4]:  # test that all three users appear in output
            self.assertIn(uuid, output)

        output = self.t_cmd_output("User.all()")
        for uuid in uuids[1:4]:  # test that all three users appear in output
            self.assertIn(uuid, output)

        for model, uuid in zip(models, uuids):
            self.t_destroy_model(f"{model} {uuid}")  # destroy them

    def test_count_command(self):
        """Tests for the count command"""
        self.t_cmd_output_test("count", "* class name missing **")
        users = self.t_fetch_model("User")  # get all the users
        n_users = len(users)
        self.t_cmd_output_test("count User", "{}".format(n_users))
        self.t_cmd_output_test("count xyz", "** class doesn't exist **")

        uuids = [self.t_create_model("User") for _ in range(3)]  # 3 new users
        self.t_cmd_output_test("count User", "{}".format(n_users+3))
        self.t_cmd_output_test("User.count()", "{}".format(n_users+3))

        for uuid in uuids:  # destroy the 3 users
            self.t_destroy_model(f"User {uuid}")

    def test_update_command(self):
        """Tests update command"""
        self.t_cmd_output_test("update", "* class name missing **")
        self.t_cmd_output_test("update xyz", "** class doesn't exist **")
        self.t_cmd_output_test("update User", "** instance id missing **")

        ud = self.t_create_model("User")
        self.t_cmd_output_test(f"show User {ud}", ud)  # check that User exists
        self.t_cmd_output_test(f"update User {ud}", "attribute name missing")

        # Test for different ways of using the update command
        expected = """'email': 'abc@gmail.com'"""  # Update the nomal way
        self.t_cmd_output_test(f'update User {ud} email "abc@gmail.com"', "")
        self.t_cmd_output_test(f"show User {ud}", expected)  # Did it work?

        expected = """'age': 36"""  # Update using dot notation
        self.t_cmd_output_test(f'User.update("{ud}", "age", 36)', "")
        self.t_cmd_output_test(f"show User {ud}", expected)  # Did it work?

        expected = """'name': 'Michael'"""  # Update using dot notation
        self.t_cmd_output_test(
            f'User.update("{ud}", {{"name": "Michael"}})', "")
        self.t_cmd_output_test(f"show User {ud}", expected)  # Did it work?

        self.t_destroy_model(f"User {ud}")  # Destroy the  created user


if __name__ == "__main__":
    unittest.main()
