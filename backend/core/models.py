from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class StoryOptionLLM(BaseModel):
    text: str = Field(description="the text of the option shown to the user")
    nextNode: Dict[str, Any] = Field(
        description="the next node content and its options"
    )


class StoryNodeLLM(BaseModel):
    content: str = Field(description="the main content of the story node")
    isEnding: bool = Field(description="whether this node is an ending node")
    isWinningEnding: bool = Field(
        description="whether this node is a winning ending node"
    )
    options: Optional[List[StoryOptionLLM]] = Field(
        description="the options for this node", default=None
    )


class StoryLLMResponse(BaseModel):
    title: str = Field(description="the title of the story")
    rootNode: StoryNodeLLM = Field(description="the root node of the story")
