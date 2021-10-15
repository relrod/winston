""" tests for runner.api
"""

import pytest

from ansible_navigator.runner import api


@pytest.mark.parametrize(
    "orig_exec, orig_args, exp_stdout, exp_interactive",
    [
        (
            "ansible-lint",
            [],
            ["-c 'exec 2>/dev/null; ansible-lint'"],
            ["-c", "exec 2>/dev/null; ansible-lint"],
        ),
        (
            "ansible-lint",
            ["/tmp/myroles/supercool/tasks/main.yml"],
            ["-c 'exec 2>/dev/null; ansible-lint /tmp/myroles/supercool/tasks/main.yml'"],
            ["-c", "exec 2>/dev/null; ansible-lint /tmp/myroles/supercool/tasks/main.yml"],
        ),
        (
            "ansible-lint",
            ["lintable1", "lintable2", "lintable3"],
            ["-c 'exec 2>/dev/null; ansible-lint lintable1 lintable2 lintable3'"],
            ["-c", "exec 2>/dev/null; ansible-lint lintable1 lintable2 lintable3"],
        ),
        (
            "ansible-lint",
            ["lintable1", "lint\"able'2", "lint able3"],
            [
                (
                    "-c 'exec 2>/dev/null; ansible-lint lintable1 "
                    "'\"'\"'lint\"able'\"'\"'\"'\"'\"'\"'\"'\"'2'\"'\"' '\"'\"'lint able3'\"'\"''"
                )
            ],
            ["-c", "exec 2>/dev/null; ansible-lint lintable1 'lint\"able'\"'\"'2' 'lint able3'"],
        ),
    ],
    ids=[
        "only executable command",
        "executable command with one argument",
        "executable command with several arguments",
        "executable command with arguments containing quotes and spaces",
    ],
)
def test_command_base_runner_wrap_sh(orig_exec, orig_args, exp_stdout, exp_interactive):
    """test CommandBaseRunner properly wraps commands with sh -c when asked."""

    # default (no sh wrap)
    cr = api.CommandRunner(orig_exec, cmdline=orig_args[:])
    cr.generate_run_command_args()
    assert cr._runner_args.get("executable_cmd") == orig_exec
    assert cr._runner_args.get("cmdline_args") == orig_args

    # explicit sh wrap - stdout mode
    cr = api.CommandRunner(orig_exec, cmdline=orig_args[:], wrap_sh=True, navigator_mode="stdout")
    cr.generate_run_command_args()
    assert cr._runner_args.get("executable_cmd") == "/bin/sh"
    assert cr._runner_args.get("cmdline_args") == exp_stdout

    # explicit sh wrap - interactive mode
    cr = api.CommandRunner(
        orig_exec, cmdline=orig_args[:], wrap_sh=True, navigator_mode="interactive"
    )
    cr.generate_run_command_args()
    assert cr._runner_args.get("executable_cmd") == "/bin/sh"
    assert cr._runner_args.get("cmdline_args") == exp_interactive
