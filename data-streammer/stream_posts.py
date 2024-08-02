# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import time
import boto3
import argparse
import pandas as pd
import random
from datetime import datetime

parser = argparse.ArgumentParser(description='Stream sample posts to an Amazon SQS Queue for processing')
parser.add_argument('--queue_url', type=str, help='Amazon SQS Queue URL')
parser.add_argument('--region', type=str, help='The region where the AI Powered Text Insights is deployed')

sample_cities = ['New York', 'Chicago', 'Kentucky', 'Arkansas', 'Miami', 'Los Angeles',
                 'San Francisco', 'New Jersey', 'San Diego', 'Orlando', 'Arlington', 'Washington DC',
                 'Las Vegas', 'Portland', 'Seattle', 'Austin', 'Phoenix']

# Create a function to send a JSON object to an SQS queue
def send_sqs_message(queue_url, message):
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message)
    )
    return response


def send_batch(posts_batch, queue_url):

    for text in posts_batch:

        utc_now_str = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fz")

        # Add a location randomly.
        if random.uniform(0, 1) < 0.1:
            text = text + '. From ' + random.choice(sample_cities)

        message = {
            "text": text,
            "user": "test_user",
            "created_at": utc_now_str,
            "source": "test",
            "platform": "test client"
        }

        print(message)
        response = send_sqs_message(queue_url, message)
        print(response)


if __name__ == '__main__':

    args = parser.parse_args()

    queue_url = args.queue_url
    region = args.region

    sqs = boto3.client('sqs')
    translate = boto3.client(service_name='translate', region_name=region, use_ssl=True)

    new_years_resolutions_df = pd.read_csv('new_years_resolutions_tweets.csv')
    new_years_resolutions_df['text'] = new_years_resolutions_df['text'].map(lambda x: x.encode(encoding='UTF-8', errors='replace').decode())

    resolutions_text = new_years_resolutions_df['text'].values.tolist()

    #Use Amazon translate to translate the text into Spanish
    delta_i = 20
    for i in range(0, len(resolutions_text), delta_i):

        end_i = i + delta_i if i + delta_i < len(resolutions_text) else len(resolutions_text)
        text_batch = resolutions_text[i:end_i]

        print(f'Streaming from {i} to {end_i}')

        send_batch(text_batch, queue_url)

        time.sleep(60)