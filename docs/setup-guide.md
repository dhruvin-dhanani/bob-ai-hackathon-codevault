# Setup Guide

This guide explains how to install, run, verify, and test the Supply Chain Disruption Assistant & Fleet Utilisation Optimizer locally.

## Prerequisites

Before starting, make sure you have:

* Python 3.12 or newer
* Git
* A web browser such as Chrome or Edge
* Windows PowerShell or Command Prompt

No database server is required because the current prototype uses CSV datasets.

IBM watsonx.ai credentials are optional. The application can run without them.

## Project Structure

The main application is located inside `src/`:

```text
src/
├── backend/
│   ├── analysis.py
│   ├── main.py
│   └── watsonx_client.py
├── data/
│   ├── carriers.csv
│   ├── disruptions.csv
│   ├── fleet.csv
│   ├── shipments.csv
│   └── temperature_readings.csv
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
├── .env.example
└── requirements.txt
```

## Installation

### 1. Clone the repository

```powershell
git clone https://github.com/dhruvin-dhanani/bob-ai-hackathon-codevault.git
cd bob-ai-hackathon-codevault
```

### 2. Create a Python virtual environment

```powershell
python -m venv venv
```

### 3. Activate the virtual environment

```powershell
venv\Scripts\activate
```

After activation, the terminal normally shows `(venv)` at the beginning of the command prompt.

### 4. Install Python dependencies

```powershell
pip install -r src\requirements.txt
```

The main dependencies include:

* FastAPI
* Uvicorn
* Pandas
* NumPy
* python-dotenv
* IBM watsonx.ai Python SDK

## Environment Variables

The project includes:

```text
src/.env.example
```

The watsonx.ai integration uses the following environment variables:

| Variable             | Description                | Required |
| -------------------- | -------------------------- | -------- |
| `WATSONX_API_KEY`    | IBM watsonx.ai API key     | No       |
| `WATSONX_PROJECT_ID` | IBM watsonx.ai project ID  | No       |
| `WATSONX_URL`        | IBM watsonx.ai service URL | No       |

These variables are optional because the application has a safe fallback when watsonx.ai is not configured.

Never commit real API keys or other credentials to GitHub.

## Running the Backend

From the repository root, with the virtual environment activated, run:

```powershell
uvicorn src.backend.main:app --reload
```

The backend should start at:

```text
http://127.0.0.1:8000
```

### Verify the backend

Open this URL in your browser:

```text
http://127.0.0.1:8000
```

You should see:

```text
{"message":"Supply Chain Disruption Assistant is running!"}
```

The backend also provides these API endpoints:

```text
/affected-shipments
/idle-fleet
/temperature-excursions
/recommendations
/situation-summary
```

## Running the Frontend

Keep the backend terminal running.

Open a second terminal and navigate to:

```powershell
cd src\frontend
```

Start the frontend server:

```powershell
python -m http.server 5500
```

The frontend should be available at:

```text
http://127.0.0.1:5500
```

Open that URL in a browser.

The dashboard should display:

* Affected shipments
* Idle fleet
* Temperature excursions
* Alternative recommendations
* Situation summary

## Running Tests

Open a terminal at the repository root and make sure the virtual environment is activated.

Run:

```powershell
python -m unittest tests/test_analysis.py -v
```

The current test suite contains 45 automated tests.

A successful run should end with:

```text
Ran 45 tests
OK
```

The tests cover:

* Disruption detection
* Affected shipment identification
* Idle fleet detection
* Fleet capacity matching
* Cold-chain requirements
* Temperature excursions
* Temperature severity
* Alternative carrier recommendations
* Route recommendations
* Data integrity

## Quick Verification

After starting both servers:

1. Open `http://127.0.0.1:8000`.
2. Confirm the backend status message appears.
3. Open `http://127.0.0.1:5500`.
4. Confirm the dashboard loads.
5. Confirm the dashboard displays:

   * Affected Shipments: 4
   * Idle Fleet: 4
   * Temperature Excursions: 2
   * Recommendations: 4
6. Click the Refresh button once.
7. Confirm the dashboard reloads the same data successfully.

## watsonx.ai Without Credentials

The application does not require watsonx.ai credentials for the core dashboard.

If credentials are not configured, the situation-summary endpoint returns:

```text
Situation summary unavailable - watsonx.ai not configured.
```

This does not prevent the other dashboard features from working.

To enable the AI-generated situation summary, configure valid watsonx.ai credentials locally using the environment variables described above.

## Troubleshooting

| Issue                             | Solution                                                                                                           |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `python` is not recognized        | Install Python and ensure it is added to PATH.                                                                     |
| `pip` is not recognized           | Reinstall Python with the PATH option enabled, or use `python -m pip`.                                             |
| `ModuleNotFoundError`             | Activate the virtual environment and run `pip install -r src\requirements.txt`.                                    |
| `uvicorn` is not recognized       | Activate the virtual environment and reinstall the dependencies.                                                   |
| Port 8000 is already in use       | Stop the other process using port 8000 before starting the backend.                                                |
| Port 5500 is already in use       | Stop the other process using port 5500 or use another available port.                                              |
| Frontend cannot load backend data | Make sure the backend is running at `http://127.0.0.1:8000`.                                                       |
| Dashboard shows `—` values        | Check that the backend server is running and refresh the dashboard.                                                |
| watsonx.ai summary unavailable    | Configure valid watsonx.ai credentials, or continue using the application without the optional AI summary.         |
| Tests fail                        | Activate the virtual environment and run `pip install -r src\requirements.txt` again, then rerun the test command. |

## Security Notes

* Never commit `.env` files containing real credentials.
* Never place API keys directly inside Python source code.
* Use `src/.env.example` as the template for required environment variables.
* The current prototype does not implement user authentication or authorization.

## Current Prototype Limitations

The prototype currently uses local CSV datasets and does not connect to live logistics systems.

It does not currently provide:

* Live GPS tracking
* Live traffic information
* Live port status feeds
* Live carrier APIs
* Production database storage
* Production authentication

These are potential future improvements.
