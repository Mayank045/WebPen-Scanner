# 🛡️ Web-Pen Scanner

> **A web-based penetration testing and vulnerability assessment platform for authorized security testing.**

Web-Pen Scanner is a cybersecurity project designed to provide a browser-based interface for performing structured web application security assessments.

Instead of requiring the user to interact with multiple security tools through the terminal, Web-Pen Scanner aims to provide a centralized dashboard for configuring scans, monitoring their progress, analyzing findings, and generating security reports.

The project is being developed incrementally as both a **cybersecurity learning project** and a **portfolio project**.

---

## 🎯 Project Vision

The long-term vision of Web-Pen Scanner is to provide a modular security assessment platform capable of:

* 🔎 Reconnaissance
* 🕷️ Web crawling
* 🌐 Endpoint and parameter discovery
* 🔐 Security configuration analysis
* 🧪 Vulnerability detection
* 🧠 Risk and severity analysis
* 📊 Security scoring
* 📄 Automated reporting
* 🔧 Integration with established security tools

The application will provide a web dashboard while the actual scanning and analysis will be performed by the backend.

```text
                    Web Browser
                         │
                         │ HTTP / REST API
                         ▼
                ┌──────────────────┐
                │   Flask Backend  │
                └────────┬─────────┘
                         │
                         ▼
                   Scan Manager
                         │
             ┌───────────┼───────────┐
             ▼           ▼           ▼
           Recon       Crawler     Security
                                  Checks
             │           │           │
             └───────────┼───────────┘
                         ▼
                    Risk Engine
                         │
                         ▼
                      SQLite
                         │
                         ▼
                  Dashboard / Reports
```

---

## ⚠️ Legal & Ethical Use

Web-Pen Scanner is intended **only for authorized security testing**.

Use it against:

* Applications you own
* Local test environments
* CTF/lab environments
* Applications for which you have explicit permission to perform security testing

Do **not** use this project to scan systems without authorization.

The project is designed around defensive security assessment and should avoid destructive exploitation, credential theft, persistence, evasion, or unauthorized data access.

---

# 🧰 Technology Stack

## Frontend

| Technology | Purpose                                    |
| ---------- | ------------------------------------------ |
| HTML       | Dashboard structure                        |
| CSS        | Styling and responsive UI                  |
| JavaScript | Frontend interaction and API communication |

The frontend intentionally uses **vanilla HTML, CSS, and JavaScript** instead of a frontend framework.

This keeps the project approachable while providing a strong understanding of how web applications communicate with backend services.

## Backend

| Technology | Purpose                        |
| ---------- | ------------------------------ |
| Python     | Core programming language      |
| Flask      | Web server and REST API        |
| SQLite     | Persistent scan/result storage |

## Planned Security Tool Integrations

The project may eventually integrate tools such as:

* Nmap
* Nuclei
* FFUF

These will be treated as modular integrations rather than making Web-Pen Scanner simply a wrapper around external tools.

---

# 🏗️ Current Architecture

The project is currently being developed around a modular Flask architecture.

```text
Web-Pen-Scanner/
│
├── app/
│   ├── routes/
│   ├── scanner/
│   ├── services/
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── templates/
│
├── data/
│
├── reports/
│
├── tests/
│
├── configs/
│
├── docs/
│
├── updates.txt
├── requirements.txt
├── run.py
├── README.md
└── .gitignore
```

The exact structure will evolve as new modules are introduced.

---

# 🔄 How Web-Pen Scanner Works

A typical scan will eventually follow this workflow:

```text
1. User enters authorized target
              │
              ▼
2. Dashboard sends HTTP request
              │
              ▼
3. Flask validates the request
              │
              ▼
4. Scan is created
              │
              ▼
5. Scanner performs reconnaissance
              │
              ▼
6. Web application is crawled
              │
              ▼
7. Security checks are performed
              │
              ▼
8. Findings are normalized
              │
              ▼
9. Risk engine evaluates findings
              │
              ▼
10. Results stored in database
              │
              ▼
11. Dashboard displays results
              │
              ▼
12. Security report is generated
```

---

# 🔍 Planned Scanning Modules

## 1. Reconnaissance

The reconnaissance module will gather information about the target such as:

* DNS information
* IP resolution
* HTTP/HTTPS information
* Response headers
* Basic technology information
* Optional port information

---

## 2. Web Crawler

The crawler will discover the application's attack surface by identifying:

* Web pages
* Internal links
* Forms
* Input fields
* Query parameters
* JavaScript files
* Redirects

Example:

```text
Target
 │
 ├── /
 ├── /login
 ├── /products
 │     └── ?id=10
 ├── /contact
 └── /api
```

---

## 3. Security Checks

The scanner will gradually introduce modular security checks such as:

* Security header analysis
* Cookie security attributes
* HTTPS configuration
* TLS observations
* CORS configuration
* Information disclosure
* Exposed resources
* Potentially sensitive configuration files

