# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import os
import logging

logging.getLogger().setLevel(os.environ.get('LOG_LEVEL', 'WARNING').upper())
location_service = boto3.client('location')

def handler(event, context):

    item = event

    logging.info('Item is located in ' + item['location'])
    res_locations = location_service.search_place_index_for_text(FilterCountries=[os.environ['GEO_REGION']],
                                                                 IndexName=os.environ['PLACE_INDEX_NAME'],
                                                                 Language=os.environ['LANGUAGE'],
                                                                 MaxResults=1,
                                                                 Text=item['location']
                                                                 )
    logging.info(res_locations)

    if len(res_locations['Results']) >= 1:
        print(res_locations['Results'][0])
        item['longitude'] = res_locations['Results'][0]['Place']['Geometry']['Point'][0]
        item['latitude'] = res_locations['Results'][0]['Place']['Geometry']['Point'][1]

    return item

