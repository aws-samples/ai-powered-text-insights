# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import traceback

import demoji

import boto3
import langchain_core
from langchain_aws import ChatBedrock

from output_models.models import ExtractedInformation, TopicMatch
from prompt_selector import get_information_extraction_prompt_selector, get_topic_match_prompt_selector

from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools import Logger

MODEL_ID = os.environ['MODEL_ID']
AWS_REGION = os.environ['AWS_REGION']
LANGUAGE_CODE = os.environ['LANGUAGE_CODE']
META_TOPICS_STR = os.environ['LABELS']
META_SENTIMENTS_STR = os.environ['SENTIMENT_LABELS']

INFORMATION_EXTRACTION_PROMPT_SELECTOR = get_information_extraction_prompt_selector(LANGUAGE_CODE)
TOPIC_MATCH_PROMPT_SELECTOR = get_topic_match_prompt_selector(LANGUAGE_CODE)

TOPIC_MATCH_MODEL_PARAMETERS = {
    "max_tokens": 500,
    "temperature": 0.1,
    "top_k": 20,
}

INFORMATION_EXTRACTION_MODEL_PARAMETERS = {
    "max_tokens": 1500,
    "temperature": 0.1,
    "top_k": 20,
}

bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name=AWS_REGION
)

logger = Logger()

langchain_core.globals.set_debug(True)

def unknown_to_empty_text_values(extracted_info: ExtractedInformation):

    extracted_info.topic = extracted_info.topic.strip()
    extracted_info.location = extracted_info.location.strip()
    extracted_info.sentiment = extracted_info.sentiment.strip()

    extracted_info.topic = extracted_info.topic if extracted_info.topic != "<UNKNOWN>" else ""
    extracted_info.location = extracted_info.location if extracted_info.location != "<UNKNOWN>" else ""
    extracted_info.sentiment = extracted_info.sentiment if extracted_info.sentiment != "<UNKNOWN>" else ""


def text_topic_match(
        meta_topics: str,
        text: str,
) -> TopicMatch:

    bedrock_llm = ChatBedrock(
        model_id=MODEL_ID,
        model_kwargs=TOPIC_MATCH_MODEL_PARAMETERS,
        client=bedrock_runtime,
    )

    claude_topic_match_prompt_template = TOPIC_MATCH_PROMPT_SELECTOR.get_prompt(MODEL_ID)

    print(claude_topic_match_prompt_template.format(meta_topics=meta_topics, text=text))

    structured_llm = bedrock_llm.with_structured_output(TopicMatch)

    structured_topic_match_chain = claude_topic_match_prompt_template | structured_llm

    topic_match_obj = structured_topic_match_chain.invoke({"meta_topics": meta_topics, "text": text})

    print("Topic match object")
    print(type(topic_match_obj))
    print(topic_match_obj)

    return topic_match_obj

def text_information_extraction(
        sentiments: str,
        text: str
) -> ExtractedInformation:

    bedrock_llm = ChatBedrock(
        model_id=MODEL_ID,
        model_kwargs=INFORMATION_EXTRACTION_MODEL_PARAMETERS,
        client=bedrock_runtime,
    )

    claude_information_extraction_prompt_template = INFORMATION_EXTRACTION_PROMPT_SELECTOR.get_prompt(MODEL_ID)

    print("The prompt template")
    print(claude_information_extraction_prompt_template)

    print(claude_information_extraction_prompt_template.format(
        text=text,
        sentiments=sentiments
        )
    )

    structured_llm = bedrock_llm.with_structured_output(ExtractedInformation)

    structured_chain = claude_information_extraction_prompt_template | structured_llm

    information_extraction_obj = structured_chain.invoke({
        "text": text,
        "sentiments": sentiments
    })

    print("Information extraction object")
    print(type(information_extraction_obj))
    print(information_extraction_obj)

    return information_extraction_obj

@logger.inject_lambda_context(log_event=True)
def handler(event, _context: LambdaContext):

        item = event

        logger.info('Item:')
        logger.info(item)

        #Attemp to categorize item
        text = item['text']
        logger.info(f'Text: {text}')

        text = demoji.replace(text, "")
        item['text_clean'] = text

        try:

            #meta_topics_str = ','.join(META_TOPICS)
            topic_match = text_topic_match(META_TOPICS_STR, item['text_clean'])

            if topic_match.is_match == True and len(topic_match.related_topics) > 0:

                try:

                    text_insight = text_information_extraction(META_SENTIMENTS_STR, item['text_clean'])
                    logger.info(f'Text insights:')
                    logger.info(text_insight)

                    if text_insight is not None:
                        item['process_post'] = True
                        logger.info("Removing <UNKNOWN> values")
                        logger.info(text_insight)
                        unknown_to_empty_text_values(text_insight)
                        logger.info("<UNKNOWN> removed")
                        logger.info(text_insight)
                        item.update(text_insight)
                        item["meta_topics"] = topic_match.related_topics

                        # Process location only if there is one
                        if len(item['location']) > 0:
                            item['process_location'] = True
                        else:
                            item['process_location'] = False

                        item['model'] = MODEL_ID

                        logger.info(f'Invoking next function')
                        logger.info(item)
                    else:
                        item['process_post'] = False
                        logger.info(f'Nothing else to do')
                        logger.info(item)

                    return item

                except Exception as e:

                    print(traceback.format_exc())

                    raise Exception("Unable to extract data on text")

            else:
                logger.info(f'Topic not matched')
                return {'process_post': False}

        except Exception as e:

            print(traceback.format_exc())

            raise Exception("Unable to match topics on text")