Each finding should contain useful context rather than simply reporting that a check failed.

---

# 🧠 Risk Analysis

Findings will eventually be normalized into a common format.

Example:

```text
Finding:
Missing Content-Security-Policy

Severity:
Medium

Confidence:
High

Category:
Security Configuration

Evidence:
The response did not contain a Content-Security-Policy header.

Recommendation:
Consider implementing an appropriate Content Security Policy.
```

The project will eventually include a risk engine capable of categorizing findings and producing an overall security score.

---

# 🖥️ Web Dashboard

The dashboard is intended to become the primary interface for Web-Pen Scanner.

Planned sections include:

### Dashboard

* Scan statistics
* Recent scans
* Security score
* Finding severity overview

### New Scan

* Target URL
* Scan configuration
* Available modules
* Start scan button

### Scan Progress

* Current scan stage
* Progress percentage
* Completed tasks
* Current operation

### Scan Results

* Findings
* Severity
* Confidence
* Evidence
* Recommendations
* Affected endpoints

### Reports

* HTML reports
* JSON reports
* Future report formats

---

# ⚙️ Background Scanning

Long-running scans should not block the normal Flask HTTP request.

The intended architecture is:

```text
Browser
   │
   │ POST /api/scans
   ▼
Flask
   │
   ├── Create scan
   │
   └── Start scan job
            │
            ▼
         Scanner
            │
            ▼
         Database
```

The API can immediately return a scan identifier while the scanner continues processing.

The frontend can then retrieve the scan's status and results.

More advanced real-time communication may be introduced later if required.

---

# 🛣️ Development Roadmap

Web-Pen Scanner will be developed incrementally.

### Phase 0 — Foundation

* Project structure
* Flask application
* Basic frontend
* Basic API
* SQLite setup
* Configuration
* Logging
* Development changelog

### Phase 1 — First Working Scan

Build the first complete flow:

```text
Browser
   ↓
Target URL
   ↓
Flask API
   ↓
HTTP Request
   ↓
Response Analysis
   ↓
Dashboard Result
```

### Phase 2 — Reconnaissance

Add:

* DNS
* IP resolution
* HTTP headers
* Basic technology detection

### Phase 3 — Web Crawler

Add:

* URL discovery
* Forms
* Parameters
* JavaScript discovery

### Phase 4 — Security Checks

Add modular checks for:

* Headers
* Cookies
* HTTPS
* TLS
* CORS
* Information disclosure
* Safe exposure checks

### Phase 5 — Background Scanning

Introduce:

* Scan jobs
* Scan states
* Progress tracking
* Cancellation/error handling

### Phase 6 — Database Expansion

Store:

* Targets
* Scans
* Endpoints
* Findings
* Scan status
* Timestamps

### Phase 7 — Tool Integrations

Introduce optional integrations with:

* Nmap
* Nuclei
* FFUF

### Phase 8 — Risk Engine

Add:

* Severity
* Confidence
* Categories
* Recommendations
* Security score

### Phase 9 — Reporting

Generate:

* HTML reports
* JSON reports
* Additional formats where useful

### Phase 10 — Final Polish

Improve:

* Dashboard UI
* Testing
* Error handling
* Documentation
* Deployment
* GitHub presentation

---

# 📈 Project Development Log

A lightweight development log is maintained in:

```text
updates.txt
```

Each meaningful implementation change is recorded as a concise one-line entry.

Example:

```text
[2026-09-06] - Initialized the Flask backend, frontend dashboard, SQLite database, and project structure.
```

This file is maintained throughout development to provide a simple history of the project's progress.

---

# 🧪 Testing

Testing will be introduced progressively as functionality is developed.

The project should eventually include tests for:

* URL validation
* HTTP handling
* Scanner modules
* API endpoints
* Database operations
* Vulnerability checks
* Risk classification

Testing should use intentionally vulnerable or controlled environments rather than unauthorized public systems.

---

# 🚀 Running the Project

Create and activate a Python virtual environment:

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the Flask application:

```bash
python run.py
```

Then open the local address displayed by Flask in your browser.

---

# 📌 Current Status

**Project Stage:** Foundation / Early Development

Currently the project is establishing:

* Flask backend
* Web frontend
* API structure
* SQLite database
* Scanner architecture
* Development workflow

The actual security scanning capabilities will be implemented incrementally in later phases.

---

# 🎓 Project Goals

Web-Pen Scanner is being developed to strengthen practical understanding of:

* Web application architecture
* HTTP communication
* REST APIs
* Flask
* HTML/CSS/JavaScript
* Python networking
* Web crawling
* Vulnerability assessment
* Security misconfiguration detection
* Databases
* Background jobs
* Risk analysis
* Security reporting
* Secure software development

The project is intended to demonstrate both **software development skills and cybersecurity knowledge**.

---

## 👨‍💻 Project

**Web-Pen Scanner**

A learning-focused web penetration testing and vulnerability assessment platform.

> Build it. Understand it. Secure it.
