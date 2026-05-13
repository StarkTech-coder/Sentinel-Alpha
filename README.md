# 🛡️ SENTINEL ALPHA

**Sentinel Alpha**, M2 Apple Silicon mimarisi için optimize edilmiş, yerel (offline) çalışan bir otonom savunma ve durumsal farkındalık sistemidir.

## 🚀 Teknolojiler
- **Core:** Python 3.12 + Multiprocessing
- **Vision:** YOLOv8n (Metal Performance Shaders - MPS ile hızlandırılmış)
- **Messaging:** ZeroMQ (PUB/SUB)
- **UI:** PyQt6 Stark-HUD Design
- **Intelligence:** Ollama/Llama-3 Local LLM

## 🏗️ Mimari Yapı
Sistem, birbirinden bağımsız çalışan ajanlardan oluşur. Her ajan kendi M2 çekirdeğinde veriyi toplar ve ZMQ üzerinden merkezi yönlendiriciye (Master Router) iletir.

- **VisionAgent:** Canlı hedef takibi (İnsan, Drone, Araç).
- **SystemAgent:** Donanım telemetrisi ve ısı kontrolü.
- **BrainLogic:** Tehdit analizi ve strateji belirleme.

## 🛠️ Kurulum
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py