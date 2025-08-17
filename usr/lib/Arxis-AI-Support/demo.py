#!/usr/bin/env python3
"""Demo version of the customer support bot that simulates AI responses without needing OpenAI API"""

import ttkbootstrap as ttk
from Gui import create_widgets
import asyncio
import threading
import logging
import random
from Functions import format_response_text, split_text_for_streaming


logging.basicConfig(level=logging.DEBUG)


class MockSupportBot:
    """Mock version that simulates the real SupportBot without API calls"""

    class MockFSM:
        def __init__(self):
            self.current_state = "START"
            self.completed = False

        def is_completed(self):
            return self.completed

        def set_next_state(self, state):
            self.current_state = state
            if state == "END":
                self.completed = True

        async def run_state_machine(
            self, client, user_input, model="gpt-5-nano-2025-08-07"
        ):

            await asyncio.sleep(random.uniform(1, 3))

            class MockRun:
                def __init__(self, response):
                    self.response = response

            if self.current_state == "START":
                if "name" in user_input.lower() or any(
                    word
                    for word in user_input.split()
                    if len(word) > 2 and word.isalpha()
                ):
                    self.set_next_state("CONFIRM")
                    return MockRun(
                        "Thank you! You provided your name. Is this correct? (yes/no)"
                    )
                else:
                    return MockRun("Please provide your name to get started.")

            elif self.current_state == "CONFIRM":
                user_input_lower = user_input.lower().strip()

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

                if any(
                    indicator in user_input_lower for indicator in positive_indicators
                ):

                    if not any(
                        neg_word in user_input_lower
                        for neg_word in ["not", "no", "isn't", "aren't", "don't"]
                    ):
                        self.set_next_state("IDENTIFIED")
                        return MockRun(
                            "Thank you for confirming your details. How can I help you today?"
                        )

                if any(
                    indicator in user_input_lower for indicator in negative_indicators
                ):
                    self.set_next_state("START")
                    return MockRun("Let's try again. Please provide your name.")

                return MockRun(
                    "I didn't understand your response. Please reply with 'yes' if the information is correct, or 'no' if it needs to be changed."
                )

            elif self.current_state == "IDENTIFIED":
                if any(
                    word in user_input.lower()
                    for word in ["bye", "goodbye", "done", "finished", "quit", "exit"]
                ):
                    self.set_next_state("END")
                    return MockRun("Thank you for contacting us! Have a great day!")
                else:
                    return MockRun(
                        "I understand your concern. Is there anything else I can help you with today?"
                    )

            else:
                return MockRun("Goodbye!")

    def __init__(self):
        self.fsm = self.MockFSM()
        self.ai_client = None


