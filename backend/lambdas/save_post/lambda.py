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


def create_multi_records(insights, key, dest_key):
    items = io.StringIO()
    item = {}

    item['created_at'] = insights['created_at']
    item['timestamp'] = insights['timestamp']
    item['user'] = insights['user']
    item['platform'] = insights['platform']
    item['text_clean'] = insights['text_clean']
    item['count'] = 1

    if key == 'meta_topics':
        item['sentiment'] = insights['sentiment'].lower().strip()

        if insights['process_location']:
            item['location'] = insights['location']
            item['longitude'] = insights['longitude']
            item['latitude'] = insights['latitude']

    # Write as JSON lines so that Athena can read them
    with jsonlines.Writer(items) as writer:
        for insights_key in insights[key]:
            if key == 'meta_topics':
                item[dest_key] = insights_key.lower().strip()
            else:
                item[dest_key] = insights_key
            writer.write(item)

    return items.getvalue()


def handler(event, context):

    item = event

    utc_now = datetime.datetime.now(datetime.timezone.utc)
    item['timestamp'] = utc_now.strftime('%Y-%m-%d %H:%M:%S.%f')

    # Add count for anomaly detection
    item['count'] = 1

    created_at = datetime.datetime.strptime(item['created_at'], '%Y-%m-%dT%H:%M:%S.%fz')
    item['created_at'] = created_at.strftime('%Y-%m-%d %H:%M:%S.%f')

    logging.info("Item to be saved")
    logging.info(item)

    #Retrive objects 1:N
    phrases_json_lines = create_multi_records(item, key='keyphrases', dest_key='phrase')
    meta_topics_json_lines = create_multi_records(item, key='meta_topics', dest_key='topic')
    links_json_lines = create_multi_records(item, key='links', dest_key='link')

    # Create partition key for S3
    partition_timestamp = datetime.datetime(created_at.year, created_at.month, created_at.day, 0, 0, 0)
    key = f"{partition_timestamp.strftime('%Y-%m-%d %H:%M:%S')}/{str(uuid.uuid1())}.json"

    logging.info('Key phrases')
    logging.info(phrases_json_lines)

    logging.info('Meta topics')
    logging.info(meta_topics_json_lines)

    logging.info('Links')
    logging.info(links_json_lines)

    # Save item
    if item['process_location']:
        post = {'text': item['text'], 'user': item['user'], 'created_at': item['created_at'], 'source': item['source'],
                'platform': item['platform'], 'text_clean': item['text_clean'], 'topic': item['topic'].lower().strip(),
                'model': item['model'], 'sentiment': item['sentiment'].lower().strip(), 'location': item['location'],
                'longitude': item['longitude'], 'latitude': item['latitude'], 'timestamp': item['timestamp'], 'count': item['count']}
    else:
        post = {'text': item['text'], 'user': item['user'], 'created_at': item['created_at'], 'source': item['source'],
                'platform': item['platform'], 'text_clean': item['text_clean'], 'topic': item['topic'].lower().strip(),
                'model': item['model'], 'sentiment': item['sentiment'].lower().strip(), 'timestamp': item['timestamp'],
                'count': item['count']}

    s3.put_object(
        Body=json.dumps(post, ensure_ascii=False),
        Bucket=os.environ['POSTS_BUCKET'],
        Key='posts/' + key
    )

    # Save 1:N objectsº

    if phrases_json_lines:
        # Save key phrases
        s3.put_object(
            Body=phrases_json_lines,
            Bucket=os.environ['POSTS_BUCKET'],
            Key='phrases/' + key
        )

    if meta_topics_json_lines:
        # Save meta topics
        s3.put_object(
            Body=meta_topics_json_lines,
            Bucket=os.environ['POSTS_BUCKET'],
            Key='topics/' + key
        )

    if links_json_lines:
        # Save links
        s3.put_object(
            Body=links_json_lines,
            Bucket=os.environ['POSTS_BUCKET'],
            Key='links/' + key
        )

    return {'success': True}
