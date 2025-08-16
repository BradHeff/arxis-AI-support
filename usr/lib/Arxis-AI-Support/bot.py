import logging
from support import SupportBot
from fsm_llm.state_models import FSMRun


class BotRunner:
    """Small wrapper around SupportBot to provide a clean async interface for the GUI.

    Responsibilities:
    - Hold the SupportBot instance
    - Provide an async `process` method returning the FSMRun
    - Expose simple helpers for state and completion checks
    """

    def __init__(self):
        try:
            self.support_bot = SupportBot()
        except Exception as e:
            logging.error(f"Failed to initialize SupportBot: {e}")
            raise

    async def process(
        self, user_input: str, model: str = "gpt-5-nano-2025-08-07"
    ) -> FSMRun:
        """Run the FSM for a user input and return the FSMRun result."""
        return await self.support_bot.fsm.run_state_machine(
            self.support_bot.ai_client, user_input=user_input, model=model
        )

    def is_completed(self) -> bool:
        return self.support_bot.fsm.is_completed()

    def get_state(self) -> str:
        try:
            return self.support_bot.fsm.get_curr_state()
        except Exception:
            return "UNKNOWN"