class CustomerSupportBotDemo(ttk.Window):

    chat_entry: ttk.Entry
    chat_display: ttk.Text
    statusLabel: ttk.Label
    progress_bar: ttk.Progressbar
    button: ttk.Button

    loop: asyncio.AbstractEventLoop
    fsm: MockSupportBot
    conversation_log: list

    def __init__(self):
        super().__init__()
        try:

            create_widgets(self)

            self.protocol("WM_DELETE_WINDOW", self.on_closing)

            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

            self.fsm = MockSupportBot()
            self.conversation_log = []

            self.after(100, self.show_welcome_message)

        except Exception as e:
            logging.error(f"Error initializing CustomerSupportBotDemo: {e}")
            self.destroy()

    def on_closing(self):
        """Handle window closing"""
        try:
            if hasattr(self, "loop"):
                self.loop.close()
        except Exception:
            pass
        self.destroy()

    def show_welcome_message(self):
        """Show welcome message after GUI is fully initialized"""
        welcome_msg = "Hello! Welcome to Arxis AI Support (Demo Mode). I'm here to help you. May I please have your name?"

        threading.Thread(
            target=self.run_async_in_thread,
            args=(self.simulate_streaming_response(welcome_msg),),
            daemon=True,
        ).start()

    def run_async_in_thread(self, coro):
        """Run an async coroutine in a thread"""
        try:
            asyncio.run(coro)
        except Exception as e:
            logging.error(f"Error in async thread: {e}")

    def start_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def update_status(self, status_text, show_progress=False):
        """Update the status label and optionally show progress indicator"""
        try:
            if hasattr(self, "statusLabel"):
                self.statusLabel.config(text=status_text)

            if hasattr(self, "progress_bar"):
                if show_progress:

                    self.progress_bar.pack(
                        side=ttk.BOTTOM,
                        fill=ttk.X,
                        padx=10,
                        pady=2,
                        before=self.statusLabel,
                    )
                    self.progress_bar.start(10)
                else:
                    self.progress_bar.stop()
                    self.progress_bar.pack_forget()

            self.update_idletasks()
        except Exception as e:
            logging.error(f"Error updating status: {e}")

    def on_submit(self, event=None):
        user_input = self.chat_entry.get().strip()

        if not user_input:
            return

        self.chat_entry.delete(0, ttk.END)
        self.display_user_message(user_input)

        self.chat_entry.config(state="disabled")

        future = asyncio.run_coroutine_threadsafe(
            self.process_chat(user_input), self.loop
        )

        def enable_input():
            try:
                future.result(timeout=0.1)
                self.chat_entry.config(state="normal")
                self.chat_entry.focus()
            except Exception:

                self.after(100, enable_input)

        self.after(100, enable_input)

    async def process_chat(self, user_input):
        try:
            self.update_status("AI is thinking...", show_progress=True)

            logging.debug(f"Current FSM state: {self.fsm.fsm.current_state}")
            logging.debug(f"User input: {user_input}")

            if user_input.lower() in ["quit", "exit"]:
                self.fsm.fsm.set_next_state("END")
                self.update_status("Conversation ended", show_progress=False)
                self.display_message("Agent: Conversation ended. Thank you!", "BOT")
                return

            run_state = await self.fsm.fsm.run_state_machine(
                None, user_input=user_input, model="gpt-5-nano-2025-08-07"
            )

            await self.simulate_streaming_response(run_state.response)

            if self.fsm.fsm.is_completed():
                self.update_status("Conversation completed", show_progress=False)
                await self.simulate_streaming_response("Conversation ended. Thank you!")
            else:
                self.update_status("Waiting for your response...", show_progress=False)

        except Exception as e:
            logging.error(f"Error in process_chat: {e}")
            self.update_status("Error occurred", show_progress=False)
            await self.simulate_streaming_response(
                f"Sorry, I encountered an error: {str(e)}"
            )

    def display_message(self, message, tag):
        """Display message in chat with proper error handling"""
        try:
            self.chat_display.config(state=ttk.NORMAL)
            self.chat_display.insert(ttk.END, message + "\n", tag)
            self.chat_display.config(state=ttk.DISABLED)
            self.chat_display.see(ttk.END)
        except Exception as e:
            logging.error(f"Error displaying message: {e}")

    def display_user_message(self, user_input):
        """Display user message with proper styling - only 'You:' is green"""
        try:
            self.chat_display.config(state=ttk.NORMAL)

            self.chat_display.insert(ttk.END, "You: ", "USER_NAME")

            self.chat_display.insert(ttk.END, user_input + "\n", "USER_MESSAGE")
            self.chat_display.config(state=ttk.DISABLED)
            self.chat_display.see(ttk.END)
        except Exception as e:
            logging.error(f"Error displaying user message: {e}")

    def start_agent_message(self):
        """Start a new agent message and return the starting position"""
        try:
            self.chat_display.config(state=ttk.NORMAL)

            start_pos = self.chat_display.index(ttk.END)
            self.chat_display.insert(ttk.END, "Agent: ", "BOT")
            return start_pos
        except Exception as e:
            logging.error(f"Error starting agent message: {e}")
            return None

    def stream_agent_text(self, text, is_final=False):
        """Stream text as the agent response, word by word"""
        try:
            self.chat_display.config(state=ttk.NORMAL)

            self.chat_display.insert(ttk.END, text, "BOT_STREAMING")

            if is_final:
                self.chat_display.insert(ttk.END, "\n")

            self.chat_display.config(state=ttk.DISABLED)
            self.chat_display.see(ttk.END)
            self.update_idletasks()
        except Exception as e:
            logging.error(f"Error streaming agent text: {e}")

    async def simulate_streaming_response(self, response_text):
        """Simulate streaming by displaying the response with proper formatting"""
        try:

            self.start_agent_message()

            formatted_text = format_response_text(response_text)

            chunks = split_text_for_streaming(formatted_text)

            for chunk in chunks:
                self.stream_agent_text(chunk)
                await asyncio.sleep(0.03)

            self.stream_agent_text("", is_final=True)

        except Exception as e:
            logging.error(f"Error in streaming response: {e}")

            formatted_fallback = format_response_text(response_text)
            self.display_message(f"Agent: {formatted_fallback}", "BOT")


if __name__ == "__main__":
    print("Starting Arxis AI Support Tool Demo...")
    print("This demo simulates the chatbot behavior without requiring OpenAI API.")
    print("Try the following interactions:")
    print("1. Provide your name")
    print("2. Confirm with 'yes' or 'no'")
    print("3. Ask for help")
    print("4. Say 'goodbye' to end the conversation")
    print()

    app = CustomerSupportBotDemo()
    app.mainloop()
