import click
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from pydantic import BaseModel, Field
from src.config import Config

# Used for structured output
class Evaluation(BaseModel):
    is_correct: bool = Field(description="Whether the response is correct")

class Quiz:
    def __init__(self):
        self.model = self.get_model()
        self.messages: list[BaseMessage] = [
            SystemMessage("You are a helpful chatbot that responds with only what the user asks for.")
        ]

    def get_model(self) -> BaseChatModel:
        config: Config = Config()
        match config.api:
            case "OPENAI":
                return ChatOpenAI(model=config.model, api_key=config.api_key)
            case "ANTHROPIC":
                return ChatAnthropic(model=config.model, api_key=config.api_key)
            case _:
                raise click.ClickException("API not supported")
    
    def invoke(self, content: str) -> bool:
        question = self.get_question(content)
        click.secho(question, fg='cyan')
        response = click.prompt("Response")
        is_correct = self.check_answer(question, content, response)
        if not is_correct:
            self.explain(question, content, response)
        else:
            click.secho("Correct!", fg='green', bold=True)
        return is_correct
    
    def get_question(self, content: str) -> str:
        return self.model.invoke([
            SystemMessage(
                "You are a helpful chatbot that responds with only what the user asks for."
            ),
            HumanMessage(
                f"Respond with a question that tests whether the user knows the following information: {content}"
            )
        ]).content

    def check_answer(self, question: str, content: str, response: str) -> bool:
        
        return self.model.with_structured_output(Evaluation).invoke([
            HumanMessage(f"Evaluate the response to the following question designed to test a users knowledge...\n\nKNOWLEDGE TO TEST: {content}\n\nQUESTION: {question}\n\nRESPONSE: {response}")
        ]).is_correct
    
    def explain(self, question: str, content: str, response: str):
        explanation = self.model.invoke([
            SystemMessage("You are a helpful chatbot that responds with only what the user asks for. Do not preface your response in any way."),
            HumanMessage(f"The following response to a question designed to test a user's knowledge was incorrect. Provide a helpful response to send to the user reminding them of the correct information...\n\nKNOWLEDGE TO TEST: {content}\n\nQUESTION: {question}\n\nRESPONSE: {response}")
        ]).content
        click.secho(explanation, fg='red', bold=True)