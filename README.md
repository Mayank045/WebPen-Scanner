🛡️ Web-Pen Scanner

<p align="center"> <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=24&duration=3000&pause=1000&color=38BDF8&center=true&vCenter=true&width=650&lines=Web+Security+Scanner;Recon+%7C+Crawling+%7C+Security+Checks;Built+with+Python+%2B+Flask" alt="Typing animation"> </p>

<p align="center"> <b>A lightweight web security assessment platform for authorized targets.</b> </p>

<p align="center"> <img src="https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square&logo=python&logoColor=white"> <img src="https://img.shields.io/badge/Flask-3.x-black?style=flat-square&logo=flask"> <img src="https://img.shields.io/badge/SQLite-Database-003B57?style=flat-square&logo=sqlite"> <img src="https://img.shields.io/badge/JavaScript-Vanilla-F7DF1E?style=flat-square&logo=javascript&logoColor=black"> </p>

🔎 About

Web-Pen Scanner is a browser-based web security scanner built with Python, Flask, SQLite, and vanilla JavaScript.

It performs controlled reconnaissance, web crawling, passive security analysis, and risk assessment through a modern cybersecurity dashboard.

Target
  ↓
Validation + SSRF Protection
  ↓
Reconnaissance
  ↓
Controlled Crawler
  ↓
Passive Security Checks
  ↓
Findings + Risk Score
  ↓
Dashboard

## 🧱 Architecture

```text
                    ┌──────────────────────┐
                    │      Browser         │
                    │   Web Dashboard      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Flask Web App     │
                    │      REST API        │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Scan Service      │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        ┌──────────┐    ┌──────────┐    ┌──────────────┐
        │  Recon   │    │ Crawler  │    │   Security   │
        │  Module  │    │  Module  │    │    Checks    │
        └────┬─────┘    └────┬─────┘    └──────┬───────┘
             │               │                 │
             └───────────────┼─────────────────┘
                             ▼
                    ┌──────────────────────┐
                    │ Findings + Risk      │
                    │       Engine         │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │       SQLite         │
                    └──────────────────────┘
```
---

## 🧰 Tech Stack

| Technology       | Purpose                      |
| ---------------- | ---------------------------- |
| 🐍 Python        | Core application and scanner |
| 🌶️ Flask        | Backend and REST API         |
| 🗄️ SQLite       | Scan/result persistence      |
| 🌐 HTML          | Dashboard structure          |
| 🎨 CSS           | Dashboard styling            |
| ⚡ JavaScript     | Frontend interactions        |
| 🔍 Requests      | HTTP communication           |
| 🍲 BeautifulSoup | HTML parsing                 |
| 🧪 Pytest        | Automated testing            |

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Web-Pen-Scanner.git
cd Web-Pen-Scanner
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the application

```bash
python run.py
```

Open:

```text
http://127.0.0.1:5000
```

---

## ⚡ Quick Demo

Once the application is running:

```text
┌──────────────────────────────────────┐
│        WEB-PEN SCANNER               │
│                                      │
│  Target URL                          │
│  ┌────────────────────────────────┐  │
│  │ https://authorized-target.com │  │
│  └────────────────────────────────┘  │
│                                      │
│          [ START SCAN → ]            │
└──────────────────────────────────────┘
```

The scanner then performs:

```text
[1] Target validation
        ↓
[2] Reconnaissance
        ↓
[3] Controlled crawling
        ↓
[4] Passive security analysis
        ↓
[5] Findings
        ↓
[6] Risk assessment
        ↓
[7] Dashboard results
```

---

## ⚖️ Responsible Use

**Only scan systems that you own or have explicit permission to test.**

Do not use this project against:

* systems you do not own
* websites without authorization
* internal infrastructure
* third-party services without permission

The author is not responsible for misuse of this software.

This project exists for:

> **Cybersecurity education, defensive research, authorized testing, and portfolio development.**


---

<p align="center">

### 🛡️ Built for learning. Designed for security.

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f172a,50:111827,100:38bdf8&height=120&section=footer" alt="Footer animation">

</p>
