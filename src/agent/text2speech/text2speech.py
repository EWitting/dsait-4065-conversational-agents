import os
import uuid
import threading
import time
import queue
from gtts import gTTS
import librosa
import sounddevice as sd

def play_audio(filename):
    audio, sr = librosa.load(filename)
    sd.play(audio, sr)
    sd.wait()  # Wait until audio is done playing

class Text2Speech:
    """
    A class to handle text-to-speech conversion and playback.
    Uses gTTS for conversion and playsound for audio playback.
    """

    def __init__(self, lang="en", slow=False, debug=False):
        """
        Initialize the Text2Speech engine.

        Args:
            lang (str): Language code for the speech (default: "en")
            slow (bool): Whether to speak slowly (default: False)
            debug (bool): Whether to print debug information (default: False)
        """
        self.lang = lang
        self.slow = slow
        self.audio_files = []
        self.current_audio = None
        self.debug = debug

        # Speech queue and processing thread
        self.speech_queue = queue.Queue()
        self.is_speaking = False
        self.stop_requested = False

        # Start speech processing thread
        self.speech_thread = threading.Thread(target=self._process_speech_queue)
        self.speech_thread.daemon = True
        self.speech_thread.start()

        self._log("Text2Speech initialized")

    def _log(self, message):
        """Internal method for logging debug messages"""
        if self.debug:
            print(f"[Text2Speech] {message}")

    def convert_to_speech(self, text):
        """
        Convert text to speech and save it as an audio file.

        Args:
            text (str): The text to convert to speech

        Returns:
            str: Path to the generated audio file
        """
        # Process text to extract summary if available
        original_text = text

        # Check for Summary section
        if "Summary:" in text:
            # Get only the text after "Summary:"
            text = text.split("Summary:", 1)[1].strip()

        # If the text is empty after processing, fall back to original
        if not text:
            text = original_text

        # Remove any markdown numbered/bullet list markers
        lines = text.split('\n')
        processed_lines = []

        for line in lines:
            # Remove numbered list markers (e.g., "1. ", "2. ")
            line = line.strip()
            if line and line[0].isdigit() and '. ' in line[:4]:
                line = line.split('. ', 1)[1]
            # Remove bullet list markers
            if line.startswith('- ') or line.startswith('* '):
                line = line[2:]
            processed_lines.append(line)

        text = ' '.join(processed_lines)

        # Generate a unique filename
        filename = f"speech_{uuid.uuid4()}.mp3"

        # Create the TTS object and save to file
        tts = gTTS(text=text, lang=self.lang, slow=self.slow)
        tts.save(filename)

        # Add to our list of generated files
        self.audio_files.append(filename)
        self.current_audio = filename

        return filename

    def play_speech(self, text=None, filename=None):
        """
        Play speech from text or from a saved file.

        Args:
            text (str, optional): Text to convert and play
            filename (str, optional): Path to an existing audio file to play

        Returns:
            bool: True if playback was successful
        """
        try:
            # If text is provided, convert it first
            if text:
                filename = self.convert_to_speech(text)

            # If no filename provided and no current audio, can't play
            if not filename and not self.current_audio:
                return False

            # Use the provided filename or the current audio
            audio_file = filename or self.current_audio

            # Play the audio in a separate thread to avoid blocking
            threading.Thread(target=play_audio, args=(audio_file,)).start()
            return True

        except Exception as e:
            print(f"Error playing speech: {str(e)}")
            return False

    def speak(self, text):
        """
        Add text to the speech queue for processing.

        Args:
            text (str): The text to speak

        Returns:
            bool: True if added to queue successfully
        """
        try:
            self._log(f"Adding to speech queue: '{text[:30]}...' ({len(text)} chars)")

            # Check if this text contains a summary marker
            if "Summary:" in text:
                self._log("Summary marker detected - will speak only the summary section")

            self.speech_queue.put(text)
            return True
        except Exception as e:
            self._log(f"Error adding to speech queue: {str(e)}")
            return False

    def _process_speech_queue(self):
        """
        Process the speech queue in a separate thread.
        This ensures each speech segment plays completely before starting the next.
        """
        self._log("Speech queue processing started")
        while not self.stop_requested:
            try:
                # Check if there's anything in the queue
                if not self.speech_queue.empty():
                    # Get the next text to speak
                    text = self.speech_queue.get()
                    self._log(f"Processing speech: '{text[:30]}...' ({len(text)} chars)")

                    # Mark as speaking
                    self.is_speaking = True

                    # Convert and play
                    filename = self.convert_to_speech(text)
                    self._log(f"Playing audio file: {filename}")
                    play_audio(filename)

                    # Mark task as done
                    self.speech_queue.task_done()
                    self.is_speaking = False
                    self._log("Speech complete")
                else:
                    # No speech to process, sleep a bit to prevent CPU hogging
                    time.sleep(0.1)
            except Exception as e:
                self._log(f"Error in speech queue processing: {str(e)}")
                # Continue processing the queue even if one item fails
                self.is_speaking = False
                time.sleep(0.1)

    def wait_until_done(self, timeout=None):
        """
        Wait until all queued speech has finished playing.

        Args:
            timeout (float, optional): Maximum time to wait in seconds

        Returns:
            bool: True if all speech completed, False if timed out
        """
        if timeout:
            end_time = time.time() + timeout
            while not self.speech_queue.empty() or self.is_speaking:
                if time.time() > end_time:
                    return False
                time.sleep(0.1)
            return True
        else:
            # Wait indefinitely
            while not self.speech_queue.empty() or self.is_speaking:
                time.sleep(0.1)
            return True

    def cleanup(self):
        """
        Stop the speech thread and remove all temporary audio files.
        """
        # Signal the thread to stop
        self.stop_requested = True

        # Wait for the thread to finish (with timeout)
        if hasattr(self, 'speech_thread') and self.speech_thread.is_alive():
            self.speech_thread.join(timeout=2.0)

        for file in self.audio_files:
            try:
                if os.path.exists(file):
                    os.remove(file)
            except Exception as e:
                print(f"Error cleaning up file {file}: {str(e)}")

        # Clear the list after cleanup
        self.audio_files = []
        self.current_audio = None


# Example usage (only runs if this file is executed directly)
if __name__ == "__main__":
    tts = Text2Speech()
    tts.speak("Hello, world!")
    # Wait a bit for the speech to finish before exiting
    import time

    time.sleep(3)
    tts.cleanup()