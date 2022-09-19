# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import os
import operator
import logging

from text_preprocessing import TweetPreprocessor

logging.getLogger().setLevel(os.environ.get('LOG_LEVEL', 'WARNING').upper())
comprehend = boto3.client('comprehend')

def extract_key_phrases(item):
    """Use comprehend to extract key phrases from the text"""

    key_phrases = comprehend.detect_key_phrases(Text=item['text_clean'], LanguageCode=os.environ['LANGUAGE'])[
        'KeyPhrases']

    logging.info("Key phrases")
    logging.info(key_phrases)

    return [phrase['Text'] for phrase in key_phrases if phrase['Score'] > float(os.environ['MIN_KEY_PHRASE_SCORE'])]

def create_composed_locations(locations):
    """Given a set of locations, create addresses from locations that are consecutive in the text.
    We assume that the locations are found in increasing offset numbers by comprehend"""

    logging.info('Locations: ')
    logging.info(locations)

    max_offset = 10
    locations_offset = []
    starting_offset = locations[0]['BeginOffset']
    end_offset = locations[0]['EndOffset']

    locations.pop(0)

    # If the location is consecutive (by max_offset), append it to the composed location
    for location in locations:
        if end_offset < location['BeginOffset'] - max_offset:
            locations_offset.append((starting_offset, end_offset))
            starting_offset = location['BeginOffset']

        end_offset = location['EndOffset']

    locations_offset.append((starting_offset, end_offset))

    return locations_offset


def get_addresses(item):
    """Add the geolocation data to the item if there are locations in the text"""

    locations = []
    addresses = None
    entities = comprehend.detect_entities(Text=item['text_clean'], LanguageCode=os.environ['LANGUAGE'])

    # Extract locations
    for entity in entities['Entities']:
        if entity['Type'] == 'LOCATION' and entity['Score'] >= float(os.environ['MIN_ENTITY_LOCATION_SCORE']):
            locations.append(entity)

    # Create composed locations
    if locations:
        locations_offsets = create_composed_locations(locations)
        addresses = {item['text_clean'][offsets[0]:offsets[1]]: offsets[1] - offsets[0] for offsets in
                     locations_offsets}

    return addresses


def handler(event, context):

    item = event

    logging.info('Applying comprehend to item: ')
    logging.info(item)

    key_phrases = {}

    # Add sentiment to the item
    item['sentiment'] = comprehend.detect_sentiment(Text=item['text_clean'], LanguageCode=os.environ['LANGUAGE'])[
        'Sentiment']

    # Get location data
    addresses = get_addresses(item)

    if addresses is not None:
        item['location'] = max(addresses.items(), key=operator.itemgetter(1))[0]  # Location is the largest location
        item['process_location'] = True
    else:
        item['process_location'] = False

    # Extract hashtags and key phrases
    key_phrases['hashtags'] = set(TweetPreprocessor.get_hash_tags(item['text_clean']))
    key_phrases['phrases'] = set(extract_key_phrases(item))

    item['phrases'] = list(key_phrases['hashtags'].union(key_phrases['phrases']))

    return item
