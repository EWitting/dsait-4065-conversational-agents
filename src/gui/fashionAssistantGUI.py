import tkinter as tk
import uuid
from tkinter import scrolledtext, filedialog, messagebox
from PIL import Image, ImageTk
import threading
import io
import base64
import time
import sounddevice as sd
import wavio
import os

# Import your existing components
from src.agent.controller.controller import Controller
from src.agent.asr.asr import ASR
from src.agent.memory.memory import Memory
from src.agent.emotion.emotion import EmotionSystem
from src.agent.generator.generator import Generator
from src.agent.controller.controller import ConversationPhase


class FashionAssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Fashion Assistant")
        self.root.geometry(
            "1000x600"
        )  # Wider window to accommodate side-by-side layout
        self.root.configure(bg="#f0f0f0")

        # Initialize conversation state
        self.conversation_active = False
        self.listening = False

        # Initialize components
        self.initialize_components()
        self.setup_layout()

        # Initialize agent components
        self.asr = ASR(model_name="base")
        self.memory = Memory()
        self.emotion = EmotionSystem()
        self.generator = Generator()
        self.controller = Controller(
            asr=self.asr,
            memory=self.memory,
            emotion=self.emotion,
            generator=self.generator,
        )

        # Override controller methods
        self.override_controller_methods()

    def initialize_components(self):
        # Main container for side-by-side layout
        self.main_container = tk.Frame(self.root, bg="#f0f0f0")

        # Left frame - for chat area
        self.left_frame = tk.Frame(self.main_container, bg="#f0f0f0")

        # Right frame - for image display
        self.right_frame = tk.Frame(self.main_container, bg="#f0f0f0", width=400)

        # Chat display area
        self.chat_frame = tk.Frame(self.left_frame, bg="#f0f0f0")
        self.chat_display = scrolledtext.ScrolledText(
            self.chat_frame,
            wrap=tk.WORD,
            width=50,
            height=20,
            font=("Arial", 10),
            bg="white",
        )
        self.chat_display.config(state=tk.DISABLED)

        # User input area
        self.input_frame = tk.Frame(self.left_frame, bg="#f0f0f0")
        self.user_input = tk.Entry(self.input_frame, width=50, font=("Arial", 10), bd=2)
        self.user_input.bind("<Return>", self.send_message)

        # Buttons
        self.button_frame = tk.Frame(self.left_frame, bg="#f0f0f0")
        self.send_button = tk.Button(
            self.button_frame,
            text="Send",
            command=self.send_message,
            width=10,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
        )
        self.speak_button = tk.Button(
            self.button_frame,
            text="Speak",
            command=self.toggle_listening,
            width=10,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
        )
        self.new_convo_button = tk.Button(
            self.button_frame,
            text="New Conversation",
            command=self.start_new_conversation,
            width=15,
            bg="#FF9800",
            fg="white",
            font=("Arial", 10, "bold"),
        )

        # Image display area
        self.image_frame = tk.Frame(self.right_frame, bg="#f0f0f0")
        self.image_label = tk.Label(self.image_frame, bg="#f0f0f0")

        # Status bar
        self.status_bar = tk.Label(
            self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W
        )

        # Track previous suggestions
        self.previous_suggestions = []

    def setup_layout(self):
        # Pack main container
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left side - Chat area
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Chat display
        self.chat_frame.pack(fill=tk.BOTH, expand=True)
        self.chat_display.pack(fill=tk.BOTH, expand=True)

        # Input area and buttons in left frame
        self.input_frame.pack(fill=tk.X, pady=5)
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.button_frame.pack(fill=tk.X, pady=5)
        self.send_button.pack(side=tk.LEFT, padx=5)
        self.speak_button.pack(side=tk.LEFT, padx=5)
        self.new_convo_button.pack(side=tk.RIGHT, padx=5)

        # Right side - Image display
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        self.right_frame.pack_propagate(False)  # Prevent frame from shrinking

        # Image frame in right side
        self.image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.image_label.pack(expand=True)

        # Status bar at the bottom
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def display_system_message(self, message):
        """Display a system message in the chat display with a different format."""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(
            tk.END, "System: " + message + "\n\n", "system_message"
        )
        # Define a tag for system messages with a gray color
        self.chat_display.tag_configure(
            "system_message", foreground="#555555", font=("Arial", 9, "italic")
        )
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def override_controller_methods(self):
        # Override controller's speak method
        self.controller.speak = self.display_assistant_message

        # Override controller's listen method
        original_listen = self.controller.listen

        def new_listen():
            """
            Modified listen method that waits for either text input or speak button press
            """
            # Reset input state
            self.waiting_for_input = True
            self.last_input = None

            # Let the user know we're waiting for input
            self.display_system_message(
                "Please type your response or press 'Speak' to use voice input."
            )
            self.update_status("Waiting for input...")

            # Wait for either text input or voice input to complete
            while self.waiting_for_input:
                self.root.update()
                time.sleep(0.1)

                # Exit the loop if input has been provided
                if self.last_input is not None:
                    break

            # Get whatever input was provided
            input_text = self.last_input if self.last_input is not None else ""

            # Reset for next input
            self.last_input = None

            return input_text, "neutral"

        self.controller.listen = new_listen

        # Override controller's show_image method
        def new_show_image(image):
            try:
                # Check if image is a string (path or base64)
                if isinstance(image, str):
                    # For base64 encoded images
                    if image.startswith("data:image"):
                        # Extract the base64 part
                        base64_data = image.split(",")[1]
                        image_data = base64.b64decode(base64_data)
                        image = Image.open(io.BytesIO(image_data))
                    else:
                        # For file paths
                        image = Image.open(image)
                # If image is already a PIL Image object, use it directly
                elif isinstance(image, Image.Image):
                    # Image is already a PIL Image object, no need to process
                    pass
                else:
                    raise TypeError(f"Unsupported image type: {type(image)}")

                # Resize image to fit the window
                image = self.resize_image(image)

                photo = ImageTk.PhotoImage(image)
                self.image_label.config(image=photo)
                self.image_label.image = photo  # Keep a reference
            except Exception as e:
                self.display_assistant_message(f"Failed to display image: {str(e)}")

        self.controller.show_image = new_show_image

        original_handle_recommending = self.controller.handle_recommending

        def new_handle_recommending():
            self.controller.speak("Here is a recommendation for you.")
            memories = self.controller.memory.retrieve(
                self.controller.user, self.controller.conversation_index
            )

            # Pass previous suggestions to generate
            text, image = self.controller.generator.generate(
                self.controller.context, memories, self.previous_suggestions
            )

            # Store this suggestion for future reference
            self.previous_suggestions.append(text)

            self.controller.speak(text)
            self.controller.show_image(image)

            self.controller.speak("What do you think?")
            response, emotion = self.controller.listen()

            preference = dict(outfit=text, response=response, emotion=emotion)
            self.controller.memory.add_preference(
                self.controller.user, self.controller.conversation_index, preference
            )

            self.controller.speak("Are you satisfied with the recommendation?")
            response, _ = self.controller.listen()

            # Make the check case-insensitive by converting to lowercase
            # Also check if 'yes' is in the response, not just equal to 'yes'
            if "yes" in response.lower():
                self.controller.speak(
                    "Thank you for using our service. Have a nice day!"
                )
                return ConversationPhase.END
            else:
                return ConversationPhase.RECOMMENDING

        self.controller.handle_recommending = new_handle_recommending

    def resize_image(self, image, max_width=380, max_height=400):
        """Resize image to fit within the side panel while maintaining aspect ratio"""
        width, height = image.size
        if width > max_width or height > max_height:
            ratio = min(max_width / width, max_height / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            return image.resize((new_width, new_height), Image.LANCZOS)
        return image

    def display_assistant_message(self, message):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "Assistant: " + message + "\n\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self.update_status("Ready")

    def display_user_message(self, message):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "You: " + message + "\n\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def send_message(self, event=None):
        """Handle text input submission"""
        message = self.user_input.get().strip()
        if message:
            self.display_user_message(message)
            self.user_input.delete(0, tk.END)
            self.last_input = message
            self.waiting_for_input = False

    def toggle_listening(self):
        """Toggle voice input recording"""
        if not self.listening:
            # Start listening
            self.listening = True
            # Disable the button while recording to prevent multiple clicks
            self.speak_button.config(
                text="Recording...", bg="#F44336", state=tk.DISABLED
            )
            self.update_status("Listening...")

            # Start recording in a separate thread
            threading.Thread(target=self.record_audio).start()
        else:
            # This shouldn't happen with the disabled button during recording
            pass

    def record_audio(self):
        """Record audio and process it with ASR"""
        try:
            # Set up recording parameters
            duration = 5  # seconds
            fs = 16000  # sample rate

            # Show recording status
            self.update_status(f"Recording for {duration} seconds...")

            # Perform the recording
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
            sd.wait()  # Wait until recording is finished

            # Create temporary filename
            temp_filename = f"temp_{uuid.uuid4()}.wav"
            wavio.write(temp_filename, recording, fs, sampwidth=2)

            # Transcribe the audio
            text = self.asr.transcribe(temp_filename)

            # Clean up the temporary file
            os.remove(temp_filename)

            # Display the transcription result
            self.display_system_message(f'Voice recognized: "{text}"')

            # Also display as user message
            if text:
                self.display_user_message(text)

            # Store the transcription as input and signal that we're done waiting
            self.last_input = text
            self.waiting_for_input = False

        except Exception as e:
            self.display_system_message(f"Error recording audio: {str(e)}")
            # Still need to provide something and mark as not waiting
            self.last_input = ""
            self.waiting_for_input = False
        finally:
            # IMPORTANT: Use root.after to ensure button state is updated in the main thread
            # This ensures the button is properly re-enabled
            self.root.after(0, self._reset_speak_button)
            self.update_status("Ready")

    def start_listening(self):
        self.update_status("Listening...")
        # The actual listening happens in the controller's listen method
        # Add a timeout to prevent indefinite listening
        timeout = 10  # seconds
        start_time = time.time()

        while self.listening and time.time() - start_time < timeout:
            # Check periodically if we're still supposed to be listening
            time.sleep(0.1)

        # If we're still in listening mode after timeout, automatically stop it
        if self.listening:
            self.toggle_listening()

    def update_status(self, message):
        self.status_bar.config(text=message)
        self.root.update()

    def start_new_conversation(self):
        # Reset controller state
        self.controller.phase = ConversationPhase.ASK_NAME
        self.controller.user = ""
        self.controller.context = None
        self.controller.conversation_index = 0

        # Clear chat display
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state=tk.DISABLED)

        # Clear image
        self.image_label.config(image="")

        # Reset previous suggestions
        self.previous_suggestions = []

        # Set conversation state and start new thread
        self.conversation_active = True
        threading.Thread(target=self.run_conversation).start()

    def run_conversation(self):
        self.update_status("Conversation started")
        self.new_convo_button.config(state=tk.DISABLED)
        try:
            self.controller.start()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            self.conversation_active = False
            self.new_convo_button.config(state=tk.NORMAL)
            self.update_status("Conversation ended")

    def _reset_speak_button(self):
        """Helper method to reset the speak button state correctly in the main thread"""
        self.listening = False
        self.speak_button.config(text="Speak", bg="#2196F3", state=tk.NORMAL)
