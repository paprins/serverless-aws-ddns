#!/usr/bin/env python
import os
import sys
import yaml
import logging

from cryptography.fernet import Fernet

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ddns')

def get_secret_key(args):
  try:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config = yaml.load(open(os.path.join(dir_path, f"config.{args.env}.yml")), Loader=yaml.BaseLoader)

    return config['secret_key']

  except KeyError:
    raise Exception(f'Missing key secret_key in config.{args.env}.yml')
  except Exception:
    raise Exception(f"Unable to load config.{args.env}.yml")

def main(args):
    secret = get_secret_key(args)
    cipher_suite = Fernet(secret)
    token = cipher_suite.encrypt(str(args.hostname).encode())

    logger.info(f"Here's your token for hostname '{args.hostname}': \n\n{token.decode()}")

if __name__ == "__main__":
  import json
  import argparse

  parser = argparse.ArgumentParser(
      description="This utility will generate a token for given context.\n\nPlease note that the 'SECRET_KEY' is parsed from 'config.ENV.yml' (path: secret_key).",
      formatter_class=argparse.RawTextHelpFormatter
    )

  parser.add_argument("--env", type=str, dest="env", required=True, help="Environment", choices=['dev','test','uat','prd'])

  parser.add_argument("--hostname", type=str, dest="hostname", required=True, help="Hostname for which a token should be generated")

  args = parser.parse_args()

  sys.exit(main(args))