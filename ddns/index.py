# pylint: disable=import-error
import os
import json
import re
import ipaddress
import boto3
from aws_lambda_powertools.logging import logger_setup, logger_inject_lambda_context

logger = logger_setup(boto_level='CRITICAL') 

try:
  ROUTE_53_ZONE_ID   = os.environ['ROUTE_53_ZONE_ID']
  ROUTE_53_ZONE_NAME = os.environ['ROUTE_53_ZONE_NAME']
except KeyError as e:
  raise Exception('Missing required environment variables!')

class InvalidRequest(Exception):
    pass

class RequestHandler(object):

    def __init__(self, event, context):

        self.event = event
        self.context = context
        self.params = self.__get_parameters()

        self.route53 = boto3.client('route53')

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

    def __is_valid_fqdn(self, fqdn):
        """
        Check if incoming 'hostname' is valid.
        """
        length = len(fqdn)
        if fqdn.endswith("."):
            length -= 1
        if length > 253:
            return False
        _re = re.compile(r"^((?!-)[-A-Z\d]{1,63}(?<!-)\.)+(?!-)[-A-Z\d]{1,63}(?<!-)\.?$", re.IGNORECASE)
        return bool(_re.match(fqdn))

    def is_valid_request(self):
        """
        Check if incoming request is valid.
        """
        for p in ['hostname','myip']:
            if not p in self.params:
                raise InvalidRequest(f"Missing request parameter '{p}'")

        # validate hostname
        if not self.__is_valid_fqdn(f"{self.params['hostname']}.{ROUTE_53_ZONE_NAME}"):
            # TODO: Return 'service_ddns_status_not_fqdn
            raise InvalidRequest(f"Invalid fqdn specified: {self.params['hostname']}.{ROUTE_53_ZONE_NAME}")

        # validate ip
        try:
            ipaddress.ip_address(self.params['myip'])
        except ValueError as e:
            raise e

        return True

    def update(self):
        """
        Create or Update Route 53 resource record set using incoming parameters. 
        """
        response = self.route53.change_resource_record_sets(
            HostedZoneId = ROUTE_53_ZONE_ID,
            ChangeBatch = {
                'Comment': 'Synology DDNS Service resource record.',
                'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': f"{self.params['hostname']}.{ROUTE_53_ZONE_NAME}",
                        'Type': 'A',
                        'TTL': 3600,
                        'ResourceRecords': [
                            {
                                'Value': self.params['myip']
                            }
                        ]
                    }
                }
            ]
            }
        )

        logger.debug(response)

        return {
            "data":{
                "status": "service_ddns_normal"
            },
            "success":True
        }


@logger_inject_lambda_context
def lambda_handler(event, context):

    logger.debug(event)

    try:
        clazz = RequestHandler(event, context)

        if clazz.is_valid_request():
            response = clazz.update()

            return {
                "statusCode": 200,
                "body": json.dumps(response)
            }
        else:
            logger.warn('Invalid request')

    except Exception as e:
        logger.error(e, exc_info=True)

        return {
            "statusCode": 500,
            "body": json.dumps({
                "data":{
                    "status": "service_ddns_error_unknown",
                    "message": str(e)
                },
                "success": False
            })
        }