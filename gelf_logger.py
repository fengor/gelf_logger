#!/usr/bin/python
import json
import time
import socket
import http.client as httplib
from urllib.parse import urlparse
from ansible.module_utils.basic import AnsibleModule

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
module: gelf_logger

short_description: sends gelf messages to a remote endpoint

version_added: "2.5"

options: 
    dest: 
        description: 
            - "The adress of the endpoint. Specify as (tcp|udp|http)://host:port/path"
        required: true
    host:
        description:
            - "The host the message is FROM. 
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
# send gelf via udp
- name: send gelf via udp
  gelf_logger: dest="udp://example.com:12201" host="{{ ansible_hostname }}" level=5 message="say hi"


# send gelf via tcp
- name: send gelf via tcp and full_message attribute
  gelf_logger: dest="tcp://example.com:12201" host="{{ ansible_hostname }}" level=5 message="say hi" full_message="lorem ipsum" 

# send gelf via http and additional fields
- name: send gelf via http
  gelf_logger: 
    dest="http://example.com:12201/gelf" 
    host="{{ ansible_hostname }}" 
    level=5 
    message="say hi"
    fields:
        environment: "test"

'''

RETURN = '''
gelf:
    description: "the generated gelf json body"
    type: str
'''


class GelfMessage:
    """
    Class representing a GELF message
    """
    def __init__(self):
        self.version = "1.1"
        self.timestamp = time.time()
        self.host = None
        self.short_message = None
        self.full_message = None

def send_tcp(host, port, gelf):
    """
    sends a GELF message via tcp
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        sock.send(gelf.encode() + b'\x00')
    finally:
        sock.close()
    return True

def send_udp(host, port, gelf):
    """
    sends a GELF message via udp
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(gelf.encode(), (host, port))
    return True

def send_http(host, port, path, gelf):
    """
    sends a GELF message via http
    """
    conn = httplib.HTTPConnection(host=host, port=port)
    conn.request('POST', path, gelf)
    return True


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
        gelf="",
        changed=False
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

    if parse_result.scheme == "tcp":
        send_tcp(parse_result.hostname, parse_result.port, json.dumps(gelf_message.__dict__))
    elif parse_result.scheme == "http":
        send_http(parse_result.hostname, parse_result.port, parse_result.path, json.dumps(gelf_message.__dict__))
    elif parse_result.scheme == "udp":
        send_udp(parse_result.hostname, parse_result.port, json.dumps(gelf_message.__dict__))

    result['gelf'] = json.dumps(gelf_message.__dict__)

    if module.check_mode:
        return result

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
