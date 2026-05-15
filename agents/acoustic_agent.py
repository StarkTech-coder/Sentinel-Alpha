import zmq
import time
import numpy as np
import pyaudio
import json
from datetime import datetime


def run_acoustic_agent():
    # 1. ZMQ KURULUMU (Santrale Bağlantı)
    context = zmq.Context()
    # ARTIK PUSH: Veriyi merkeze (Master Router) gönderiyoruz
    socket = context.socket(zmq.PUSH)
    # Master Router'ın giriş portuna (5555) bağlanıyoruz
    socket.connect("tcp://localhost:5555")

    # 2. PYAUDIO AYARLARI
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    p = pyaudio.PyAudio()
    try:
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )
    except Exception as e:
        print(f"[ACOUSTIC_ERROR] Mikrofon açılamadı: {e}")
        return

    print("[ACOUSTIC_AGENT] Mikrosistem aktif. Santrale bağlandı (Giriş: 5555)")

    try:
        while True:
            # Ses verisini oku
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)

            # Ses şiddetini hesapla (RMS)
            mean_sq = np.mean(audio_data.astype(float) ** 2)
            amplitude = np.sqrt(mean_sq) if mean_sq > 0 else 0

            # HUD için normalize et (0-100 arası)
            # M2 mikrofon hassasiyetine göre 1000-2000 arası ideal bir bölendir
            level = min(100, (amplitude / 1500) * 100)

            # 3. SANTAL VE WIDGET UYUMLU PAYLOAD
            payload = {
                "agent": "AcousticAgent",
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "level": round(level, 2),  # Widget bu 'level' anahtarına bakar
                "metadata": {
                    "db_level": round(level, 2),  # Bazı widgetlar db_level arayabilir
                    "raw_amplitude": int(amplitude),
                    "status": "LISTENING",
                },
            }

            # Veriyi Santrale fırlat
            socket.send_json(payload)

            # UI akıcılığı için 50ms (20 FPS) idealdir
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("[ACOUSTIC] Durduruluyor...")
    except Exception as e:
        print(f"[ACOUSTIC_AGENT] Çalışma Hatası: {e}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        socket.close()
        context.term()


if __name__ == "__main__":
    run_acoustic_agent()
