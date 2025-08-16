import os
import openai
import logging
from fsm_llm.fsm import LLMStateMachine
from fsm_llm.state_models import DefaultResponse
from pydantic import BaseModel
from dotenv import load_dotenv


logging.basicConfig(level=logging.DEBUG)
load_dotenv()


class UserIdentificationResponse(BaseModel):
    user_name: str


class ConfirmationResponse(BaseModel):
    confirmation: str


class SupportBot:
    def __init__(self):
        try:

            self.ai_client = openai.AsyncOpenAI()

            api_key = os.getenv("OPENAI_API_KEY")
            organization = os.getenv("OPENAI_ORGANIZATION")

            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is not set")

            openai.api_key = api_key
            if organization:
                openai.organization = organization

            self.fsm = LLMStateMachine(initial_state="START", end_state="END")
            self._define_states()

        except Exception as e:
            logging.error(f"Error initializing SupportBot: {e}")
            raise

    def _define_states(self):
        """Define all FSM states by delegating to individual state definition methods."""
        try:
            self._define_start_state()
            self._define_confirm_state()
            self._define_identified_state()
            self._define_end_state()
        except Exception as e:
            logging.error(f"Error defining states: {e}")
            raise

    def _define_start_state(self):
        """Define the START state for user identification."""

        @self.fsm.define_state(
            state_key="START",
            prompt_template=(
                "You are a customer support bot. Your first task is to ask the user for their "
                "name. Please ensure the user provides their name before proceeding."
            ),
            response_model=UserIdentificationResponse,
            transitions={"CONFIRM": "Once the user provides their name"},
        )
        async def start_state(
            fsm: LLMStateMachine,
            response: UserIdentificationResponse,
            will_transition: bool,
        ):
            try:
                logging.debug(f"START state: {response}")
                if will_transition and fsm.get_next_state() == "CONFIRM":
                    fsm.set_context_data(
                        "verified_user",
                        {"user_name": response.user_name},
                    )
                    return (
                        f"Thank you! You provided your name as: {response.user_name}\n"
                        f"Is this correct? (yes/no)"
                    )
                return "Please provide your name to get started."
            except Exception as e:
                logging.error(f"Error in start_state: {e}")
                return "I'm sorry, there was an error processing your request. Please try again."

    def _define_confirm_state(self):
        """Define the CONFIRM state for user confirmation."""

        @self.fsm.define_state(
            state_key="CONFIRM",
            prompt_template="Please confirm the information you provided. Reply with 'yes' or 'no'.",
            response_model=ConfirmationResponse,
            transitions={
                "IDENTIFIED": "If the user confirms the details are correct",
                "START": "If the user indicates the details are incorrect",
            },
        )
        async def confirm_state(
            fsm: LLMStateMachine,
            response: ConfirmationResponse,
            will_transition: bool,
        ):
            try:
                logging.debug(f"CONFIRM state: {response}")
                return self._process_confirmation(response.confirmation, fsm)
            except Exception as e:
                logging.error(f"Error in confirm_state: {e}")
                return "I'm sorry, there was an error processing your confirmation. Please try again."

    def _process_confirmation(self, confirmation: str, fsm: LLMStateMachine) -> str:
        """Process user confirmation and set appropriate next state."""
        confirmation = confirmation.lower().strip()

        positive_indicators = [
            "yes",
            "y",
            "correct",
            "true",
            "confirm",
            "confirmed",
            "right",
            "accurate",
        ]
        negative_indicators = [
            "no",
            "n",
            "incorrect",
            "false",
            "wrong",
            "not correct",
            "not right",
        ]

        if any(indicator in confirmation for indicator in positive_indicators):

            if not any(
                neg_word in confirmation
                for neg_word in ["not", "no", "isn't", "aren't", "don't"]
            ):
                fsm.set_next_state("IDENTIFIED")
                return (
                    "Thank you for confirming your details. How can I help you today?"
                )

        if any(indicator in confirmation for indicator in negative_indicators):
            fsm.set_next_state("START")
            return "Let's try again. Please provide your name."

        return "I didn't understand your response. Please reply with 'yes' if the information is correct, or 'no' if it needs to be changed."

    def _define_identified_state(self):
        """Define the IDENTIFIED state for ongoing conversation."""

        @self.fsm.define_state(
            state_key="IDENTIFIED",
            prompt_template=(
                "Thank you for identifying yourself. Is there anything else you need help with?"
            ),
            response_model=DefaultResponse,
            transitions={"END": "When the user indicates the conversation is over"},
        )
        async def identified_state(
            fsm: LLMStateMachine, response: DefaultResponse, will_transition: bool
        ):
            try:
                logging.debug(f"IDENTIFIED state: {response}")
                if will_transition and fsm.get_next_state() == "END":
                    return "Thank you! Have a great day!"
                return (
                    response.content
                    or "You have been identified successfully. How can I assist you further?"
                )
            except Exception as e:
                logging.error(f"Error in identified_state: {e}")
                return "I'm sorry, there was an error processing your request. Please try again."

    def _define_end_state(self):
        """Define the END state for conversation termination."""

        @self.fsm.define_state(
            state_key="END",
            prompt_template="Thank you! Goodbye.",
            response_model=DefaultResponse,
        )
        async def end_state(
            fsm: LLMStateMachine, response: DefaultResponse, will_transition: bool
        ):
            try:
                logging.debug(f"END state: {response}")
                return "Goodbye! If you need further assistance, feel free to reach out again."
            except Exception as e:
                logging.error(f"Error in end_state: {e}")
                return "Goodbye!"
