"""Run the :exec subcommand."""
import logging
import os
import shlex

from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from ..action_base import ActionBase
from ..action_defs import RunStdoutReturn
from ..configuration_subsystem import ApplicationConfiguration
from ..configuration_subsystem.navigator_settings import NavigatorSettings
from ..configuration_subsystem.definitions import Constants
from ..runner import Command
from . import _actions as actions


GeneratedCommand = Tuple[str, Optional[List[str]]]

logger = logging.getLogger(__name__)


def _generate_command(
    exec_command: str,
    exec_shell: bool,
    extra_args: Union[Constants, List[str]],
) -> GeneratedCommand:
    """Generate the command and args.

    :param exec_command: The command to run
    :param exec_shell: Should the command be wrapped in a shell
    :param extra_args: Any unknown or extra arguments passed on the command line
    :returns: The command and any pass through arguments
    """
    logger.debug("exec_command: %s", exec_command)
    logger.debug("exec_shell: %s", exec_shell)
    logger.debug("extra_args: %s", extra_args)
    if exec_shell and exec_command:
        command = "/bin/bash"
        # Determine if any extra args were picked up
        _extra_args = extra_args if isinstance(extra_args, list) else ()
        pass_command = " ".join((exec_command, *_extra_args))
        pass_through_args = ["-c", pass_command]
    else:
        parts = shlex.split(exec_command)
        command = parts[0]
        if len(parts) == 1 and isinstance(extra_args, list):
            # Use the extra arguments
            pass_through_args = extra_args
        else:
            # Use the leftovers or an empty list
            pass_through_args = parts[1:]
    logger.debug("runner command: %s", command)
    logger.debug("runner passthrough: %s", pass_through_args)
    return (command, pass_through_args)


@actions.register
class Action(ActionBase):
    """Run the :exec subcommand."""

    KEGEX = "^e(?:xec)?$"

    def __init__(self, args: ApplicationConfiguration[NavigatorSettings]):
        """Initialize the ``:exec`` action.

        :param args: The current settings for the application
        """
        super().__init__(args=args, logger_name=__name__, name="exec")

    def run_stdout(self) -> RunStdoutReturn:
        """Execute the ``exec`` request for mode stdout.

        :returns: The return code or 1. If the response from the runner invocation is None,
            indicates there is no console output to display, so assume an issue and return 1
            along with a message to review the logs.
        """
        self._logger.debug("exec requested in stdout mode")
        response = self._run_runner()
        if response is None:
            self._logger.error("Unexpected response: %s", response)
            return RunStdoutReturn(message="Please review the log for errors.", return_code=1)
        _out, error, return_code = response
        return RunStdoutReturn(message=error, return_code=return_code)

    def _run_runner(self) -> Optional[Tuple]:
        """Spin up runner.

        :returns: The stdout, stderr and return code from runner
        """
        if isinstance(self._args.entries.set_environment_variable.current, dict):
            env_vars_to_set = self._args.entries.set_environment_variable.current.copy()
        elif isinstance(self._args.entries.set_environment_variable.current, Constants):
            env_vars_to_set = {}
        else:
            log_message = (
                "The setting 'set_environment_variable' was neither a dictionary"
                " or Constants, please raise an issue. No environment variables will be set."
            )
            self._logger.error(
                "%s The current value was found to be '%s'",
                log_message,
                self._args.entries.set_environment_variable.current,
            )
            env_vars_to_set = {}

        if self._args.entries.display_color.current is False:
            env_vars_to_set["ANSIBLE_NOCOLOR"] = "1"

        kwargs = {
            "container_engine": self._args.entries.container_engine.current,
            "host_cwd": os.getcwd(),
            "execution_environment_image": self._args.entries.execution_environment_image.current,
            "execution_environment": self._args.entries.execution_environment.current,
            "navigator_mode": self._args.entries.mode.current,
            "pass_environment_variable": self._args.entries.pass_environment_variable.current,
            "set_environment_variable": env_vars_to_set,
            "timeout": self._args.entries.ansible_runner_timeout.current,
        }

        if isinstance(self._args.entries.execution_environment_volume_mounts.current, list):
            kwargs["container_volume_mounts"] = self._args.entries.execution_environment_volume_mounts.current

        if isinstance(self._args.entries.container_options.current, list):
            kwargs["container_options"] = self._args.entries.container_options.current

        command, pass_through_args = _generate_command(
            exec_command=self._args.entries.exec_command.current,
            exec_shell=self._args.entries.exec_shell.current,
            extra_args=self._args.entries.cmdline.current,
        )
        if isinstance(pass_through_args, list):
            kwargs["cmdline"] = pass_through_args

        runner = Command(executable_cmd=command, **kwargs)
        return runner.run()
