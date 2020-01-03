# pylint: disable=import-error,unused-variable
import os
import sys
import traceback

from cryptography.fernet import Fernet, InvalidToken
from aws_lambda_powertools.logging import logger_setup, logger_inject_lambda_context
from policy import AuthPolicy, HttpVerb

logger = logger_setup(boto_level='CRITICAL') 

try:
  SECRET_KEY = os.environ['SECRET_KEY']
except KeyError as e:
  raise Exception('Missing required environment variables!')

class Authorizer(object):

    def __init__(self, event):
        self.event = event
        self.params = self.__get_parameters()
        self.cipher_suite = Fernet(SECRET_KEY)

    def __get_parameters(self):
        """
        Get merged dict() using `pathParameters` and (optional) `queryStringParameters`
        """
        if not hasattr(self, 'params'):
            params = self.event.get('pathParameters', {})

            if not params:
                params = {}

            queryStringParameters = self.event.get('queryStringParameters', {})

            if queryStringParameters:    
                params = {**queryStringParameters, **params}

            self.params = params
        
        return self.params

    def validate(self):

        tmp = self.event['methodArn'].split(':')
        api_gateway_arn = tmp[5].split('/')
        account_id = tmp[4]

        token = self.params['token']
        try:
            # Check if valid token
            decoded_token = self.cipher_suite.decrypt(str(token).encode())

            authpolicy = AuthPolicy(token, account_id)
            authpolicy.rest_api_id = api_gateway_arn[0]
            authpolicy.region = tmp[3]
            authpolicy.stage = api_gateway_arn[1]

            logger.info(decoded_token)

            if decoded_token.decode() == self.params['hostname']:
                authpolicy.allow_all_methods()
            else:
                authpolicy.deny_all_methods()

        except InvalidToken:
            authpolicy.deny_all_methods()

        policy = authpolicy.build()

        logger.info(policy)

        return policy

def lambda_handler(event, context):
    try:
        logger.info(event)

        clazz = Authorizer(event)
        return clazz.validate()
        
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        raise Exception("Unauthorized")