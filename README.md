# 🔍 Exposure Engine

**Exposure Engine** is an asynchronous, evidence-based OSINT framework for public username enumeration across multiple platforms.

The project focuses on a simple principle:

> A successful HTTP response is not automatically proof that an account exists.

Instead of treating every `HTTP 200 OK` as a positive result, Exposure Engine uses platform-specific detection logic, structured evidence, confidence levels, and explicit result states.

It is being developed as a practical Python, OSINT, and cybersecurity learning project.

---

## ✨ Key Features

- **⚡ Asynchronous Scanning**  
  Platform checks run concurrently using `asyncio` and `aiohttp`.

- **🔁 Shared HTTP Session**  
  A single `aiohttp.ClientSession` is reused during a scan and safely managed through an async context manager.

- **🎯 Evidence-Based Detection**  
  Different platforms can use different detection strategies instead of relying on one generic HTTP rule.

- **🧩 Detector Registry**  
  Detector implementations are registered centrally, reducing direct coupling between the HTTP collector and platform-specific logic.

- **🧹 Input Normalization**  
  Usernames are cleaned and normalized before scanning, including removal of leading `@` and unnecessary whitespace.

- **🚦 Explicit Result States**  
  Results distinguish confirmed profiles, missing accounts, blocked requests, rate limits, inconclusive responses, and errors.

- **📊 Confidence Levels**  
  Evidence is classified as `HIGH`, `MEDIUM`, or `LOW` confidence.

- **🔁 Retry Logic**  
  Retryable HTTP failures use exponential backoff.

- **🖥️ Rich CLI Output**  
  Scan results are displayed with structured panels, status highlighting, metadata, and a final summary.

- **📦 JSON Reporting**  
  Every completed scan can be exported as a structured JSON report containing normalized evidence from all sources.

- **🧪 Unit and Integration Testing**  
  Local tests are separated from tests that depend on real external services.

---

## 🛠️ Supported Platforms

| Platform | Verification Method | Example Metadata |
| :--- | :--- | :--- |
| **GitHub** | REST API | Username, name, creation date, public repositories |
| **GitLab** | REST API | Username, name, available account metadata |
| **DockerHub** | REST API | Username existence |
| **Reddit** | JSON endpoint / HTTP state | Access state, blocking, availability |
| **Telegram** | Public HTML markers | Public profile-page evidence |
| **Hacker News** | Official public API | Username, karma, creation date, about |
| **DEV Community** | Public API | Username, name, GitHub username, location, website |

Platform behavior may change over time.

When a source does not provide enough evidence for a reliable conclusion, Exposure Engine returns `UNKNOWN` rather than forcing a positive or negative result.

---

## 🚦 Result Statuses

Exposure Engine uses explicit result states:

| Status | Meaning |
| :--- | :--- |
| `FOUND` | Positive evidence supports the existence of a public profile |
| `NOT_FOUND` | Explicit negative evidence supports that the profile does not exist |
| `BLOCKED` | The source refused or restricted the request |
| `RATE_LIMITED` | The source applied a request-rate restriction |
| `UNKNOWN` | Available evidence is insufficient for a reliable conclusion |
| `ERROR` | A network, configuration, parsing, or runtime failure occurred |

Core detection principle:

```text
No positive evidence ≠ NOT_FOUND
No negative evidence ≠ FOUND
```

Another important OSINT principle:

```text
Same username on multiple platforms
≠
same person
```

A `FOUND` result means that a public digital trace was found for that username on a specific source.

It does **not** mean that identities across different platforms have been confirmed to belong to the same person.

---

## 📊 Confidence Model

Evidence also includes a confidence level:

| Confidence | Meaning |
| :--- | :--- |
| `HIGH` | Strong source-specific evidence supports the classification |
| `MEDIUM` | The result is meaningful but affected by access restrictions or uncertainty |
| `LOW` | The result is incomplete, ambiguous, or based on an error condition |

