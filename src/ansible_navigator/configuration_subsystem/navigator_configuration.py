"""the ansible-navigator configuration
"""

from dataclasses import dataclass
from typing import Optional
from typing import Tuple
from typing import Union

from .definitions import ApplicationConfiguration
from .definitions import Constants as C

from .navigator_post_processor import NavigatorPostProcessor
from .navigator_settings import APP_NAME
from .navigator_settings import NavigatorSettings
from .navigator_settings import generate_share_directory
from .navigator_settings import navigator_subcommands
from .navigator_settings import initialization_exit_messages
from .navigator_settings import initialization_messages

from ..utils.key_value_store import KeyValueStore


@dataclass
class Internals:
    """a place to hold object that need to be carried
    from application initiation to the rest of the app
    """

    action_packages: Tuple[str] = ("ansible_navigator.actions",)
    collection_doc_cache: Union[C, KeyValueStore] = C.NOT_SET
    initializing: bool = False
    """This is an initial run (app starting for the first time)"""
    initialization_exit_messages = initialization_exit_messages
    initialization_messages = initialization_messages
    settings_file_path: Optional[str] = None
    settings_source: C = C.NOT_SET
    share_directory: str = generate_share_directory()


NavigatorConfiguration = ApplicationConfiguration(
    application_name=APP_NAME,
    application_version=C.NOT_SET,
    internals=Internals(),
    post_processor=NavigatorPostProcessor(),
    subcommands=navigator_subcommands,
    entries=NavigatorSettings(),
)
