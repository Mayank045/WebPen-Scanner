# 🛡️ Web-Pen Scanner --- Run Test & Validation

```{=html}
<p align="center">
```
`<b>`{=html}End-to-end execution guide and validation record for Web-Pen
Scanner`</b>`{=html}
```{=html}
</p>
```
```{=html}
<p align="center">
```
`<img src="https://img.shields.io/badge/Test%20Version-v1.0-38BDF8?style=for-the-badge">`{=html}
`<img src="https://img.shields.io/badge/Platform-Windows%2011-0078D4?style=for-the-badge">`{=html}
`<img src="https://img.shields.io/badge/Python-3.13.x-3776AB?style=for-the-badge&logo=python&logoColor=white">`{=html}
`<img src="https://img.shields.io/badge/Flask-3.x-black?style=for-the-badge&logo=flask">`{=html}
```{=html}
</p>
```

------------------------------------------------------------------------

## 🎯 Purpose

This document demonstrates how to **install, start, validate, and run a
security scan** using Web-Pen Scanner.

The documented test was performed against **Pentest Ground**, an
intentionally vulnerable security-testing environment, using the target:

``` text
https://pentest-ground.com:81/
```

> ⚠️ **Authorized testing only:** Use Web-Pen Scanner only against
> systems you own, intentionally vulnerable labs, or systems for which
> you have explicit permission to test.

## 🧪 Test Environment

  -----------------------------------------------------------------------
  Component                           Configuration
  ----------------------------------- -----------------------------------
  Operating System                    Windows 11

  Python                              3.13.x

  Framework                           Flask 3.x

  Database                            SQLite

  Browser                             Google Chrome

  Scanner                             Web-Pen Scanner

  Test Target                         Pentest Ground --- Authorized
                                      Vulnerable Testing Environment

  Project Version                     v1.0

  Test Date                           16 October 2026
  -----------------------------------------------------------------------

## ⚙️ Prerequisites

-   Python 3.x
-   Git
-   A modern web browser
-   Project dependencies from `requirements.txt`
-   An authorized vulnerability-testing target

### Install dependencies

``` powershell
python -m pip install -r requirements.txt
```

### Create and activate a virtual environment

``` powershell
python -m venv .venv
.venv\Scripts\activate
```

## 🚀 1. Start Web-Pen Scanner

From the project root:

``` powershell
python run.py
```

A successful startup should expose the Flask development server locally,
for example:

``` text
http://127.0.0.1:5000
```

![Flask server startup](assets/screenshot-1.png)

## 🖥️ 2. Open the Dashboard

Open `http://127.0.0.1:5000` in your browser. The dashboard provides the
interface for starting scans, viewing scan history, reviewing crawl
results, inspecting security findings, and viewing severity information
and risk score.

![Web-Pen Scanner dashboard](assets/screenshot-2.png)

## ❤️ 3. Verify API Health

Open:

``` text
http://127.0.0.1:5000/api/health
```

Expected response:

``` json
{
  "service": "web-pen-scanner",
  "status": "ok"
}
```

![API health check](assets/screenshot-3.png)

**Result: ✅ PASS**

The API returned the expected `status: ok` response.

## 🎯 4. Configure the Scan Target

For this validation run, the authorized lab target was:

``` text
https://pentest-ground.com:81/
```

![Target configuration](assets/screenshot-4.png)

Click **Start Scan** to begin the assessment.

## 🔍 5. Scan Execution

The scanner processes the target through its security-assessment
pipeline:

``` text
Target
   │
   ▼
URL Validation + SSRF Protection
   │
   ▼
Reconnaissance
   │
   ▼
Controlled Web Crawler
   │
   ▼
Passive Security Checks
   │
   ▼
Findings + Risk Score
   │
   ▼
Dashboard Results
```

The scan collects reconnaissance information, discovers same-origin
pages within configured crawler limits, performs passive security
checks, and stores the resulting scan information.

## 📊 6. Scan Output

The documented test run produced a completed scan in the dashboard. The
recorded dashboard view shows:

-   **Total scans:** 1
-   **Pages crawled:** 10
-   **Findings:** 7
-   **Latest risk score:** 100

![Completed scan output](assets/screenshot-5.png)

> These values represent the documented test run shown in the supplied
> validation screenshots. Results can vary depending on the target and
> its current responses.

## 🔬 7. Scan Details

The scan-details view provides a deeper inspection of the assessment,
including target information and security findings.

![Scan details](assets/screenshot-6.png)

The details view can be used to review the evidence produced by the
scanner and understand why findings were generated.

## 🛡️ What the Current Version Tests

The current Web-Pen Scanner focuses primarily on **controlled
reconnaissance and passive security analysis**.

### Reconnaissance

-   Hostname
-   Public IP resolution
-   HTTP/HTTPS scheme
-   HTTP status code
-   Final URL after redirects
-   Response headers

### Controlled Crawling

-   Same-origin crawling
-   Relative URL normalization
-   Fragment removal
-   Duplicate prevention
-   Crawl depth limits
-   Page-count limits
-   HTML-only crawling
-   Redirect scope enforcement

### Passive Security Checks

-   Security headers
-   HTTPS/HSTS observations
-   Cookie security attributes
-   Conservative CORS observations
-   Server/version disclosure
-   Risk-score integration

## 🔐 Security Controls

Web-Pen Scanner includes safeguards intended to keep assessments
controlled and non-destructive:

-   SSRF protection
-   Private/loopback IP blocking
-   Redirect validation
-   Request timeouts
-   Response-size limits
-   Crawl depth and page limits
-   Same-origin restrictions
-   Safe frontend rendering
-   No automatic form submission

## ⚠️ Current Scope & Limitations

The current version should **not** be presented as a full active
vulnerability-exploitation scanner.

It does not currently perform active testing for:

-   SQL Injection
-   Cross-Site Scripting exploitation
-   Command Injection
-   Authentication bypass
-   IDOR
-   Remote Code Execution
-   Credential attacks
-   Destructive exploitation

Its current scope is **reconnaissance, controlled crawling, passive
security analysis, evidence collection, and risk scoring**.

## 🧾 Validation Checklist

  Test                           Expected Result                   Status
  ------------------------------ -------------------------------- --------
  Flask application startup      Local server starts                 ✅
  Dashboard access               Web interface loads                 ✅
  API health check               `status: ok` returned               ✅
  Authorized target submission   Target accepted                     ✅
  Reconnaissance                 Target information collected        ✅
  Web crawling                   Pages discovered within limits      ✅
  Passive security checks        Findings generated                  ✅
  Risk assessment                Risk score displayed                ✅
  Scan details                   Detailed results displayed          ✅

## 🛑 8. Stop the Application

After completing the scan and saving the required results, return to the
terminal running Flask and press:

``` text
Ctrl + C
```

This terminates the local development server.

## 📌 Test Conclusion

The documented validation confirms that the Web-Pen Scanner can be
launched locally, expose a working API, accept an authorized target,
execute its current scanning pipeline, and present reconnaissance,
crawl, passive security findings, and risk information through the
dashboard.

The test also demonstrates the project's current scope: **controlled and
non-destructive web security assessment rather than active
exploitation.**

------------------------------------------------------------------------

```{=html}
<p align="center">
```
`<b>`{=html}🛡️ Web-Pen
Scanner`</b>`{=html}`<br>`{=html}`<sub>`{=html}Built for learning •
Designed for authorized security testing`</sub>`{=html}
```{=html}
</p>
```
