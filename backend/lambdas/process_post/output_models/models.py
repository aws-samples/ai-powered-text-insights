# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Optional, Literal

class ExtractedInformation(BaseModel):
    """Contains information extracted from the text"""
    topic: str = Field([], description="The main topic of the text")
    location: str = Field("", description="The location where the events occur, empty if no location can be inferred")
    entities: List[str] = Field([], description="The entities involved in the text")
    keyphrases: List[str] = Field([], description="The keyphrases in the short text")
    sentiment: str = Field("neutral", description="The overall sentiment of the text")
    links: List[str] = Field([], description="Any links found withing the text")

class TopicMatch(BaseModel):
    """Information regarding the match of a topic to a set of predefined topics"""
    understanding: str = Field(description="In your own words the topics to which this text is related")
    related_topics: List[str] = Field(description="The list of topics into which the input text can be classified")
    is_match: bool = Field(description="true if the text matches one of your topics of interest, false otherwise")


class TextWithInsights(ExtractedInformation):
    """A text with its extracted insights"""
    text: str = Field(description="The original text as written by the user")
    user: str = Field(description="The user that wrote the text")
    created_at: str = Field(description="The datetime when te text was created")
    source: str = Field(description="The source platform from where this text was generated")
    platform: str = Field(description="The platform from where this text was generated")
    text_clean: str = Field(description="The original text after being pre-processed")
    process_post: bool = Field(description="Whether the text should be further processed or not")
    meta_topics: List[str] = Field([], description="A list of topics in which the text can be classified"),
    process_location: bool = Field(False, description="Whether the text has a location that should be further processed"),
    model_id: str = Field(description="The model id that was used to extract these insights")
