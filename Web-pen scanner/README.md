# Web-Pen Scanner

A lightweight web security scanner built with Flask, SQLite, and vanilla JavaScript. This project is intentionally beginner-friendly and focuses on safe, educational checks rather than destructive or unauthorized exploitation.

## Features

- Enter a target URL in a simple dashboard
- Validate and normalize the URL
- Create and track scans in SQLite
- Run safe reconnaissance checks against the target
- Inspect response headers, links, forms, and common findings
- View results with a risk score and summary

## Quick start

1. Create and activate a virtual environment.
2. Install dependencies:

   python -m pip install -r requirements.txt

3. Run the app:

   python run.py

4. Open http://127.0.0.1:5000 in your browser.

## Important usage note

Only scan systems you own or have explicit authorization to test. This project is for defensive security learning and evidence gathering.
