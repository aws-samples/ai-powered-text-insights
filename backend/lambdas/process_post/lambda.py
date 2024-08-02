# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import copy
import os
import traceback

import demoji

import boto3
import langchain_core
from langchain_aws import ChatBedrock

from output_models.models import ExtractedInformation, TopicMatch, TextWithInsights
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

def remove_unknown_values(extracted_info: ExtractedInformation):

    text_insights = copy.deepcopy(extracted_info)

    topic = extracted_info.topic.strip()
    location = extracted_info.location.strip()
    sentiment = extracted_info.sentiment.strip()

    text_insights.topic = topic if topic != "<UNKNOWN>" else ""
    text_insights.location = location if location != "<UNKNOWN>" else ""
    text_insights.sentiment = sentiment if sentiment != "<UNKNOWN>" else ""

    return text_insights

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

    structured_llm = bedrock_llm.with_structured_output(TopicMatch)

    structured_topic_match_chain = claude_topic_match_prompt_template | structured_llm

    topic_match_obj = structured_topic_match_chain.invoke({"meta_topics": meta_topics, "text": text})

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

    structured_llm = bedrock_llm.with_structured_output(ExtractedInformation)

    structured_chain = claude_information_extraction_prompt_template | structured_llm

    information_extraction_obj = structured_chain.invoke({
        "text": text,
        "sentiments": sentiments
    })

    return information_extraction_obj

@logger.inject_lambda_context(log_event=True)
def handler(event, _context: LambdaContext):

        item = event
        text = item['text']

        clean_text = demoji.replace(text, "")

        # Attemp to extract information from text
        try:

            topic_match = text_topic_match(META_TOPICS_STR, clean_text)

            if topic_match.is_match and len(topic_match.related_topics) > 0:

                try:

                    insights = text_information_extraction(META_SENTIMENTS_STR, clean_text)
                    logger.info(f'Text insights:')
                    logger.info(insights)

                    if insights is not None:

                        logger.info("Removing <UNKNOWN> values")
                        logger.debug(insights)

                        insights = remove_unknown_values(insights)

                        logger.info("<UNKNOWN> removed")
                        logger.debug(insights)

                        # Create output object
                        text_insights = TextWithInsights(
                            text=item["text"],
                            user=item["user"],
                            created_at=item["created_at"],
                            source=item["source"],
                            platform=item["platform"],
                            text_clean=clean_text,
                            meta_topics=topic_match.related_topics,
                            topic=insights.topic,
                            location=insights.location,
                            entities=insights.entities,
                            keyphrases=insights.keyphrases,
                            sentiment=insights.sentiment,
                            links=insights.links,
                            model_id=MODEL_ID,
                            process_post=True,
                            process_location=True if len(insights.location) > 0 else False # Process location only if there is one
                        )

                        logger.info(f'Invoking next function')
                        logger.debug(item)
                    else:

                        # Create output object
                        text_insights = TextWithInsights(
                            text=item["text"],
                            user=item["user"],
                            created_at=item["created_at"],
                            source=item["source"],
                            platform=item["platform"],
                            text_clean=clean_text,
                            model_id=MODEL_ID,
                            process_post=False
                        )

                        logger.info(f'Could not extract information from this text')
                        logger.debug(item)

                    return text_insights.dict()

                except Exception as e:

                    logger.error("Unable to extract data from text")
                    logger.error(traceback.format_exc())

                    raise Exception("Unable to extract data from text")

            else:
                logger.info(f'Topic not matched')
                return {'process_post': False}

        except Exception as e:

            logger.error(traceback.format_exc())

            raise Exception("Unable to match topics on text")