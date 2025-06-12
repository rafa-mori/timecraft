import pyttsx3

class VoiceSynthesizer:
    def __init__(self, rate: int = 180, volume: float = 1.0, voice: str = None):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)
        if voice:
            self.engine.setProperty('voice', voice)

    def speak(self, text: str):
        self.engine.say(text)
        self.engine.runAndWait()