Status and confidence are stored together in a standardized `Evidence` object.

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/Bathometi/exposure-engine.git
cd exposure-engine
```

### 2. Create a virtual environment

Linux / WSL:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run Exposure Engine

```bash
python check_username.py
```

The CLI will ask for a username:

```text
Введи username для пошуку: octocat
```

Usernames can also contain a leading `@`:

```text
@octocat
```

The normalizer converts the raw input into a standardized username before scanning.

---

## 🖥️ CLI Output

Exposure Engine displays a separate result panel for every source.

Example fields may include:

```text
Status
Confidence
HTTP
URL
Username
Name
Created At
Public Repos
GitHub Username
Location
Website
Karma
About
```

Only metadata actually returned by the source is displayed.

At the end of the scan, Exposure Engine generates a summary:

```text
FOUND
NOT_FOUND
RATE_LIMITED
BLOCKED
UNKNOWN
ERROR
```

---

## 📦 JSON Reports

Completed scans are stored as structured JSON reports inside:

```text
reports/
```

Example:

```text
reports/2026-08-15_10-21-11_username_ben.json
```

A report contains:

```text
scan metadata
raw input
normalized value
scan timestamp
result count
platform evidence
status
confidence
source-specific metadata
limitations
HTTP information
```

Example structure:

```json
{
  "scan": {
    "entity_type": "username",
    "raw_value": "example",
    "normalized_value": "example",
    "scanned_at_utc": "2026-08-15T10:21:11+00:00",
    "results_count": 7
  },
  "results": []
}
```

Generated reports are excluded from Git through `.gitignore`.

---

## 🧪 Testing

Exposure Engine currently separates local tests from external integration tests.

### Run the default local test suite

```bash
python -m pytest -q
```

Current local suite:

```text
37 passed
1 integration test deselected
```

These tests are designed to run without depending on a live external API.

### Run integration tests

```bash
python -m pytest -m integration -q
```

Current integration suite:

```text
1 passed
37 deselected
```

The integration test performs a real external API check.

### Current total

```text
38 tests
```

Test coverage includes:

```text
normalization
schema validation
platform detectors
detector registry
platform configuration
HTTP collector behavior
retry logic
exponential backoff
failure paths
async context management
JSON reporting
external integration
```

Mocks, fake HTTP sessions, and `monkeypatch` are used where appropriate to keep local tests deterministic.

---

## 🏗️ Architecture

Current high-level flow:

```text
Raw Username
     ↓
Normalizer
     ↓
Platform Configuration
     ↓
HTTPCollector
     ↓
Detector Registry
     ↓
Platform Detector
     ↓
Evidence
     ↓
┌───────────────┬───────────────┐
│               │               │
Rich CLI     JSON Report     Summary
```

### HTTP lifecycle

A scan uses one shared HTTP client:

```text
OPEN ClientSession
        ↓
Concurrent platform checks
        ↓
Retries when required
        ↓
Collect Evidence
        ↓
CLOSE ClientSession
```

The shared session is managed using an asynchronous context manager.

---

## 🧩 Detector Registry

The collector does not need to know every detector implementation directly.

Instead, platform configuration references a detector name:

```text
"devto"
"hackernews"
"telegram"
"status_code"
```

The Detector Registry maps that name to:

```text
detector implementation
+
expected response type
```

Example concept:

```text
"telegram"
    ↓
TelegramDetector
    ↓
text response

"devto"
    ↓
DevToDetector
    ↓
JSON response
```

This reduces coupling and makes future platform integrations easier to maintain.

---

## 🧠 Collector vs Detector

Exposure Engine keeps data collection and interpretation separate.

```text
Collector
→ obtains the response

