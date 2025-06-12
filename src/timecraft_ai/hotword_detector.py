import pvporcupine
import pyaudio

class HotwordDetector:
    def __init__(self, keyword: str = "mcp", sensitivity: float = 0.7):
        self.keyword = keyword
        self.sensitivity = sensitivity
        self.porcupine = pvporcupine.create(keywords=[self.keyword], sensitivities=[self.sensitivity],
                                             access_key="YOUR_PV_PORCUPINE_ACCESS_KEY")
        self.pa = pyaudio.PyAudio()
        self.audio_stream = self.pa.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length
        )

    def listen_for_hotword(self):
        print(f"🔎 Diga a palavra-chave para ativar: '{self.keyword.upper()}'")
        try:
            while True:
                pcm = self.audio_stream.read(self.porcupine.frame_length, exception_on_overflow=False)
                pcm = memoryview(pcm).cast('h')
                result = self.porcupine.process(pcm)
                if result >= 0:
                    print(f"🟢 Palavra-chave '{self.keyword.upper()}' detectada!")
                    return True
        except KeyboardInterrupt:
            print("\nInterrompido pelo usuário.")
        finally:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            self.pa.terminate()
            self.porcupine.delete()

