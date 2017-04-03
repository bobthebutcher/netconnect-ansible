#! /usr/bin/env python


import os

from ansible.module_utils.basic import AnsibleModule

from netconnect.arista.arista_driver import AristaDriver
from netconnect.exceptions import (
    LoginTimeoutError,
    LoginCredentialsError,
    EnablePasswordError,
)


def get_result(device, username, password, enable_password, commands,
               ssh_config_file, ignore_ssh_config, timeout):

    if ssh_config_file.startswith('~'):
        ssh_config_file = os.path.expanduser('~/.ssh/config')

    fail_reason = ''
    dev = AristaDriver(device=device, username=username, password=password,
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
    # mgmt_int = results[0].split('\r\n')[1].split(' ')[0]

    if fail_reason:
        result = {
            'result':  fail_reason,
            'success': False,
        }
    else:
        result = {
            'result':  results,
            # 'mgmt_int': mgmt_int,
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
        module.exit_json(result=result['result'])  # , mgmt_int=result['mgmt_int'])
    else:
        module.fail_json(msg=result['result'])


if __name__ == '__main__':
    main()
