#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interact with abuseipdb https://www/.abuseipdb.com/
 - list of abusing IPs to deny in nginx or check abuse status of a specific IP
"""
import os
import shutil
import sys
import json
import argparse
import functools
import logging

import envfiles
import requests

KEY_FILE = '.apikey'
APIKEY = 'APIKEY'


@functools.lru_cache(16)
def get_apikey(directory: str = None):
    if not directory:
        apikey = get_apikey('.')
        if apikey:
            return apikey
        # fallback
        directory = os.path.dirname(__file__)
    try:
        env = envfiles.load(os.getenv('APIKEY', default=os.path.join(directory, KEY_FILE)))
        return env.get(APIKEY, None)
    except envfiles.EnvFilesError:
        pass
    return None


ABUSE_API_DB = {
    'check': 'https://api.abuseipdb.com/api/v2/check',  # GET
    'blacklist': 'https://api.abuseipdb.com/api/v2/blacklist',  # GET
    'report': 'https://api.abuseipdb.com/api/v2/report'
}


def check_ip(address, days = None, verbose=False):
    endpoint = ABUSE_API_DB['check']
    headers = {'Accept': 'application/json', 'Key': get_apikey()}
    params = {'ipAddress': str(address)}
    if days and str(days).isdigit():
        params['maxAgeInDays'] = str(days)
    if verbose:
        params['verbose'] = 'true'
    logging.debug(f'check_ip({address})')
    logging.debug(f'params={params}')
    response = requests.get(endpoint, headers=headers, params=params)
    logging.debug(f'Response Headers: {response.headers}')
    if response.status_code == 200:
        logging.debug(f'Status code: {response.status_code}')
        data = response.json()["data"]
        logging.debug(f'Response: {data}')
        return data
    logging.warning(f'Status code: {response.status_code}')
    logging.debug(f'Response: {response.text}')
    return None


def check_ips(addresses, days=None, verbose=False):
    return [check_ip(address, days=days, verbose=verbose) for address in addresses]


def check_addresses(outfile, argv: argparse.Namespace):
    results = check_ips(argv.ips, days=argv.days, verbose=argv.verbose)

    def format_result(r) -> str:
        return json.dumps(r, indent=4)

    if len(results) == 1:
        print(format_result(results[0]), file=outfile)
    else:
        formatted = [format_result(out) for out in results]
        print('[' + ','.join(formatted) + ']\n', file=outfile)


def get_blacklist(confidenceMinimum: int = 90, plaintext: bool = False):
    endpoint = ABUSE_API_DB['blacklist']
    headers = {'Accept': 'application/json', 'Key': get_apikey()}
    params = {'confidenceMinimum': str(confidenceMinimum)}
    if plaintext:
        params['plaintext'] = 1
    logging.debug(f'get_blacklist({params})')
    response = requests.get(endpoint, headers=headers, params=params)
    logging.debug(f'Response Headers: {response.headers}')
    if response.status_code == 200:
        logging.debug(f'Status code: {response.status_code}')
        return response.text if plaintext else response.json()["data"]
    logging.warning(f'Status code: {response.status_code}')
    logging.debug(f'Response: {response.text}')
    return None


def nginx_blacklist(outfile, argv: argparse.Namespace):
    blacklist = get_blacklist(confidenceMinimum=100, plaintext=True)
    for entry in blacklist.split("\n"):
        if entry:
            print(f'deny {entry};', file=outfile)


if __name__ == '__main__':

    loglevels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

    prog = os.path.basename(sys.argv[0])
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', '-o', help='Output to file (default=console)')
    parser.add_argument('--log', '-l', choices=loglevels, default='INFO', help='set log verbosity')

    subparsers = parser.add_subparsers(help='command help')

    nginx = subparsers.add_parser('nginx', help='nginx help')
    nginx.add_argument('--min', '-m', type=int, default=100, help='set confidenceMinimum level (default=100)')
    nginx.set_defaults(func=nginx_blacklist)

    check = subparsers.add_parser('check', help='check help')
    check.add_argument('--days', '-d', default=30, help='set maxAgeInDays')
    check.add_argument('--verbose', '-v', action='store_true', default=False, help='request verbose info')
    check.add_argument('ips', nargs='+', help='specify one or more IPs to check (ipv4 or ipv6)')
    check.set_defaults(func=check_addresses)

    args = parser.parse_args()

    # preserve/backup existing output file if one was specified
    if args.output:
        shutil.copy2(args.output, args.output + ".prev")
        outfile = open(args.output, 'w')
    else:
        outfile = sys.stdout

    logging.basicConfig(level=getattr(logging, args.log), format='%(asctime)s %(levelname)s %(message)s')

    args.func(outfile, args)
