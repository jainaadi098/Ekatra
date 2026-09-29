# PM-AJAY Voice Livelihood Assistant & District Perspective Planner

[![CI Pipeline](https://github.com/your-username/pmajay-voice-livelihood/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/pmajay-voice-livelihood)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-High%20Concurrency-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Ministry of Social Justice & Empowerment (MoSJE) • Smart India Hackathon (SIH)**  
> Production-grade, vernacular AI livelihood mapping and NSQF-aligned skilling recommendation platform under the **Grant-in-Aid (GIA)** component of PM-AJAY.

---

## 🎯 Ground Challenges Addressed

1. **Information Asymmetry in SC Clusters:** Traditional artisans lack awareness of NSQF alignment and direct grant options.
2. **Academic Gate Exclusion:** Strict schooling requirements typically exclude master craftsmen with zero formal schooling from certifications.
3. **Absence of Perspective Planning:** District administrations lack bottom-up data on village-level skill gaps, resulting in misallocated training center budgets.
4. **Digital Literacy Barrier:** Conventional web-portals fail for non-literate candidates with basic feature phones.

---

## 💡 Core Architecture & Innovations
USER CHANNELS
           [ Web Audio API / Mic ]  [ WhatsApp .ogg Audio ]  [ IVR DTMF Keypad ]
                                       │
                                       ▼
                             FASTAPI ASYNC GATEWAY
                             (Telemetry & Profiling)
                                       │
                                       ▼
                          STATE-AWARE ORCHESTRATOR
                         (1-to-1 Deterministic Router)
                                       │
                                       ▼
                            NSQF ALIGNMENT ENGINE
            (Academic Gate + Haversine Spatial Geofence + RPL Prior Bridge)
                                       │
               ┌───────────────────────┴───────────────────────┐
               ▼                                               ▼
     GIA FINANCIAL ENGINE                             DISTRICT MAPPER

(50% Grant Capped at ₹50,000 +                     (Leaflet.js Dynamic GIS
40% MUDRA + 10% Equity Split)                      Heatmap of Village Gaps)
│
▼
REPORTLAB PDF GENERATOR
(Official Stamped MoSJE Appraisal Dossier)
### Key Technical Pillars
* **Recognition of Prior Learning (RPL) Bridge:** Automatically bypasses formal schooling gates for traditional trades (leathercraft, tailoring, vermicomposting, masonry) and scales course durations down to accelerated 40–80 hour certification tracks.
* **Multi-Channel Accessibility Gateway:** Unified intake supporting Web Audio, binary `.ogg` / `.wav` voice payloads (WhatsApp voice notes), and DTMF keypad tones for 2G feature phones.
* **Deterministic Slot-State Routing:** 1-to-1 index-bound parsing eliminating collisions between educational classes (e.g., class 5 vs index 1) and complex Hindi/English utterances.
* **Perspective Planning GIS Heatmap:** Interactive spatial mapping identifying village skill gaps vs accredited training center capacities (PMKK, RSETI, ITIs).
* **Native Server-Side Appraisal Dossiers:** Direct PDF generation (`ReportLab`) featuring PM-AJAY GIA grant math (50% grant, 40% loan, 10% margin).

---

## 🛠️ Tech Stack

* **Backend:** Python 3.10+, FastAPI (Asynchronous high-concurrency gateway), Pydantic v2
* **Database & GIS:** SQLite3, Spatial Haversine Geofencing
* **PDF Compilation:** ReportLab Engine
* **Frontend:** TailwindCSS, Vanilla ES6+, Leaflet.js OpenStreetMap API
* **Speech Integration:** Web Speech Recognition / Synthesis API, Bhashini ULCA Pipeline Bridge

---

## ⚡ Quickstart & Deployment

### 1. Clone & Set Up Environment
```bash
git clone [https://github.com/your-username/pmajay-voice-livelihood.git](https://github.com/your-username/pmajay-voice-livelihood.git)
cd pmajay-voice-livelihood

# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
2. Run Local Instance
Bash
python run.py

EndpointMethodPayloadFunction/api/session/startPOST?language=hiInitializes candidate session and returns greeting./api/interactPOSTJSON {session_id, transcript, language, channel}Extracts slots and advances state machine./api/voice/ingestPOSTmultipart/form-data (audio_file)Accepts raw .ogg voice notes directly from external channels./api/dossier/pdf/{id}GET?lang=hiCompiles and streams official PDF appraisal sheet./api/analytics/districtGETNoneReturns aggregated skill demand and village GIS clusters.


## 👥 Team Details (SIH 2026)

* **Team Name:** Terra Sentinels[cite: 3]
* **AICTE Application No:** 1-46259231763[cite: 3]
* **Ministry / Organization:** Ministry of Social Justice & Empowerment (MoSJE)
* **Problem Statement:** PM-AJAY GIA Livelihood Mapping & NSQF Skilling Assistant

| S.No. | Name | Designation | Branch / Stream | Year |
| :---: | :--- | :--- | :---: | :---: |
| 1 | **Akhil Dev Pathak**[cite: 3] | Team Leader[cite: 3] | EC[cite: 3] | 3rd[cite: 3] |
| 2 | **Aadi Jain**[cite: 3] | Team Member[cite: 3] | CSE[cite: 3] | 3rd[cite: 3] |
| 3 | **Adrika Soni**[cite: 3] | Team Member[cite: 3] | AIDS[cite: 3] | 3rd[cite: 3] |
| 4 | **Anisha Dhanwani**[cite: 3] | Team Member[cite: 3] | AIDS[cite: 3] | 3rd[cite: 3] |
| 5 | **Vansh Dixit**[cite: 3] | Team Member[cite: 3] | CSE[cite: 3] | 3rd[cite: 3] |
| 6 | **Kawalpreet Singh**[cite: 3] | Team Member[cite: 3] | AIDS[cite: 3] | 3rd[cite: 3] |