"""``:rerun`` command implementation."""
import copy
import logging

from ..app_public import AppPublic
from ..configuration_subsystem import ApplicationConfiguration
from ..configuration_subsystem.navigator_settings import NavigatorSettings
from ..ui_framework import Interaction
from . import _actions as actions


@actions.register
class Action:
    """``:rerun`` command implementation."""

    KEGEX = r"^rr|rerun?$"

    def __init__(self, args: ApplicationConfiguration[NavigatorSettings]):
        """Initialize the ``:rerun`` action.

        :param args: The current settings for the application
        """
        self._args = args
        self._logger = logging.getLogger(__name__)

    # pylint: disable=unused-argument
    def run(self, interaction: Interaction, app: AppPublic) -> None:
        """Execute the ``:rerun`` request for mode interactive.

        :param interaction: The interaction from the user
        :param app: The app instance
        """
        self._logger.debug("rerun requested")
        this = copy.copy(app.steps.current)
        app.rerun()
        # ensure we are last on the stack
        if app.steps.current != this:
            app.steps.append(this)
