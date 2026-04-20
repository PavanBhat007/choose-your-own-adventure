from sqlalchemy.orm import Session
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from core.prompts import STORY_PROMPT
from core.models import StoryLLMResponse, StoryNodeLLM
from models.story import Story, StoryNode

load_dotenv()


class StoryGenerator:

    @classmethod
    def _get_llm(cls):
        return ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)

    @classmethod
    def generate_story(
        cls, db: Session, session_id: str, theme: str = "fantasy"
    ) -> Story:
        llm = cls._get_llm()
        story_parser = PydanticOutputParser(pydantic_object=StoryLLMResponse)

        format_instructions = story_parser.get_format_instructions()
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", STORY_PROMPT),
                (
                    "human",
                    """
                        Create the story with this theme: {theme}

                        IMPORTANT:
                        - Return ONLY valid JSON
                        - No markdown
                        - No explanations
                        - Follow this schema strictly:

                        {format_instructions}
                    """,
                ),
            ]
        )

        chain_input = {
            "theme": theme,
            "format_instructions": format_instructions,
        }

        raw_response = llm.invoke(prompt.invoke(chain_input))
        response_text = raw_response
        if hasattr(raw_response, "content"):
            response_text = raw_response.content

        try:
            story_structure = story_parser.parse(response_text)
        except Exception as e:
            raise ValueError(f"LLM output parsing failed:\n{response_text}") from e

        story_db = Story(title=story_structure.title, session_id=session_id)
        db.add(story_db)
        db.flush()

        root_node_data = story_structure.rootNode
        if isinstance(root_node_data, dict):
            root_node_data = StoryNodeLLM.model_validate(root_node_data)

        cls._process_story_node(db, story_db.id, root_node_data, isRoot=True)

        db.commit()
        return story_db

    @classmethod
    def _process_story_node(
        cls, db: Session, story_id: int, node_data: StoryNodeLLM, isRoot: bool = False
    ) -> StoryNode:
        node = StoryNode(
            story_id=story_id,
            content=(
                node_data.content
                if hasattr(node_data, "content")
                else node_data["content"]
            ),
            is_root=isRoot,
            is_ending=(
                node_data.isEnding
                if hasattr(node_data, "isEnding")
                else node_data["isEnding"]
            ),
            is_winning_ending=(
                node_data.isWinningEnding
                if hasattr(node_data, "isWinningEnding")
                else node_data["isWinningEnding"]
            ),
            options=[],
        )

        db.add(node)
        db.flush()

        if not node.is_ending and (hasattr(node_data, "options") and node_data.options):
            options_list = []
            for option_data in node_data.options:
                next_node = option_data.nextNode

                if isinstance(next_node, dict):
                    next_node = StoryNodeLLM.model_validate(next_node)

                child_node = cls._process_story_node(
                    db, story_id, next_node, isRoot=False
                )
                options_list.append(
                    {"text": option_data.text, "node_id": child_node.id}
                )

            node.options = options_list

        db.flush()
        return node
