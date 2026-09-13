# 🚚 Supply Chain Disruption Assistant & Fleet Utilisation Optimizer

An AI-assisted logistics dashboard that helps logistics teams identify shipment disruptions, detect cold-chain risks, find available fleet capacity, and recommend alternative carriers and routes.

---

## 👥 Team

| Field         | Value                                                                                                                                                                                                                               |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Team Name** | codevault                                                                                                                                                                                                                           |
| **Track**     | L2 — Supply Chain Disruption Assistant & Fleet Utilisation Optimizer                                                                                                                                                                |
| **Team Lead** | Om Patel — [26ce067@charusat.edu.in](mailto:26ce067@charusat.edu.in)                                                                                                                                                                |
| **Members**   | Dhruvin Dhanani — [26ce021@charusat.edu.in](mailto:26ce021@charusat.edu.in), Shaurya Chaudhary — [26ce015@charusat.edu.in](mailto:26ce015@charusat.edu.in), Somya Patel — [26ce076@charusat.edu.in](mailto:26ce076@charusat.edu.in) |

---

## 🎯 Problem Statement

Logistics teams need to react quickly when ports, roads, or carriers are disrupted. A disruption can affect multiple shipments while available vehicles and cold-chain risks may be overlooked.

This project provides a centralized assistant that identifies affected shipments, detects temperature excursions, finds available fleet, and recommends alternative carriers and routes.

---

## 💡 Solution

We built a FastAPI backend and browser-based dashboard that analyzes shipment, disruption, fleet, carrier, and temperature data.

The system combines deterministic logistics analysis with an IBM watsonx.ai integration for generating a natural-language situation summary when watsonx.ai credentials are configured.

---

## ✨ Key Features

* **Disruption Detection:** Identifies shipments affected by active port, road, and carrier disruptions.
* **Fleet Utilisation:** Finds available vehicles and matches them according to capacity, location, and cold-chain requirements.
* **Cold-Chain Monitoring:** Detects temperature readings above the 2°C–8°C operating range and assigns risk severity.
* **Alternative Recommendations:** Suggests alternative carriers, vehicles, and routes while considering the current disruption and cargo requirements.
* **AI Situation Summary:** Uses IBM watsonx.ai to generate a concise operational briefing when configured.
* **Automated Testing:** Includes 45 automated tests covering the core logistics analysis.
* **Operational Dashboard:** Presents affected shipments, fleet availability, temperature risks, and recommendations in one interface.

---

## 🛠️ Tech Stack

| Category             | Technologies                  |
| -------------------- | ----------------------------- |
| **Languages**        | Python, HTML, CSS, JavaScript |
| **Frameworks**       | FastAPI                       |
| **IBM Technologies** | IBM watsonx.ai, IBM Bob       |
| **Data Processing**  | Pandas, NumPy                 |
| **Testing**          | Python unittest               |
| **Development**      | Git, GitHub, IBM Bob          |
| **Frontend**         | HTML, CSS, JavaScript         |
| **Backend Server**   | Uvicorn                       |

---

## 📁 Repository Structure

```text
├── .github/
│   └── workflows/
├── src/
│   ├── backend/
│   │   ├── analysis.py
│   │   ├── main.py
│   │   └── watsonx_client.py
│   ├── data/
│   │   ├── carriers.csv
│   │   ├── disruptions.csv
│   │   ├── fleet.csv
│   │   ├── shipments.csv
│   │   └── temperature_readings.csv
│   ├── frontend/
│   │   ├── index.html
│   │   ├── script.js
│   │   └── style.css
│   ├── .env.example
│   ├── README.md
│   └── requirements.txt
├── tests/
│   └── test_analysis.py
├── docs/
├── demo/
├── presentation/
├── submission.yaml
├── CONTRIBUTING.md
├── .gitignore
└── README.md
```

---

## ⚡ How to Run

### 1. Clone the repository

```bash
git clone https://github.com/dhruvin-dhanani/bob-ai-hackathon-codevault.git
cd bob-ai-hackathon-codevault
```

### 2. Create a Python virtual environment

On Windows:

```powershell
python -m venv venv
```

### 3. Activate the virtual environment

```powershell
venv\Scripts\activate
```

