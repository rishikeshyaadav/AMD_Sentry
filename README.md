# AMD Deepfake Sentry

> **Theme:** AI for Social Good / Cybersecurity  
> **Platform:** Browser Extension (Edge/Chrome) + Local Edge AI  
> **Current Version:** 1.0 (Prototype)

---

## 1. Executive Summary
**AMD Deepfake Sentry** is a privacy-first browser extension that detects AI-generated images (Deepfakes) in real-time as users browse the web. Unlike traditional tools that require cloud uploads, Sentry processes data **locally** on the user's device (simulating an NPU workload), ensuring zero data leakage and minimal latency.

---

## 2. System Architecture
The system consists of three distinct components communicating in a loop:

* **The Watchman (Frontend Extension):** Scans webpages for images, filters out icons/ads, and sends valid image URLs to the local engine.
* **The Engine (Local Python Server):** A Flask server that acts as the interface between the browser and the AI model. It handles downloading images and logging history.
* **The Brain (AI Model):** A pre-trained Vision Transformer (ViT) running locally that analyzes pixel artifacts to determine if an image is Real or Fake.

### Data Flow Diagram
`Browser (Image Found)` → `Content Script` → `Background Worker` → `Python Server (Localhost)` → `AI Inference` → `Verdict (Real/Fake)` → `Browser (Draw Border)`

---

## 3. Code Structure & File Manifest
Here is exactly what every file in the project does:

```text
AMD_Sentry/
├── backend/                  # The "Brain" of the operation
│   ├── server.py             # Main Logic: Runs the Web Server & loads AI model.
│   ├── Start_Sentry.bat      # Launcher: One-click script to start the engine.
│   └── templates/            # HTML files for the Dashboard
│       └── dashboard.html    # The "Command Center" UI (charts/logs).
│
└── extension/                # The "Eyes" (Browser Plugin)
    ├── manifest.json         # ID Card: Defines permissions and file links.
    ├── background.js         # The Messenger: Relays data between Tab <-> Server.
    ├── content.js            # The Scanner: Runs on websites, finds images, draws borders.
    ├── popup.html            # The visual menu when you click the toolbar icon.
    └── popup.js              # Logic for the toolbar popup (checks system status).
