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
