from __future__ import print_function
from datetime import datetime
import requests
import json
print('Loading function')


def lambda_handler(event, context):
    with open('./config.json') as f:
        config = json.loads(f.read())
    print("Received event: " + json.dumps(event, indent=2))

    s = requests.Session()
    s.cert = ('./pdbproxy.cert', './pdbproxy.key')
    node_req = '{url}/pdb/v4/nodes/{node}'.format(url=config['puppetdb_url'],
                                                  node=event['detail']['instance-id'])
    resp = s.get(node_req)
    node_obj = resp.json()
    if 'error' in node_obj:
        print("Error: " + node_obj['error'])
        return
    if not node_obj['deactivated']:
        deactivate_cmd = {
            'command': 'deactivate node',
            'version': 3,
            'payload': {
                'certname': event['detail']['instance-id'],
                'producer_timestamp': datetime.isoformat(datetime.now()),
            }
        }
        resp = s.post('{url}/pdb/cmd/v1', json=deactivate_cmd)
        cmd_obj = resp.json()
        if 'uuid' in cmd_obj:
            print('Submitted deactivate command for node {n} with uuid: {u}'.format(n=event['detail']['instance-id'], u=cmd_obj['uuid']))
            print('Failed to submit deactivate command with error: ' + resp.text)
            return
    else:
        print('Node {n} is already deactivated.'.format(n=event['detail']['instance-id'])
