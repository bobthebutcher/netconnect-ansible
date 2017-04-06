#! /usr/bin/env python


import os

from ansible.module_utils.basic import AnsibleModule
try:
    HAS_NETCONNECT = True
    from netconnect.cisco.cisco_asa_driver import CiscoASADriver
    from netconnect.exceptions import (
        LoginTimeoutError,
        LoginCredentialsError,
        EnablePasswordError,
    )
except ImportError:
    HAS_NETCONNECT = False

def get_result(device, username, password, enable_password, commands,
               ssh_config_file, ignore_ssh_config, timeout):

    if not HAS_NETCONNECT:
        result = {
            'result':  'The netconnect library is required for this module.',
            'success': False,
        }
        return result

    if ssh_config_file.startswith('~'):
        ssh_config_file = os.path.expanduser('~/.ssh/config')

    fail_reason = ''
    dev = CiscoASADriver(device=device, username=username, password=password,
                         ssh_config_file=ssh_config_file, ignore_ssh_config=ignore_ssh_config,
                         timeout=timeout)

    try:
        dev.login(enable_password=enable_password) if enable_password else dev.login()
    except LoginTimeoutError:
        fail_reason = 'login timeout error'
    except LoginCredentialsError:
        fail_reason = 'login credentials error'
    except EnablePasswordError:
        fail_reason = 'enable password error'

    results = dev.send_commands(commands)

    if fail_reason:
        result = {
            'result':  fail_reason,
            'success': False,
        }
    else:
        result = {
            'result':  results,
            'success': True,
        }

    return result


def main():
    module = AnsibleModule(
        argument_spec=dict(
            device=dict(required=True, type='str'),
            username=dict(type='str'),
            password=dict(type='str', no_log=True),
            enable_password=dict(type='str', no_log=True),
            ssh_config_file=dict(default='~/.ssh/config', type='str'),
            ignore_ssh_config=dict(default=True, type='bool'),
            timeout=dict(default=5, type='int'),
            commands=dict(required=True, type='list'),
        )
    )

    device = module.params['device']
    username = module.params['username']
    password = module.params['password']
    enable_password = module.params['enable_password']
    ssh_config_file = module.params['ssh_config_file']
    ignore_ssh_config = module.params['ignore_ssh_config']
    timeout = module.params['timeout']
    commands = module.params['commands']

    result = get_result(device, username, password, enable_password, commands,
                        ssh_config_file, ignore_ssh_config, timeout)

    if result['success']:
        module.exit_json(result=result['result'])
    else:
        module.fail_json(msg=result['result'])


if __name__ == '__main__':
    main()
