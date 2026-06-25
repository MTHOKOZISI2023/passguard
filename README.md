# PassGuard - Context-Aware Password Strength Analyzer

PassGuard is an academic cybersecurity prototype developed as part of the diploma thesis **"Design and Evaluation of a Context-Aware Password Strength Analyzer."** The project demonstrates how a password strength tool can combine immediate browser-side feedback with deeper backend analysis such as entropy estimation, crack-time modelling, and privacy-preserving breach detection.

## Academic Context

- Institution: University of Information Technology and Management in Rzeszow
- Faculty: Faculty of Information Technology
- Field of study: Information Technology
- Specialty: Computer Science
- Thesis type: Diploma thesis at first-cycle studies
- Author: Mthokozisi Moyo
- Supervisor: prof. UITM dr inz. Atsuo Murata
- Year: 2026

## Project Overview

Traditional password strength meters often focus only on length and character diversity. This can give users an incomplete view of password risk because a structurally complex password may still be unsafe if it has appeared in previous data breaches.

PassGuard addresses this problem by combining:

- Real-time structural password analysis in the browser.
- A visual score, strength meter, and per-rule feedback indicators.
- Backend-based entropy and estimated crack-time calculation.
- Breach database checking using the HaveIBeenPwned k-anonymity protocol.
- Actionable improvement tips for users.

The prototype is designed around usability, privacy, and transparent feedback. Local checks run instantly in the browser, while backend checks provide deeper analysis only when requested.

## Thesis Objectives

The project supports the following thesis objectives:

- Design a full-stack password strength analyzer using a zero-dependency HTML/CSS/JavaScript frontend and a Python FastAPI backend.
- Implement real-time six-rule structural evaluation on every keystroke.
- Implement backend analysis for rule verification, Shannon entropy, crack-time estimation, and breach detection.
- Use the HaveIBeenPwned k-anonymity protocol so the full password is never sent to an external breach database.
- Provide clear visual feedback through score labels, rule indicators, status panels, and improvement tips.
- Evaluate the system against common weak, breached, and strong password examples.

## Features

- Six-rule local evaluation:
  - Minimum 8 characters
  - Minimum 12 characters
  - Uppercase letter
  - Lowercase letter
  - Number
  - Symbol
- Animated strength meter and circular score display.
- Password visibility toggle.
- Backend connection status indicator.
- Backend analysis panel for breach status, entropy, crack time, and tips.
- Responsive single-page interface.

## System Architecture

PassGuard follows a two-tier client-server architecture:

```text
passguard/
+-- index.html
+-- backend/
    +-- __init__.py
    +-- main.py
    +-- requirements.txt
```

The current frontend is a self-contained HTML file. It includes the markup, styling, and JavaScript needed for the user interface and local password analysis.

The FastAPI backend provides:

- `GET /health` for server availability checks.
- `POST /analyze` for password analysis requests.

The frontend sends password analysis requests to:

```text
http://localhost:8000/analyze
```

## GitHub Pages Demo vs. Local Backend

The GitHub Pages version runs the frontend only:

```text
https://mthokozisi2023.github.io/passguard/
```

GitHub Pages cannot run Python, so the backend analysis will not work from the hosted page by itself. This is expected. To use the full system, run the FastAPI backend locally and open the cloned `index.html` file from the same computer.

The frontend avoids automatically contacting `localhost` when it is hosted on GitHub Pages, so the browser should not show a permission prompt for local-device access.

## Frontend Behaviour

The frontend contains three main JavaScript functions:

- `analyzeLocal()` checks the six password rules in real time and updates the score, label, meter, circular ring, and rule indicators.
- `analyzeBackend()` sends the password to the backend for entropy, crack-time, breach, and tip analysis.
- `checkServer()` periodically checks whether the backend server is available.

The local analysis does not require a server and can run by opening `index.html` directly in a modern browser.

## Backend Behaviour

The backend described in the thesis uses Python FastAPI. Its `/analyze` endpoint is designed to:

- Re-check the same structural rules server-side.
- Calculate Shannon entropy using `H = L * log2(A)`.
- Estimate crack time using a GPU-calibrated attack model.
- Check HaveIBeenPwned by sending only the first five characters of the SHA-1 password hash.
- Return a JSON response containing score, label, rule results, entropy, crack time, breach status, and improvement tips.

Expected response shape:

```json
{
  "score": 83,
  "label": "Good",
  "rules": {
    "length_8": true,
    "length_12": false,
    "uppercase": true,
    "lowercase": true,
    "digits": true,
    "symbols": true
  },
  "entropy": 52.4,
  "crack_time": "3k years",
  "breached": false,
  "tips": ["12+ chars is much stronger"]
}
```

## Local Setup on Windows

Clone the repository:

```bash
git clone https://github.com/MTHOKOZISI2023/passguard.git
cd passguard
```

Create and activate a virtual environment:

```bash
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use the Python executable inside the virtual environment directly:

```bash
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

If activation works, install the backend dependencies and start the server:

```bash
pip install -r backend\requirements.txt
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Then open `index.html` locally in a browser. The status line should change to:

```text
backend connected - localhost:8000
```

## Running the Frontend Only

Open the frontend file directly in a browser:

```text
index.html
```

The local strength meter will work immediately, even without Python. Backend-powered analysis requires the FastAPI server to be running at `http://localhost:8000`.

## Running the Backend

The backend development workflow is:

```bash
pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

FastAPI documentation should then be available at:

```text
http://127.0.0.1:8000/docs
```

## Evaluation Summary

The thesis evaluates PassGuard using representative password cases:

- A weak common password shows low structural strength and breach exposure.
- A structurally stronger but breached password demonstrates why structural checks alone are insufficient.
- A strong password using length and multiple character classes receives a high score and no known breach match.

This supports the central thesis argument: a meaningful password strength analyzer should consider both structural complexity and real-world breach exposure.

## Privacy and Ethical Design

PassGuard is designed around password handling safety:

- Real-time local analysis runs only in the browser.
- The backend processes passwords in memory and does not store them.
- The breach lookup uses k-anonymity, sending only a five-character SHA-1 hash prefix to HaveIBeenPwned.
- The full password is not sent to any external breach database.

## Limitations

The current thesis prototype acknowledges several limitations:

- The entropy model assumes uniformly random character selection.
- Crack-time estimates depend on a fixed attack-speed assumption.
- Dedicated personal-information context detection is not yet implemented.
- The frontend currently uses a hardcoded backend URL.
- No formal user study has been conducted yet.

## Future Work

Potential extensions include:

- Machine-learning-based guessing resistance estimation.
- Personal context detection using optional user-provided fields such as name, date of birth, or email prefix.
- Runtime backend URL configuration.
- Browser extension or password manager integration.
- Empirical usability testing with real users.

## References

This project is grounded in password security and usability research, including work on password strength meters, password cracking, k-anonymity breach checking, and user feedback systems. The full bibliography is included in the thesis document.
