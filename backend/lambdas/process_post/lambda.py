# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import logging
import os
import boto3
import demoji
import re

from langchain.prompts import PromptTemplate
from langchain.llms.bedrock import Bedrock
from langchain_community.chat_models import BedrockChat
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from text_preprocessing import TweetPreprocessor
from llm_prompts_by_lang import prompts_map, examples_map, json_format_str

model_id = os.environ['MODEL_ID']
language_code = os.environ['LANGUAGE_CODE']
meta_topics = os.environ['LABELS'].split(',')
meta_sentiments = os.environ['SENTIMENT_LABELS'].split(',')

meta_sentiments = [sentiment.strip() for sentiment in meta_sentiments if sentiment.strip() != '']
meta_topics = [topic.strip() for topic in meta_topics if topic.strip() != '']

bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"
)

model_id_mapping = {
    'claude': 'anthropic.claude-3-haiku-20240307-v1:0',
}

logging.getLogger().setLevel(os.environ.get('LOG_LEVEL', 'WARNING').upper())

# Given two sets of text, extract the elements that are common to both lists
def extract_common_elements(list1, list2):
    return list(set(list1) & set(list2))

def text_information_extraction(post):

    model_kwargs_mapping_data = {
        "claude": {
            "max_tokens": 300,
            "temperature": 0.1,
            "top_p": 0.9,
            "stop_sequences": ["</json>"]
        },
    }

    examples = "".join(
        f"\n\nPOST:\n\n{re.sub(' +', ' ', example[0])}\n\nJSON:{re.sub(' +', ' ', example[1])}" for example in
        examples_map[model_id][language_code]['info_extraction_examples'])
    logging.info(f'Examples:')
    logging.info(examples)

    if model_id == 'claude':

        llm_data = BedrockChat(
            model_id=model_id_mapping[model_id],
            model_kwargs=model_kwargs_mapping_data[model_id],
            client=bedrock_runtime,
        )

    else:
        raise Exception("Model id not supported")

    #Prompt for extracting data

    messages_data = [
        ("human", prompts_map[model_id][language_code]['info_extraction']),
    ]

    extract_data_prompt = ChatPromptTemplate.from_messages(messages_data)

    chain_extract_data = extract_data_prompt | llm_data | StrOutputParser()

    #Modify JSON format to consider only sentiments specified
    json_format = json.loads(json_format_str['info_extraction'])
    json_format['properties']['sentiment']['accepted_values'] = meta_sentiments
    augmented_json_format_str = json.dumps(json_format)

    logging.info(f'Extract data prompt')
    logging.info(extract_data_prompt.format(json_format=augmented_json_format_str,
                                                       examples=examples,
                                                       post=post))

    #Extract insights from text using LLM
    text_insights_str = chain_extract_data.invoke({"examples": examples, "json_format": augmented_json_format_str, "post": post})

    logging.info("Extracted data")
    logging.info(text_insights_str)

    text_insights = json.loads(text_insights_str)
    logging.info(f'Text insights:')
    logging.info(text_insights)

    # If the JSON object is empty return None
    if len(text_insights_str) == 0:
        return None
    else:
        return text_insights

def extract_topics(post):

    model_kwargs_mapping_topic = {
        "claude": {
            "max_tokens": 300,
            "temperature": 0.1,
            "top_p": 0.9,
            "stop_sequences": []
        },
    }

    if model_id == 'claude':

        llm_topic = BedrockChat(
            model_id=model_id_mapping[model_id],
            model_kwargs=model_kwargs_mapping_topic[model_id],
            client=bedrock_runtime,
        )

    else:
        raise Exception("Model id not supported")

    #Prompt for topic match

    messages_data = [
        ("human", prompts_map[model_id][language_code]['topic_match']),
    ]

    topic_match_prompt = ChatPromptTemplate.from_messages(messages_data)

    chain_topic_match = topic_match_prompt | llm_topic | StrOutputParser()

    #Get meta-category from topic
    meta_topics_str = ','.join(meta_topics)
    topic_match_str = chain_topic_match.invoke({"json_format": json_format_str['topic_match'], "meta_topics": meta_topics_str, "text": post})

    logging.info(f'Topic match prompt')
    logging.info(topic_match_prompt.format(json_format=json_format_str['topic_match'],
                                                       meta_topics=meta_topics_str,
                                                       text=post))

    logging.info("Matched topic")
    logging.info(topic_match_str)

    #Post process answer
    topic_match_str = topic_match_str.replace('\n', ' ').replace('\r', '').strip()
    regex_match = re.search("^<json>(.*)</json>$", topic_match_str)

    if regex_match:
        topic_match_str = regex_match.group(1)

        post_match = json.loads(topic_match_str)

        logging.info(f'Topic match:')
        logging.info(post_match)

        return post_match
    else:
        return {
            "topic_match":False,
            "related_topics": []
        }


def handler(event, context):

        item = event

        logging.info('Item:')
        logging.info(item)

        #Attemp to categorize item
        text = item['text']
        logging.info(f'Text: {text}')

        text = demoji.replace(text, "")
        item['text_clean'] = text

        topic_match = extract_topics(item['text_clean'])

        if topic_match['topic_match'] == True:

            text_insight = text_information_extraction(item['text_clean'])
            logging.info(f'Text insights:')
            logging.info(text_insight)

            if text_insight is not None:
                item['process_post'] = True
                item.update(text_insight)
                item["meta_topics"] = topic_match["related_topics"]

                # Process location only if there is one
                if len(item['location']) > 0:
                    item['process_location'] = True
                else:
                    item['process_location'] = False

                item['model'] = model_id

                logging.info(f'Invoking next function')
                logging.info(item)
            else:
                item['process_post'] = False
                logging.info(f'Nothing else to do')
                logging.info(item)

            return item

        else:
            logging.info(f'Topic not matched')
            return {'process_post': False}