Detector
→ decides what the response means
```

For example:

```text
HTTP 200
```

only tells us that the server returned a successful HTTP response.

It does **not** necessarily tell us that a requested user exists.

The detector evaluates source-specific evidence before assigning:

```text
FOUND
NOT_FOUND
BLOCKED
RATE_LIMITED
UNKNOWN
ERROR
```

---

## 🔁 Retry Strategy

Temporary network or server failures can be retried.

Retryable states include:

```text
429
500
502
503
504
```

Exposure Engine uses exponential backoff between attempts.

Conceptually:

```text
request
↓
failure

wait 2 seconds
↓
retry

wait 4 seconds
↓
retry

wait 8 seconds
↓
retry
```

If retryable server failures continue after the maximum number of retries, the result becomes:

```text
ERROR / LOW confidence
```

---

## 🔎 Detection Philosophy

Username enumeration has many edge cases.

Different platforms may:

- return `HTTP 200` for missing profiles;
- return `404` for an explicitly missing user;
- redirect to login or generic pages;
- return HTML instead of JSON;
- expose structured APIs;
- return empty lists;
- apply rate limits;
- block automated traffic;
- expose only users with certain types of public activity.

Because of this, Exposure Engine does not force every platform into one detection rule.

Examples:

```text
GitHub
→ REST API detection

GitLab
→ API response detection

Telegram
→ HTML marker detection

Hacker News
→ platform-specific API detector

DEV Community
→ platform-specific API detector
```

When evidence is insufficient, the engine prefers:

```text
UNKNOWN
```

over an unsupported assumption.

---

## 📁 Project Structure

```text
exposure-engine/
├── config/
│   └── platforms.py
│
├── core/
│   ├── collector.py
│   ├── detector_registry.py
│   ├── detectors.py
│   ├── normalizer.py
│   ├── reporting.py
│   └── schema.py
│
├── tests/
│   ├── test_collector.py
│   ├── test_detector_registry.py
│   ├── test_detectors.py
│   ├── test_normalizer.py
│   ├── test_platform_config.py
│   ├── test_reporting.py
│   ├── test_retry.py
│   └── test_schema.py
│
├── reports/
├── check_username.py
├── pytest.ini
├── requirements.txt
└── README.md
```

The architecture is expected to evolve as additional entity types and sources are introduced.

---

## ⚠️ Limitations

Exposure Engine only works with publicly accessible information and available public endpoints.

Platform APIs, HTML layouts, rate limits, anti-bot systems, and access policies may change without notice.

A detector that works today may require adjustment in the future.

A result of `UNKNOWN` is intentional when the available evidence is insufficient.

The project does not attempt to bypass:

```text
authentication
private profiles
platform access controls
anti-bot protections
```

Results should always be interpreted as source-specific evidence rather than automatic identity attribution.

---

## 🎯 Project Goals

Exposure Engine is being developed as a hands-on learning project focused on:

- Python;
- asynchronous programming;
- HTTP and API analysis;
- OSINT methodology;
- data normalization;
- evidence-based detection;
- confidence modeling;
- defensive error handling;
- retries and exponential backoff;
- automated testing;
- mocks and integration tests;
- modular software architecture;
- structured reporting.

The current development phase is focused on stabilizing the **USERNAME** engine.

Future development may include:

```text
more reliable username sources
↓
USERNAME v1 stabilization
↓
EMAIL entity support
↓
PHONE entity support
↓
additional public exposure signals
```

---

## ⚖️ Responsible Use

Exposure Engine is intended for:

- educational use;
- defensive security;
- legitimate OSINT research;
- analysis of publicly accessible information.

Use the project only in accordance with applicable laws, platform policies, and authorization requirements.

The project is not intended for unauthorized access, bypassing technical restrictions, or identity attribution based only on username similarity.

---

## 📌 Project Status

**Work in progress.**

Current state:

```text
7 username sources
Rich CLI
JSON reporting
Detector Registry
Shared aiohttp ClientSession
Retry + exponential backoff
37 local tests
1 integration test
38 tests total
```

Current development priorities:

```text
improve architecture
expand reliable test coverage
add carefully validated public sources
reduce false positives
stabilize USERNAME v1
```
