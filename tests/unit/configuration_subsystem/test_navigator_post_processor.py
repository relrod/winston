"""Tests for the navigator config post-processor."""

import pytest

from ansible_navigator.configuration_subsystem.definitions import Constants
from ansible_navigator.configuration_subsystem.navigator_post_processor import (
    VolumeMount,
)
from ansible_navigator.configuration_subsystem.navigator_post_processor import (
    VolumeMountOption,
)


@pytest.mark.parametrize(
    ("inp", "expected"),
    (
        ("", set()),
        ("Z", {VolumeMountOption.Z}),
        ("Z,z", {VolumeMountOption.Z, VolumeMountOption.z}),
        ("Z,z,Z", {VolumeMountOption.Z, VolumeMountOption.z}),
    ),
    ids=(
        "empty",
        "singleton",
        "pair",
        "repeated element",
    ),
)
def test_option_list_from_comma_string(inp, expected):
    assert VolumeMount.option_list_from_comma_string(inp) == expected


@pytest.mark.parametrize(
    ("volmount", "expected"),
    (
        (
            VolumeMount(
                fs_destination="/bar",
                fs_source="/foo",
                options=[],
                settings_entry="test_option",
                source=Constants.USER_CLI,
            ),
            "/foo:/bar",
        ),
        (
            VolumeMount(
                settings_entry="test_option",
                fs_source="/foo",
                fs_destination="/bar",
                options=[VolumeMountOption.z],
                source=Constants.USER_CLI,
            ),
            "/foo:/bar:z",
        ),
        (
            VolumeMount(
                settings_entry="test_option",
                fs_source="/foo",
                fs_destination="/bar",
                options=[VolumeMountOption.z, VolumeMountOption.Z],
                source=Constants.USER_CLI,
            ),
            "/foo:/bar:z,Z",
        ),
        (
            VolumeMount(
                settings_entry="test_option",
                fs_source="/foo",
                fs_destination="/bar",
                options=[],
                source=Constants.USER_CLI,
            ),
            "/foo:/bar",
        ),
    ),
    ids=(
        "normal mount",
        "mount with relabel option",
        "mount with a list of options",
        "mount with empty list of options",
    ),
)
def test_navigator_volume_mount_to_string(volmount, expected):
    """Make sure volume mount ``to_string`` is sane.

    :param volmount: The volume mount to test
    :param expected: The expected string resulting from the conversion of the mount to a string
    """
    assert volmount.to_string() == expected
