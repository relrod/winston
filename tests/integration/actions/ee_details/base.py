""" base class for stdout interactive tests
"""
import difflib
import json
import os
import shlex

from types import SimpleNamespace

from typing import List
from typing import NamedTuple
from typing import Union

import pytest

from ..._common import container_runtime_or_fail
from ..._common import fixture_path_from_request
from ..._common import update_fixtures
from ..._common import TmuxSession
from ....defaults import FIXTURES_DIR


TEST_FIXTURE_DIR = os.path.join(FIXTURES_DIR, "integration/actions/ee_details")
TEST_CONFIG_FILE = os.path.join(TEST_FIXTURE_DIR, "ansible-navigator.yml")


class Command(NamedTuple):
    """command details"""

    execution_environment: bool
    container_engine: str = container_runtime_or_fail()
    command: str = "ansible-navigator"
    subcommand: Union[None, str] = None

    def join(self):
        """create cli command"""
        args = []
        args.append(self.command)
        if self.subcommand is not None:
            args.append(self.subcommand)
        args.extend(["--ee", self.execution_environment])
        args.extend(["--ce", self.container_engine])
        return " ".join(shlex.quote(str(arg)) for arg in args)


class Step(SimpleNamespace):
    # pylint: disable=too-few-public-methods
    """test data object"""
    user_input: str
    comment: str

    index: int = 0
    look_fors: List[str] = []
    playbook_status: Union[None, str] = None


class Steps(list):
    """a list of test steps"""

    def add_indicies(self):
        """update the index of each"""
        for idx, step in enumerate(self):
            step.index = idx
        return self

    @staticmethod
    def step_id(value):
        """return the test id from the test step object"""
        return f"{value.index}-{value.comment}"


base_steps = Steps(
    [
        Step(user_input=":0", comment="Check gather"),
        Step(user_input=":back", comment="Return to play list"),
        Step(user_input=":1", comment="Check report"),
        Step(user_input=":back", comment="Return to playlist"),
        Step(user_input=":2", comment="Report tasks"),
        Step(user_input=":0", comment="View report", look_fors=["ansible_version", "base_os"]),
    ]
)


class BaseClass:
    """base class for interactive stdout tests"""

    UPDATE_FIXTURES = False

    @staticmethod
    @pytest.fixture(scope="module", name="tmux_session")
    def fixture_tmux_session(request):
        """tmux fixture for this module"""
        params = {
            "window_name": request.node.name,
            "setup_commands": [
                "export ANSIBLE_DEVEL_WARNING=False",
                "export ANSIBLE_DEPRECATION_WARNINGS=False",
            ],
            "config_path": TEST_CONFIG_FILE,
            "pane_height": "100",
        }
        with TmuxSession(**params) as tmux_session:
            yield tmux_session

    def test(self, request, tmux_session, step):
        # pylint:disable=unused-argument
        # pylint: disable=too-few-public-methods
        # pylint: disable=too-many-arguments

        """test"""
        assert os.path.exists(TEST_CONFIG_FILE)

        received_output = tmux_session.interaction(
            step.user_input, wait_on_playbook_status=step.playbook_status
        )
        if self.UPDATE_FIXTURES:
            update_fixtures(request, step.index, received_output, step.comment)
        dir_path, file_name = fixture_path_from_request(request, step.index)
        with open(f"{dir_path}/{file_name}") as infile:
            expected_output = json.load(infile)["output"]

        if step.look_fors:
            for look_for in step.look_fors:
                assert any(look_for in line for line in received_output), (
                    look_for,
                    "\n".join(received_output),
                )
        else:
            assert expected_output == received_output, "\n" + "\n".join(
                difflib.unified_diff(expected_output, received_output, "expected", "received")
            )
