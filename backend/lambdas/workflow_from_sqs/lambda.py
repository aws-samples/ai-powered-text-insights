# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import logging
import os

from aws_lambda_powertools.utilities.batch import BatchProcessor, EventType, batch_processor
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord

processor = BatchProcessor(event_type=EventType.SQS)

logging.getLogger().setLevel(os.environ.get('LOG_LEVEL', 'WARNING').upper())

def record_handler(record: SQSRecord):

    message_body = record.body

    if message_body:
        logging.info('SQS message body:')
        logging.info(message_body)
        #item = json.loads(message_body, strict=False)

        logging.info('Starting step function processing:')

        client = boto3.client('stepfunctions')
        response = client.start_execution(
            stateMachineArn=os.environ['PROCESS_POST_STATE_MACHINE'],
            input=message_body
        )

        logging.info('Step function response:')
        logging.info(response)

        return response


@batch_processor(record_handler=record_handler, processor=processor)
def handler(event, context):
    return processor.response()



