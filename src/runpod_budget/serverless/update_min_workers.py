#!/usr/bin/env python3
import argparse
import json
from runpod_budget import runpod


def get_args():
    parser = argparse.ArgumentParser(
        description='Update Min Workers for a Serverless Endpoint',
    )

    parser.add_argument(
        '--endpoint_id', '-endpoint_id', '--endpoint', '-endpoint', '--e', '-e',
        type=str,
        required=True,
        help='endpoint id (eg. dg31b9aqtupn2z)'
    )

    parser.add_argument(
        '--min_workers', '-min_workers', '--min', '-min', '--m', '-m',
        type=int,
        required=True,
        help='min workers (eg. 1)'
    )

    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    runpod = runpod.Serverless()
    response = runpod.update_min_workers(args.endpoint_id, args.min_workers)

    if response.status_code == 200:
        resp_json = response.json()

        if 'errors' in resp_json:
            print('ERROR:')
            for error in resp_json['errors']:
                print(error['message'])
        else:
            endpoint = resp_json['data']['updateEndpointWorkersMin']
            print('Min workers updated successfully.')
            print(f"endpoint id: {endpoint['id']}")
            print(f"template id: {endpoint['templateId']}")
            print(f"min workers: {endpoint['workersMin']}")
            print(f"max workers: {endpoint['workersMax']}")
    elif response.status_code == 401:
        print('ERROR: Unauthorized (401) - Check your API token')
    else:
        print('ERROR: ', end='')
        print(f'HTTP Status code: {response.status_code}')
