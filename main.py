import ttkbootstrap as ttk
from support import SupportBot
import asyncio
from Gui import create_widgets
from fsm_llm.state_models import FSMRun
import threading
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)


# Define the main window class
class CustomerSupportBot(ttk.Window):
    def __init__(self):
        super(CustomerSupportBot, self).__init__(
            title="Arxis AI Support Tool", themename="trinity-dark"
        )

        create_widgets(self)

        print(
            "Agent: Hello! I am your customer service assistant. Say something to get started."
        )
        self.support_bot = SupportBot()  # Initialize the SupportBot
        self.openai_client = self.support_bot.ai_client  # Initialize the OpenAI client

        # Start the asyncio event loop in a separate thread
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.start_event_loop, daemon=True).start()

    def start_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def on_submit(self, event=None):
        user_input = self.chat_entry.get()
        self.chat_entry.delete(0, ttk.END)  # Clear the entry field after submission
        self.display_message(f"You: {user_input}", "USER")
        asyncio.run_coroutine_threadsafe(self.process_chat(user_input), self.loop)

    async def process_chat(self, user_input):
        while not self.support_bot.fsm.is_completed():
            logging.debug(f"Current FSM state: {self.support_bot.fsm.current_state}")
            logging.debug(f"User input: {user_input}")

            if user_input.lower() in ["quit", "exit"]:
                self.support_bot.fsm.set_next_state("END")
                break

            run_state: FSMRun = await self.support_bot.fsm.run_state_machine(
                self.openai_client, user_input=user_input
            )
            self.display_message(f"Agent: {run_state.response}", "BOT")

            # Wait for new user input
            user_input = None
            while not user_input:
                await asyncio.sleep(0.1)  # Small delay to allow GUI updates
                user_input = self.chat_entry.get()

        self.display_message("Agent: Conversation ended. Thank you!", "BOT")

    def display_message(self, message, tag):
        self.chat_display.config(state=ttk.NORMAL)
        self.chat_display.insert(ttk.END, message + "\n", tag)
        self.chat_display.config(state=ttk.DISABLED)
        self.chat_display.see(ttk.END)


if __name__ == "__main__":
    app = CustomerSupportBot()
    app.mainloop()
