import ttkbootstrap as ttk
from bot import BotRunner
import asyncio
from Gui import create_widgets
from fsm_llm.state_models import FSMRun
import threading
import logging


logging.basicConfig(level=logging.DEBUG)


class CustomerSupportBot(ttk.Window):

    chat_entry: ttk.Entry
    chat_display: ttk.Text
    statusLabel: ttk.Label
    progress_bar: ttk.Progressbar
    button: ttk.Button

    def __init__(self, themename="darkly"):
        super().__init__()
        try:

            create_widgets(self)

            self.protocol("WM_DELETE_WINDOW", self.on_closing)

            # Start a dedicated asyncio event loop in a background thread.
            # All async work (OpenAI calls, FSM) will be scheduled onto this loop
            self.loop = asyncio.new_event_loop()
            self.loop_thread = threading.Thread(
                target=self.start_event_loop, daemon=True
            )
            self.loop_thread.start()

            # Bot wrapper that encapsulates FSM and client
            self.bot = BotRunner()
            self.conversation_log = []

            self.after(100, self.show_welcome_message)

        except Exception as e:
            logging.error(f"Error initializing CustomerSupportBot: {e}")
            self.destroy()

    def on_closing(self):
        """Handle window closing"""
        try:
            # Stop the background loop and wait for thread to exit
            if hasattr(self, "loop") and hasattr(self, "loop_thread"):
                try:
                    # Stop the loop thread safely
                    self.loop.call_soon_threadsafe(self.loop.stop)
                    self.loop_thread.join(timeout=2)
                except Exception:
                    pass
        except Exception:
            pass
        self.destroy()

    def show_welcome_message(self):
        """Show welcome message after GUI is fully initialized"""
        welcome_msg = "Hello! Welcome to Arxis AI Support. I'm here to help you. May I please have your name?"
        # Schedule the welcome message to run on the background loop
        try:
            self.run_async_in_thread(self.simulate_streaming_response(welcome_msg))
        except Exception as e:
            logging.error(f"Failed to schedule welcome message: {e}")

    def run_async_in_thread(self, coro):
        """Run an async coroutine in a thread"""
        try:
            # Schedule coroutine on the background loop and attach an error handler
            future = asyncio.run_coroutine_threadsafe(coro, self.loop)

            def _done_callback(fut):
                try:
                    fut.result()
                except Exception as exc:
                    logging.error(f"Coroutine raised: {exc}")

            future.add_done_callback(_done_callback)
            return future
        except Exception as e:
            logging.error(f"Error in async thread: {e}")

    def start_event_loop(self):
        # This runs in the background thread
        try:
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()
        except Exception as e:
            logging.error(f"Background event loop stopped with error: {e}")

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

        # Schedule the async processing onto the background loop and handle completion
        try:
            future = asyncio.run_coroutine_threadsafe(
                self.process_chat(user_input), self.loop
            )

            def _on_done(fut):
                exc = fut.exception()
                if exc:
                    logging.error(f"Error in process_chat: {exc}")
                    self.after(0, lambda: self.handle_processing_error(str(exc)))
                # Re-enable input on the main thread
                self.after(0, self.enable_input)

            future.add_done_callback(_on_done)
        except Exception as e:
            logging.error(f"Failed to schedule process_chat: {e}")
            self.after(0, self.handle_processing_error, str(e))
            self.after(0, self.enable_input)

    def enable_input(self):
        """Re-enable input field"""
        try:
            self.chat_entry.config(state="normal")
            self.chat_entry.focus()
        except Exception as e:
            logging.error(f"Error enabling input: {e}")

    def handle_processing_error(self, error_msg):
        """Handle processing errors on main thread"""
        try:
            self.update_status("Error occurred", show_progress=False)

            threading.Thread(
                target=self.run_async_in_thread,
                args=(
                    self.simulate_streaming_response(
                        f"Sorry, I encountered an error: {error_msg}"
                    ),
                ),
                daemon=True,
            ).start()
        except Exception as e:
            logging.error(f"Error handling processing error: {e}")

    def handle_exception(self, exc: Exception, user_message: str = "An error occurred"):
        """Centralized exception handler: log and notify user"""
        try:
            logging.exception("Unhandled exception: %s", exc)
            self.update_status(user_message, show_progress=False)
            self.after(0, lambda: self.display_message(f"Agent: {user_message}", "BOT"))
        except Exception:
            logging.error("Error while handling exception")

    async def process_chat(self, user_input):
        try:

            self.after(
                0, lambda: self.update_status("AI is thinking...", show_progress=True)
            )

            logging.debug(f"Current FSM state: {self.bot.get_state()}")
            logging.debug(f"User input: {user_input}")

            if user_input.lower() in ["quit", "exit"]:
                try:
                    # attempt to set FSM to END if available
                    getattr(
                        self.bot.support_bot.fsm, "set_next_state", lambda *_: None
                    )("END")
                except Exception:
                    pass
                self.after(
                    0,
                    lambda: self.update_status(
                        "Conversation ended", show_progress=False
                    ),
                )
                self.after(
                    0,
                    lambda: self.display_message(
                        "Agent: Conversation ended. Thank you!", "BOT"
                    ),
                )
                return

            run_state: FSMRun = await self.bot.process(
                user_input=user_input, model="gpt-5-nano-2025-08-07"
            )

            await self.simulate_streaming_response(run_state.response)

            if self.bot.is_completed():
                self.after(
                    0,
                    lambda: self.update_status(
                        "Conversation completed", show_progress=False
                    ),
                )
                await self.simulate_streaming_response("Conversation ended. Thank you!")
            else:
                self.after(
                    0,
                    lambda: self.update_status(
                        "Waiting for your response...", show_progress=False
                    ),
                )

        except Exception as e:
            logging.error(f"Error in process_chat: {e}")
            self.after(
                0, lambda: self.update_status("Error occurred", show_progress=False)
            )
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

            self.after(0, self.start_agent_message)
            await asyncio.sleep(0.1)

            formatted_text = self._format_response_text(response_text)

            chunks = self._split_text_for_streaming(formatted_text)

            for chunk in chunks:
                self.after(0, lambda text=chunk: self.stream_agent_text(text))
                await asyncio.sleep(0.03)

            self.after(0, lambda: self.stream_agent_text("", is_final=True))

        except Exception as e:
            logging.error(f"Error in streaming response: {e}")

            formatted_fallback = self._format_response_text(response_text)
            self.after(
                0, lambda: self.display_message(f"Agent: {formatted_fallback}", "BOT")
            )

    def _format_response_text(self, text):
        """Format the response text for proper display in the GUI"""
        if not text:
            return text

        formatted = text.replace("\\n", "\n")

        lines = formatted.split("\n")
        processed_lines = []

        for line in lines:

            if line.strip() and line.strip()[0].isdigit() and ")" in line[:5]:
                processed_lines.append(line)

            elif line.strip().startswith("-"):
                processed_lines.append(line)

            else:
                processed_lines.append(line)

        return "\n".join(processed_lines)

    def _split_text_for_streaming(self, text):
        """Split text into chunks for streaming while preserving formatting"""
        chunks = []
        lines = text.split("\n")

        for i, line in enumerate(lines):
            if line.strip():

                words = line.split()
                current_chunk = ""

                for word in words:
                    if current_chunk:
                        current_chunk += " " + word
                    else:
                        current_chunk = word

                    if len(current_chunk) > 20 or word == words[-1]:
                        chunks.append(current_chunk)
                        current_chunk = ""

            if i < len(lines) - 1:
                chunks.append("\n")

        return chunks


if __name__ == "__main__":
    app = CustomerSupportBot()
    app.mainloop()
