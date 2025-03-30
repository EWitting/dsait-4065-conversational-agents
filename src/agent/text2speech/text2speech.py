from gtts import gTTS
from playsound import playsound

# Convert text to speech
tts = gTTS("Hello, world!", lang="en")
tts.save("hello.mp3")

# Play the saved audio
playsound("hello.mp3")
