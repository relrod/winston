"""ansible-navigator settings class
"""

import logging
import os

from dataclasses import dataclass
from dataclasses import fields

from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

from ..utils.functions import ExitMessage
from ..utils.functions import LogMessage
from ..utils.functions import abs_user_path
from ..utils.functions import get_share_directory
from ..utils.functions import oxfordcomma

from .definitions import Constants as C
from .definitions import CliParameters
from .definitions import SettingsEntry
from .definitions import SettingsEntryValue
from .definitions import SubCommand

initialization_messages: List[LogMessage] = []
initialization_exit_messages: List[ExitMessage] = []

PLUGIN_TYPES: Tuple[str, ...] = (
    "become",
    "cache",
    "callback",
    "cliconf",
    "connection",
    "httpapi",
    "inventory",
    "lookup",
    "module",
    "netconf",
    "shell",
    "strategy",
    "vars",
)


APP_NAME: str = "ansible_navigator"


def generate_editor_command() -> str:
    """Generate a default for editor_command if EDITOR is set"""
    editor = os.environ.get("EDITOR")
    if editor is None:
        message = "EDITOR environment variable not set"
        initialization_messages.append(LogMessage(level=logging.DEBUG, message=message))
        command = "vi +{line_number} {filename}"
    else:
        message = f"EDITOR environment variable set as '{editor}'"
        initialization_messages.append(LogMessage(level=logging.DEBUG, message=message))
        command = f"{editor!s} {{filename}}"
    message = f"Default editor_command set to: {command}"
    initialization_messages.append(LogMessage(level=logging.DEBUG, message=message))
    return command


def generate_cache_path():
    """Generate a path for the collection cache"""
    file_name = "collection_doc_cache.db"
    cache_home = os.environ.get("XDG_CACHE_HOME", f"{os.path.expanduser('~')}/.cache")
    cache_path = os.path.join(cache_home, APP_NAME.replace("_", "-"), file_name)
    message = f"Default collection_doc_cache_path set to: {cache_path}"
    initialization_messages.append(LogMessage(level=logging.DEBUG, message=message))
    return cache_path


def generate_share_directory():
    """Generate a share director"""
    messages, exit_messages, share_directory = get_share_directory(APP_NAME)
    initialization_messages.extend(messages)
    initialization_exit_messages.extend(exit_messages)
    return share_directory

navigator_subcommands = [
    SubCommand(
        name="builder",
        description="Build execution environment (container image)",
        epilog=(
            "Note: 'ansible-navigator builder' additionally supports"
            " the same parameters as the 'ansible-builder' command."
            " For more information about these, try "
            " 'ansible-navigator builder --help-builder --mode stdout'"
        ),
    ),
    SubCommand(name="collections", description="Explore available collections"),
    SubCommand(
        name="config",
        description="Explore the current ansible configuration",
        epilog=(
            "Note: With '--mode stdout', 'ansible-navigator config' additionally supports"
            " the same parameters as the 'ansible-config' command."
            " For more information about these, try "
            " 'ansible-navigator config --help-config --mode stdout'"
        ),
    ),
    SubCommand(
        name="doc",
        description="Review documentation for a module or plugin",
        epilog=(
            "Note: With '--mode stdout', 'ansible-navigator doc' additionally supports"
            " the same parameters as the 'ansible-doc' command."
            " For more information about these, try "
            " 'ansible-navigator doc --help-doc --mode stdout'"
        ),
    ),
    SubCommand(
        name="exec",
        description="Run a command within an execution environment",
        epilog=(
            "Note: During development, it may become necessary to interact"
            " directly with the execution environment to review and confirm"
            " its build and behavior. All navigator settings will be applied"
            " when starting the execution environment."
        ),
    ),
    SubCommand(
        name="images",
        description="Explore execution environment images",
    ),
    SubCommand(
        name="inventory",
        description="Explore an inventory",
        epilog=(
            "Note: With '--mode stdout', 'ansible-navigator inventory' additionally supports"
            " the same parameters as the 'ansible-inventory' command."
            " For more information about these, try "
            " 'ansible-navigator inventory --help-inventory --mode stdout'"
        ),
    ),
    SubCommand(name="replay", description="Explore a previous run using a playbook artifact"),
    SubCommand(
        name="run",
        description="Run a playbook",
        epilog=(
            "Note: 'ansible-navigator run' additionally supports"
            " the same parameters as the 'ansible-playbook' command."
            " For more information about these, try "
            " 'ansible-navigator run --help-playbook --mode stdout'"
        ),
    ),
    SubCommand(name="welcome", description="Start at the welcome page"),
]


