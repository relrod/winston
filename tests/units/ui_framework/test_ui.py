import pytest

@pytest.fixture
def yaml():
    from ansible_navigator.ui_framework.ui import my_represent_scalar, yaml, \
        Dumper

    # This looks odd, but we set the representer here in the fixture since it
    # is always used in UserInterface in ui.py which is what we're testing.
    old_representer = yaml.representer.BaseRepresenter.represent_scalar
    yaml.representer.BaseRepresenter.represent_scalar = my_represent_scalar

    yield (yaml, Dumper)

    # Right now, there's no reason to do this, but future proof in case there's
    # code that doesn't use the representer in the future and we write tests
    # for that code. Otherwise we change it once here and get unexpected
    # results later on.
    yaml.representer.BaseRepresenter.represent_scalar = old_representer

def test_my_represent_scalar(yaml):
    # Pull out fixture vars
    Dumper = yaml[1]
    yaml = yaml[0]

    data = {
        'examples': ("\n# Test we can logon to 'webservers' and execute "
            "python with json lib.\n# ansible webservers -m ping\n\n- name: "
            "Example from an Ansible Playbook\n  ansible.builtin.ping:\n\n-  "
            "name: Induce an exception to see what happens\n   "
            "ansible.builtin.ping:\n     data: crash\n"),
    }
    expected = '''---
examples: |2-

  # Test we can logon to 'webservers' and execute python with json lib.
  # ansible webservers -m ping

  - name: Example from an Ansible Playbook
    ansible.builtin.ping:

  -  name: Induce an exception to see what happens
     ansible.builtin.ping:
       data: crash
'''
    result = yaml.dump(
        data,
        default_flow_style=False,
        Dumper=Dumper,
        explicit_start=True,
        sort_keys=True)
    assert result == expected
