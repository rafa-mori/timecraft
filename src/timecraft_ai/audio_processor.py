import sys
import wave
import json
import pyaudio
from vosk import Model, KaldiRecognizer

# Configuração do modelo
model = Model("models/vosk-model-small-pt")
rec = KaldiRecognizer(model, 16000)
rec.SetWords(True)

# Configuração do PyAudio para capturar áudio
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)

print("🎤 Capturando áudio... Fale algo!")

while True:
    data = stream.read(8192)
    if rec.AcceptWaveform(data):
        result = json.loads(rec.Result())
        print("📝 Transcrição:", result["text"])
