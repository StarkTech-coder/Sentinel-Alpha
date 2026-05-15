import zmq
import time
import numpy as np
import pyaudio
from datetime import datetime


def run_acoustic_agent():
    # ZMQ Ayarları
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:5558")  # Ses için 5558 portunu kullanıyoruz

    # PyAudio Ayarları
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    p = pyaudio.PyAudio()
    stream = p.open(
        format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK
    )

    print("[ACOUSTIC_AGENT] Mikrosistem aktif. Ortam dinleniyor... Port: 5558")

    try:
        while True:
            # Ses verisini oku
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)

            # Ses şiddetini hesapla (RMS)
            mean_sq = np.mean(audio_data**2)
            amplitude = np.sqrt(mean_sq) if mean_sq > 0 else 0

            # HUD için normalize et (0-100 arası)
            # 500-1000 arası genelde normal konuşma seviyesidir
            level = min(100, (amplitude / 1000) * 100)

            payload = {
                "agent": "AcousticAgent",
                "timestamp": datetime.now().isoformat(),
                "level": round(level, 2),
                "metadata": {"raw_amplitude": int(amplitude), "status": "LISTENING"},
            }

            socket.send_json(payload)

            # Çok hızlı veri gönderip sistemi yormayalım
            time.sleep(0.05)

    except Exception as e:
        print(f"[ACOUSTIC_AGENT] Hata: {e}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()


if __name__ == "__main__":
    run_acoustic_agent()
