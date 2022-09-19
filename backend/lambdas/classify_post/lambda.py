# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import logging
import os

from botocore.config import Config

import boto3
import demoji

from text_preprocessing import TweetPreprocessor

sagemaker = boto3.client('runtime.sagemaker',
                         config=Config(connect_timeout=5, read_timeout=60, retries={'max_attempts': 20}))

logging.getLogger().setLevel(os.environ.get('LOG_LEVEL', 'WARNING').upper())


def categorize_tweet(tweet):
    endpoint_name = os.environ['ENDPOINT_NAME']
    labels = os.environ['LABELS'].split(',')
    logging.info(f'Invoking endpoint {endpoint_name} with the following labels: {labels}')
    data = {
        'inputs': tweet,
        'parameters': {
            'candidate_labels': labels,
            'multi_label': False
        }
    }
    response = sagemaker.invoke_endpoint(EndpointName=endpoint_name,
                                         ContentType='application/json',
                                         Body=json.dumps(data))
    logging.info(response)

    response_body = json.loads(response['Body'].read())
    score = max(response_body['scores'])
    if score > float(os.environ['MIN_CLASS_SCORE']):
        label_index = response_body['scores'].index(score)
        label = response_body['labels'][label_index]
    else:
        label = os.environ['DEFAULT_LABEL']
        score = 0
    score_by_labels = dict(zip(response_body['labels'], response_body['scores']))
    score_by_labels_str = json.dumps(score_by_labels, ensure_ascii=False)
    logging.info(f'Category: {label}\nScore: {score}\nScores: {score_by_labels_str}')
    return label, score, score_by_labels_str


def handler(event, context):

        item = event

        logging.info('Item:')
        logging.info(item)

        #Attemp to categorize item
        text = item['text']
        logging.info(f'Tweet: {text}')

        text = demoji.replace(text, "")
        item['text_clean'] = TweetPreprocessor().preprocess(text)

        item['category_type'], item['category_type_score'], item['category_type_model_result'] = \
            categorize_tweet(item['text_clean'])
        item['model'] = os.environ['ENDPOINT_NAME']

        if item['category_type'] != os.environ['DEFAULT_LABEL']:

            item['process_post'] = True
            logging.info(f'Invoking next function')
            logging.info(item)
        else:

            item['process_post'] = False
            logging.info(f'Nothing else to do')
            logging.info(item)

        return item