@dataclass
class NavigatorSettings:
    # This is temporary to avoid having to make a bunch of changes to
    # configurator for now.
    # TODO
    def __iter__(self):
        for field in fields(self):
            yield getattr(self, field.name)

    ansible_runner_artifact_dir: SettingsEntry[str] = SettingsEntry(
        name="ansible_runner_artifact_dir",
        cli_parameters=CliParameters(short="--rad"),
        settings_file_path_override="ansible-runner.artifact-dir",
        short_description="The directory path to store artifacts generated by ansible-runner",
        value=SettingsEntryValue(),
    )
    ansible_runner_rotate_artifacts_count: SettingsEntry[int] = SettingsEntry(
        name="ansible_runner_rotate_artifacts_count",
        cli_parameters=CliParameters(short="--rac"),
        settings_file_path_override="ansible-runner.rotate-artifacts-count",
        short_description="Keep ansible-runner artifact directories, "
        "for last n runs, if set to 0 artifact directories "
        "won't be deleted",
        value=SettingsEntryValue(),
    )
    ansible_runner_timeout: SettingsEntry[int] = SettingsEntry(
        name="ansible_runner_timeout",
        cli_parameters=CliParameters(short="--rt"),
        settings_file_path_override="ansible-runner.timeout",
        short_description="The timeout value after which ansible-runner will"
        "force stop the execution",
        value=SettingsEntryValue(),
    )
    app: SettingsEntry[str] = SettingsEntry(
        name="app",
        apply_to_subsequent_cli=C.NONE,
        choices=[subcommand.name for subcommand in navigator_subcommands],
        short_description="Subcommands",
        subcommand_value=True,
        value=SettingsEntryValue(default="welcome"),
    )
    cmdline: SettingsEntry[Union[str, List[str]]] = SettingsEntry(
        name="cmdline",
        apply_to_subsequent_cli=C.SAME_SUBCOMMAND,
        settings_file_path_override="ansible.cmdline",
        short_description="Extra parameters passed to the corresponding command",
        value=SettingsEntryValue(),
    )
    collection_doc_cache_path: SettingsEntry[str] = SettingsEntry(
        name="collection_doc_cache_path",
        cli_parameters=CliParameters(short="--cdcp"),
        short_description="The path to collection doc cache",
        value=SettingsEntryValue(default=generate_cache_path()),
    )
    config: SettingsEntry[str] = SettingsEntry(
        name="config",
        cli_parameters=CliParameters(short="-c", metavar="CONFIG_FILE"),
        environment_variable_override="ansible_config",
        settings_file_path_override="ansible.config",
        short_description="Specify the path to the ansible configuration file",
        subcommands=["config"],
        value=SettingsEntryValue(),
    )
    container_engine: SettingsEntry[Union[bool, str]] = SettingsEntry(
        name="container_engine",
        choices=["auto", "podman", "docker"],
        cli_parameters=CliParameters(short="--ce"),
        settings_file_path_override="execution-environment.container-engine",
        short_description="Specify the container engine (auto=podman then docker)",
        value=SettingsEntryValue(default="auto"),
    )
    container_options: SettingsEntry[List[str]] = SettingsEntry(
        name="container_options",
        cli_parameters=CliParameters(action="append", nargs="+", short="--co"),
        environment_variable_override="ansible_navigator_container_options",
        settings_file_path_override="execution-environment.container-options",
        short_description="Extra parameters passed to the container engine command",
        value=SettingsEntryValue(),
    )
    display_color: SettingsEntry[Union[str, bool]] = SettingsEntry(
        name="display_color",
        change_after_initial=False,
        choices=[True, False],
        cli_parameters=CliParameters(short="--dc"),
        environment_variable_override="no_color",
        settings_file_path_override="color.enable",
        short_description="Enable the use of color in the display",
        value=SettingsEntryValue(default=True),
    )
    editor_command: SettingsEntry[str] = SettingsEntry(
        name="editor_command",
        cli_parameters=CliParameters(short="--ecmd"),
        settings_file_path_override="editor.command",
        short_description="Specify the editor command",
        value=SettingsEntryValue(default=generate_editor_command()),
    )
    editor_console: SettingsEntry[Union[str, bool]] = SettingsEntry(
        name="editor_console",
        choices=[True, False],
        cli_parameters=CliParameters(short="--econ"),
        settings_file_path_override="editor.console",
        short_description="Specify if the editor is console based",
        value=SettingsEntryValue(default=True),
    )
    exec_command: SettingsEntry[str] = SettingsEntry(
        name="exec_command",
        cli_parameters=CliParameters(positional=True),
        settings_file_path_override="exec.command",
        short_description="Specify the command to run within the execution environment",
        subcommands=["exec"],
        value=SettingsEntryValue(default="/bin/bash"),
    )
    exec_shell: SettingsEntry[Union[str, bool]] = SettingsEntry(
        name="exec_shell",
        choices=[True, False],
        cli_parameters=CliParameters(short="--exshell"),
        settings_file_path_override="exec.shell",
        short_description="Specify the exec command should be run in a shell.",
        subcommands=["exec"],
        value=SettingsEntryValue(default=True),
    )
    execution_environment: SettingsEntry[Union[str, bool]] = SettingsEntry(
        name="execution_environment",
        choices=[True, False],
        cli_parameters=CliParameters(short="--ee"),
        settings_file_path_override="execution-environment.enabled",
        short_description="Enable or disable the use of an execution environment",
        value=SettingsEntryValue(default=True),
    )
    execution_environment_image: SettingsEntry[str] = SettingsEntry(
        name="execution_environment_image",
        cli_parameters=CliParameters(short="--eei"),
        settings_file_path_override="execution-environment.image",
        short_description="Specify the name of the execution environment image",
        value=SettingsEntryValue(default="quay.io/ansible/creator-ee:v0.2.0"),
    )
    execution_environment_volume_mounts: SettingsEntry[Union[List[str], List[Dict[str, str]]]] = SettingsEntry(
        name="execution_environment_volume_mounts",
        cli_parameters=CliParameters(action="append", nargs="+", short="--eev"),
        delay_post_process=True,
        environment_variable_split_char=";",
        settings_file_path_override="execution-environment.volume-mounts",
        short_description=(
            "Specify volume to be bind mounted within an execution environment"
            " (--eev /home/user/test:/home/user/test:Z)"
        ),
        value=SettingsEntryValue(),
    )
    help_builder: SettingsEntry[Union[str, bool]] = SettingsEntry(
        name="help_builder",
        choices=[True, False],
        cli_parameters=CliParameters(short="--hb", action="store_true"),
        short_description="Help options for ansible-builder command in stdout mode",
        subcommands=["builder"],
        value=SettingsEntryValue(default=False),
    )
    help_config: SettingsEntry[Union[str, bool]] = SettingsEntry(
        name="help_config",
        choices=[True, False],
        cli_parameters=CliParameters(short="--hc", action="store_true"),
        short_description="Help options for ansible-config command in stdout mode",
        subcommands=["config"],
        value=SettingsEntryValue(default=False),
    )
    help_doc: SettingsEntry[Union[str, bool]] = SettingsEntry(
        name="help_doc",
        choices=[True, False],
        cli_parameters=CliParameters(short="--hd", action="store_true"),
        short_description="Help options for ansible-doc command in stdout mode",
        subcommands=["doc"],
        value=SettingsEntryValue(default=False),
    )
    help_inventory: SettingsEntry[Union[str, bool]] = SettingsEntry(
        name="help_inventory",
        choices=[True, False],
        cli_parameters=CliParameters(short="--hi", action="store_true"),
        short_description="Help options for ansible-inventory command in stdout mode",
        subcommands=["inventory"],
        value=SettingsEntryValue(default=False),
    )
    help_playbook: SettingsEntry[Union[str, bool]] = SettingsEntry(
        name="help_playbook",
        choices=[True, False],
        cli_parameters=CliParameters(short="--hp", action="store_true"),
        short_description="Help options for ansible-playbook command in stdout mode",
        subcommands=["run"],
        value=SettingsEntryValue(default=False),
    )
    inventory: SettingsEntry[Union[List[str], str]] = SettingsEntry(
        name="inventory",
        cli_parameters=CliParameters(action="append", nargs="+", short="-i"),
        environment_variable_override="ansible_navigator_inventories",
        settings_file_path_override="ansible.inventories",
        short_description="Specify an inventory file path or comma separated host list",
        subcommands=["inventory", "run"],
        value=SettingsEntryValue(),
    )
    inventory_column: SettingsEntry[List[str]] = SettingsEntry(
        name="inventory_column",
        cli_parameters=CliParameters(action="append", nargs="+", short="--ic"),
        environment_variable_override="ansible_navigator_inventory_columns",
        settings_file_path_override="inventory-columns",
        short_description="Specify a host attribute to show in the inventory view",
        subcommands=["inventory", "run"],
        value=SettingsEntryValue(),
    )
    log_append: SettingsEntry[Union[str, bool]] = SettingsEntry(
        name="log_append",
        choices=[True, False],
        cli_parameters=CliParameters(short="--la"),
        short_description=(
            "Specify if log messages should be appended to an existing log file,"
            " otherwise a new log file will be created per session"
        ),
        settings_file_path_override="logging.append",
        value=SettingsEntryValue(default=True),
    )
    log_file: SettingsEntry[str] = SettingsEntry(
        name="log_file",
        cli_parameters=CliParameters(short="--lf"),
        short_description="Specify the full path for the ansible-navigator log file",
        settings_file_path_override="logging.file",
        value=SettingsEntryValue(default=abs_user_path("./ansible-navigator.log")),
    )
    log_level: SettingsEntry[str] = SettingsEntry(
        name="log_level",
        choices=["debug", "info", "warning", "error", "critical"],
        cli_parameters=CliParameters(short="--ll"),
        short_description="Specify the ansible-navigator log level",
        settings_file_path_override="logging.level",
        value=SettingsEntryValue(default="warning"),
    )
    mode: SettingsEntry[str] = SettingsEntry(
        name="mode",
        change_after_initial=False,
        choices=["stdout", "interactive"],
        cli_parameters=CliParameters(short="-m"),
        short_description="Specify the user-interface mode",
        value=SettingsEntryValue(default="interactive"),
    )
    osc4: SettingsEntry[Union[str, bool]] = SettingsEntry(
        name="osc4",
        choices=[True, False],
        cli_parameters=CliParameters(short="--osc4"),
        settings_file_path_override="color.osc4",
        short_description="Enable or disable terminal color changing support with OSC 4",
        value=SettingsEntryValue(default=True),
    )
    pass_environment_variable: SettingsEntry[List[str]] = SettingsEntry(
        name="pass_environment_variable",
        cli_parameters=CliParameters(action="append", nargs="+", short="--penv"),
        environment_variable_override="ansible_navigator_pass_environment_variables",
        settings_file_path_override="execution-environment.environment-variables.pass",
        short_description=(
            "Specify an exiting environment variable to be passed through"
            " to and set within the execution environment (--penv MY_VAR)"
        ),
        value=SettingsEntryValue(),
    )
    playbook: SettingsEntry[str] = SettingsEntry(
        name="playbook",
        cli_parameters=CliParameters(positional=True),
        short_description="Specify the playbook name",
        settings_file_path_override="ansible.playbook",
        subcommands=["run"],
        value=SettingsEntryValue(),
    )
    playbook_artifact_enable: SettingsEntry[Union[str, bool]] = SettingsEntry(
        name="playbook_artifact_enable",
        choices=[True, False],
        cli_parameters=CliParameters(short="--pae"),
        settings_file_path_override="playbook-artifact.enable",
        short_description="Enable or disable the creation of artifacts for"
        " completed playbooks. Note: not compatible with '--mode stdout' when playbooks"
        " require user input",
        subcommands=["run"],
        value=SettingsEntryValue(default=True),
    )
    playbook_artifact_replay: SettingsEntry[str] = SettingsEntry(
        name="playbook_artifact_replay",
        cli_parameters=CliParameters(positional=True),
        settings_file_path_override="playbook-artifact.replay",
        short_description="Specify the path for the playbook artifact to replay",
        subcommands=["replay"],
        value=SettingsEntryValue(),
    )
    playbook_artifact_save_as: SettingsEntry[str] = SettingsEntry(
        name="playbook_artifact_save_as",
        cli_parameters=CliParameters(short="--pas"),
        settings_file_path_override="playbook-artifact.save-as",
        short_description="Specify the name for artifacts created from completed playbooks",
        subcommands=["run"],
        value=SettingsEntryValue(
            default="{playbook_dir}/{playbook_name}-artifact-{ts_utc}.json",
        )
    )
    plugin_name: SettingsEntry[str] = SettingsEntry(
        name="plugin_name",
        cli_parameters=CliParameters(positional=True),
        settings_file_path_override="documentation.plugin.name",
        short_description="Specify the plugin name",
        subcommands=["doc"],
        value=SettingsEntryValue(),
    )
    plugin_type: SettingsEntry[str] = SettingsEntry(
        name="plugin_type",
        choices=PLUGIN_TYPES,
        cli_parameters=CliParameters(short="-t", long_override="--type"),
        settings_file_path_override="documentation.plugin.type",
        short_description=f"Specify the plugin type, {oxfordcomma(PLUGIN_TYPES, 'or')}",
        subcommands=["doc"],
        value=SettingsEntryValue(default="module"),
    )
    pull_arguments: SettingsEntry[List[str]] = SettingsEntry(
        name="pull_arguments",
        cli_parameters=CliParameters(action="append", nargs="+", short="--pa"),
        settings_file_path_override="execution-environment.pull.arguments",
        short_description=(
            "Specify any additional parameters that should be added to the"
            " pull command when pulling an execution environment from a container"
            " registry. e.g. --pa='--tls-verify=false'"
        ),
        value=SettingsEntryValue(),
    )
    pull_policy: SettingsEntry[str] = SettingsEntry(
        name="pull_policy",
        choices=["always", "missing", "never", "tag"],
        cli_parameters=CliParameters(short="--pp"),
        settings_file_path_override="execution-environment.pull-policy",
        short_description=(
            "Specify the image pull policy."
            " always:Always pull the image,"
            " missing:Pull if not locally available,"
            " never:Never pull the image,"
            " tag:if the image tag is 'latest', always pull the image,"
            " otherwise pull if not locally available"
        ),
        value=SettingsEntryValue(default="tag"),
    )
    set_environment_variable: SettingsEntry[Union[List[str], Dict[str, str]]] = SettingsEntry(
        name="set_environment_variable",
        cli_parameters=CliParameters(action="append", nargs="+", short="--senv"),
        environment_variable_override="ansible_navigator_set_environment_variables",
        settings_file_path_override="execution-environment.environment-variables.set",
        short_description=(
            "Specify an environment variable and a value to be set within the"
            " execution environment (--senv MY_VAR=42)"
        ),
        value=SettingsEntryValue(),
    )
    workdir: SettingsEntry[str] = SettingsEntry(
        name="workdir",
        cli_parameters=CliParameters(short="--bwd"),
        settings_file_path_override="ansible-builder.workdir",
        short_description="Specify the path that contains ansible-builder manifest files",
        subcommands=["builder"],
        value=SettingsEntryValue(default=os.getcwd()),
    )
