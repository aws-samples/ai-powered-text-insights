# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import os
import logging
import datetime
import uuid
import io
import json
import jsonlines

logging.getLogger().setLevel(os.environ.get('LOG_LEVEL', 'WARNING').upper())
s3 = boto3.client('s3')


def create_key_phrases_records(item, key_phrases):
    items = io.StringIO()
    phrases_item = {}

    phrases_item['created_at'] = item['created_at']
    phrases_item['timestamp'] = item['timestamp']
    phrases_item['user'] = item['user']
    phrases_item['platform'] = item['platform']
    phrases_item['text_clean'] = item['text_clean']
    phrases_item['count'] = 1

    # Write as JSON lines so that Athena can read them
    with jsonlines.Writer(items) as writer:
        for phrase in key_phrases:
            phrases_item['phrase'] = phrase
            writer.write(phrases_item)

    return items.getvalue()


def handler(event, context):

    item = event

    utc_now = datetime.datetime.now(datetime.timezone.utc)
    item['timestamp'] = utc_now.strftime('%Y-%m-%d %H:%M:%S.%f')

    # Add count for anomaly detection
    item['count'] = 1

    created_at = datetime.datetime.strptime(item['created_at'], '%Y-%m-%dT%H:%M:%S.%fz')
    item['created_at'] = created_at.strftime('%Y-%m-%d %H:%M:%S.%f')

    #Save key phrases
    key_phrases = item['phrases']
    key_phrases_json_lines = create_key_phrases_records(item, key_phrases)

    # Create partition key for S3
    partition_timestamp = datetime.datetime(created_at.year, created_at.month, created_at.day, 0, 0, 0)
    key = f"{partition_timestamp.strftime('%Y-%m-%d %H:%M:%S')}/{str(uuid.uuid1())}.json"

    logging.info('Key phrases')
    logging.info(key_phrases_json_lines)

    # Save item
    if item['process_location']:
        post = {'text': item['text'], 'user': item['user'], 'created_at': item['created_at'], 'source': item['source'],
                'platform': item['platform'], 'text_clean': item['text_clean'], 'category_type': item['category_type'],
                'category_type_score': item['category_type_score'],
                'category_type_model_result': item['category_type_model_result'], 'model': item['model'],
                'sentiment': item['sentiment'], 'location': item['location'], 'longitude': item['longitude'],
                'latitude': item['latitude'], 'timestamp': item['timestamp'], 'count': item['count']}
    else:
        post = {'text': item['text'], 'user': item['user'], 'created_at': item['created_at'], 'source': item['source'],
                'platform': item['platform'], 'text_clean': item['text_clean'], 'category_type': item['category_type'],
                'category_type_score': item['category_type_score'],
                'category_type_model_result': item['category_type_model_result'], 'model': item['model'],
                'sentiment': item['sentiment'], 'timestamp': item['timestamp'], 'count': item['count']}

    s3.put_object(
        Body=json.dumps(post, ensure_ascii=False),
        Bucket=os.environ['TWEETS_BUCKET'],
        Key='tweets/' + key
    )

    if key_phrases_json_lines:
        # Save key phrases
        s3.put_object(
            Body=key_phrases_json_lines,
            Bucket=os.environ['TWEETS_BUCKET'],
            Key='phrases/' + key
        )

    return {'success': True}
