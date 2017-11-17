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
        required: true
    message:
        description:
            - The message you want to log. maps to GELFs short_message field
        required: true
    full_message
        description:
            - The full message field. Use this for bigger stuff. Maps to GELFs full_message field
        required: false
    level:
        description:
            - the syslog level of the message.
        required: true
    fields:
        description:
            - dictionary with additional fields for the gelf message. The leading underscore will be 
              automatically appended
    
'''

EXAMPLES = '''
'''

RETURN = '''
gelf:
    description: "the generated gelf json body"
    type: str
'''

from ansible.module_utils.basic import AnsibleModule
from urllib.parse import urlparse
import json
import time
import socket

class GelfMessage:
    def __init__(self):
        self.version = "1.1"
        self.timestamp = time.time()

def send_tcp(host, port, gelf):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        sock.send(gelf.encode() + b'\x00')
    finally:
        sock.close()
    return True

def send_udp(host, port, gelf, compression=False):
    return True

def send_http(host, port, path, gelf):
    return true


def run_module():
    module_args = dict(
        dest=dict(type='str', required=True),
        host=dict(type='str', required=True),
        message=dict(type='str', required=True),
        full_message=dict(type='str'),
        level=dict(type='int', required=True),
        fields=dict(type='dict')
    )

    result = dict(
        gelf = "",
        changed = False
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    parse_result = urlparse(module.params['dest'])

    gelf_message = GelfMessage()
    gelf_message.host = module.params['host']
    gelf_message.short_message = module.params['message']

    if module.params['full_message'] is not None:
        gelf_message.full_message = module.params['full_message']
    
    if module.params['fields'] is not None:
        for field in module.params['fields']:
            gelf_message.__dict__["_" + field] = module.params['fields'][field]

    if "tcp" == parse_result.scheme:
        send_tcp(parse_result.hostname, parse_result.port, json.dumps(gelf_message.__dict__))
    elif "http" == parse_result.scheme:
        send_http(parse_result.hostname, parse_result.port, parse_result.path, json.dumps(gelf_message.__dict__))
    elif "udp" == parse_result.scheme:
        send_udp(parse_result.hostname, parse_result.port, json.dumps(gelf_message.__dict__))

    result['gelf'] = json.dumps(gelf_message.__dict__)

    if module.check_mode:
        return result

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()


