#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
module: gelf_logger

short_description: sends gelf messages to a remote endpoint

version_added: "2.4"

options: 
    dest: 
        description: 
            - "The adress of the endpoint. Specify as (tcp|udp|http)://host:port/path"
        required: true
    host:
        description:
            - "The host the message is FROM. Defaults to {{ ansible_hostname }}
        required: false
    timestamp:
        description:
            - "The timestamp of the message. Defaults to time.time()
        required: false
    message:
        description:
            - The message you want to log. maps to GELFs short_message field
        required: true
    full_message
        description:
            - The full message field. Use this for bigger stuff. Maps to GELFs full_message field
        required: false

'''

EXAMPLES = '''
'''

RETURN = '''
gelf:
    description: "the generated gelf json body"
    type: str
'''

from ansible.module_utils.basic import AnsibleModule

def run_module():
    module_args = dict(
        dest=dict(type='str', required=True),
        host=dict(type='str'),
        timestamp=dict(type='int'),
        message=dict(type='str', required=True),
        full_message=dict(type='str')
    )

    result = dict(
        gelf = "",
        changed = False
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    result['gelf'] = module.params['message']

    if module.check_mode:
        return result

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()