### 4. Install dependencies

```powershell
pip install -r src\requirements.txt
```

### 5. Start the backend

From the repository root:

```powershell
uvicorn src.backend.main:app --reload
```

The backend will run at:

```text
http://127.0.0.1:8000
```

### 6. Start the frontend

Open a second terminal and navigate to the frontend directory:

```powershell
cd src\frontend
```

Start the frontend server:

```powershell
python -m http.server 5500
```

Open the application in a browser:

```text
http://127.0.0.1:5500
```

---

## 🤖 IBM watsonx.ai Integration

The project includes an IBM watsonx.ai integration through the backend.

The `watsonx_client.py` module connects to IBM watsonx.ai using the official Python SDK when valid credentials are configured.

The application uses watsonx.ai to generate a concise operational situation summary based on the current logistics data.

The application can also run without watsonx.ai credentials. In that case, the dashboard safely displays:

```text
Situation summary unavailable - watsonx.ai not configured.
```

Required credentials should be stored locally and must never be committed to GitHub.

---

## 🤖 IBM Bob Development Workflow

IBM Bob was used as a genuine part of the development workflow rather than being mentioned only as a technology.

Bob was used to assist with development and testing of the logistics analysis functionality. In particular, Bob helped create and expand the automated test suite covering disruption detection, fleet utilisation, temperature excursions, recommendations, and data integrity.

The resulting test suite contains 45 automated tests, all of which currently pass.

---

## 🧪 Testing

Run the automated test suite from the repository root:

```powershell
python -m unittest tests/test_analysis.py -v
```

The current test suite contains **45 tests** covering:

* Disruption detection
* Active and resolved disruptions
* Affected shipment identification
* False-positive prevention
* Idle fleet detection
* Fleet capacity matching
* Fleet location preference
* Cold-chain vehicle requirements
* Temperature excursions
* Temperature severity
* Cold-chain risk messages
* Alternative carrier recommendations
* Route recommendations
* Recommendation data integrity
* Source data integrity

Current test result:

```text
Ran 45 tests
OK
```

---

## 📊 Current Prototype Capabilities

The current prototype works with logistics datasets containing:

* Shipments
* Disruptions
* Fleet vehicles
* Temperature readings
* Carriers

The dashboard currently identifies:

* **4 affected shipments**
* **4 available fleet vehicles**
* **2 cold-chain temperature excursions**
* **4 alternative recommendations**

The recommendations consider factors such as vehicle capacity, vehicle availability, origin, cold-chain requirements, carrier availability, current carrier, disruption reason, and temperature risk.

---

## 🖥️ Demo

| Artifact        | Location                   |
| --------------- | -------------------------- |
| 📹 Demo Video   | `demo/demo-video-link.txt` |
| 🖼️ Screenshots | `demo/screenshots/`        |
| 📊 Presentation | `presentation/`            |

Demo artifacts will be completed before final submission.

---

## ⚠️ Known Limitations

* The current prototype uses CSV files rather than a production database.
* Live GPS, traffic, port, and carrier APIs are not connected.
* The watsonx.ai situation summary requires valid IBM watsonx.ai credentials to generate an AI response.
* Vehicle and route recommendations currently use deterministic logistics rules rather than a live optimisation engine.
* Authentication and role-based access control are not implemented in the prototype.
* The application is intended as a hackathon prototype rather than a production logistics platform.

---

## 🔮 Future Improvements

Potential future improvements include:

* Integration with live GPS and traffic data.
* Real-time port and road disruption feeds.
* Live IoT temperature streaming.
* Production database integration.
* Advanced route optimisation.
* Predictive disruption analysis.
* Automated notifications for high-risk shipments.
* Role-based access control.
* More advanced AI-powered logistics planning using watsonx.ai.

---

## 🏅 What We're Most Proud Of

The project goes beyond simply displaying logistics data. It connects multiple operational signals — disruptions, shipment priority, fleet availability, vehicle capacity, carrier capabilities, routes, and cold-chain temperature excursions — to produce actionable recommendations.

The project also includes a genuine IBM Bob-assisted development workflow, an IBM watsonx.ai integration, a working FastAPI backend, an interactive frontend dashboard, and an automated test suite containing 45 passing tests.
