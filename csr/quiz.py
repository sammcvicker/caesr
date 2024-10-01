import click
from langchain_core.runnables import Runnable
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from typing import Optional
from pydantic import BaseModel, Field
from csr.config import load_config
from csr.styles import styles

SYSTEM_MESSAGE = SystemMessage(
    """You are a helpful chatbot generating questions and evaluating responses for users training with flashcards.

    Because these flashcards use AI to write the questions and evaluate the user's memory, it is important to ask good questions and evaluate each response the user gives solely in the context of that question asked.
    
    Respond with only what the user asks for."""
)

def _get_model() -> BaseChatModel:
    """
    Get a chat model based on the user's configuration.

    Returns:
        BaseChatModel: An instance of a chat model (OpenAI or Anthropic).

    Raises:
        click.ClickException: If the API is not supported or if there's a failure in loading the model.
    """
    config: dict[str, str] = load_config()
    try:
        match config["api_name"]:
            case "OpenAI":
                return ChatOpenAI(model=config["model_name"], api_key=config["api_key"])
            case "Anthropic":
                return ChatAnthropic(
                    model=config["model_name"], api_key=config["api_key"]
                )
            case _:
                raise click.ClickException("API not supported")
    except:
        raise click.ClickException(
            f"Failed to load {config["model_name"]}. Double-check internet connection and API key."
        )

def _prepend_system_message_to(query: str) -> list[BaseMessage]:
    """
    Prepend the system message to the user's query.

    Args:
        query (str): The user's query.

    Returns:
        list[BaseMessage]: A list containing the system message and the user's query as a HumanMessage.
    """
    return [SYSTEM_MESSAGE, HumanMessage(query)]

def _try_invoke(model: BaseChatModel, query: str) -> str:
    """
    Try to invoke the model with the given query.

    Args:
        model (BaseChatModel): The chat model to use.
        query (str): The query to send to the model.

    Returns:
        str: The model's response.

    Raises:
        click.ClickException: If there's a failure in the model response and the user chooses not to retry.
    """
    try:
        messages = _prepend_system_message_to(query)
        return model.invoke(messages).content.strip()
    except:
        if click.confirm("Failure in model response; try again?"):
            return _try_invoke(model, query)
        raise click.ClickException("Failure in model response; aborted")

def _try_invoke_with_structured_output(model_with_structured_output: Runnable, query: str) -> str:
    """
    Try to invoke the model with structured output for the given query.

    Args:
        model_with_structured_output (Runnable): The model with structured output capability.
        query (str): The query to send to the model.

    Returns:
        str: The model's structured response.

    Raises:
        click.ClickException: If there's a failure in the model response and the user chooses not to retry.
    """
    try:
        messages = _prepend_system_message_to(query)
        return model_with_structured_output.invoke(messages)
    except:
        if click.confirm("Failure in model response; try again?"):
            return _try_invoke_with_structured_output(model_with_structured_output, query)
        raise click.ClickException("Failure in model response; aborted")

class Evaluation(BaseModel):
    """
    Represents an evaluation of a user's response.

    Attributes:
        is_correct (bool): Whether the response is correct.
        correction (Optional[str]): If the response is incorrect, provides a correct response.
    """
    is_correct: bool = Field(description="Whether the response is correct")
    correction: Optional[str] = Field(
        description="If the response is incorrect, provide a correct response", 
        default=None
    )

class Quiz:
    """
    Represents a quiz system that uses a language model to generate questions and evaluate responses.
    """

    def __init__(self):
        """
        Initialize the Quiz with a language model.
        """
        self.model = _get_model()

    def does_user_remember(self, deck_name: str, content: str,) -> bool:
        """
        Test whether the user remembers the given content by asking a question and evaluating the response.

        Args:
            deck_name (str): The name of the deck in which the content appears.
            content (str): The content to test the user's knowledge on.

        Returns:
            bool: True if the user's response is correct, False otherwise.
        """
        question = self._get_question(deck_name, content)
        click.secho(question, **styles["neutral"])

        response = click.prompt("Response")
        evaluation = self._evaluate(question, content, response)
        correction = evaluation.correction if evaluation.correction and not evaluation.is_correct else None
        
        if correction:
            click.secho(f"Correction: {evaluation.correction}", **styles["bad"])
        else:
            click.secho("Correct!", **styles["good"])

        return not correction

    def _get_question(self, deck_name: str, content: str) -> str:
        """
        Generate a question to test the user's knowledge of the given content.

        Args:
            deck_name (str): The name of the deck in which the content appears.
            content (str): The content to base the question on.

        Returns:
            str: The generated question.
        """
        query = f"The user is practicing remembering things stored in a file called {deck_name}. Respond with a question that tests whether the user knows the following information: {content}"
        return _try_invoke(self.model, query)

    def _evaluate(self, question: str, content: str, response: str) -> Evaluation:
        """
        Evaluate the user's response to a given question.

        Args:
            question (str): The question asked.
            content (str): The original content being tested.
            response (str): The user's response to the question.

        Returns:
            Evaluation: An Evaluation object containing whether the response is correct and any necessary correction.
        """
        query = f"""Evaluate the response to the following question designed to test a users knowledge...
                         
            KNOWLEDGE TO TEST: {content}
            
            QUESTION: {question}
            
            RESPONSE: {response}"""
        return _try_invoke_with_structured_output(
            self.model.with_structured_output(Evaluation),
            query
        )
