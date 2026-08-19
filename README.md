# 🔍 Exposure Engine

**Exposure Engine** is an asynchronous, evidence-based OSINT framework for public username enumeration across multiple platforms.

The project is built around one core principle:

> A successful HTTP response is not automatically proof that an account exists.

Instead of treating every `HTTP 200 OK` as a positive result, Exposure Engine uses source-specific detection logic, structured evidence, confidence levels, explicit result states, and pre-flight input validation.

The project is being developed as a practical Python, OSINT, and cybersecurity learning project.

---

## ✨ Key Features

- Asynchronous scanning with `asyncio` and `aiohttp`
- Shared HTTP session for concurrent platform checks
- Input normalization before scanning
- Pre-flight username validation before HTTP requests
- Source-specific detectors
- Detector Registry for decoupling configuration from detector implementations
- Explicit result states:
  - `FOUND`
  - `NOT_FOUND`
  - `BLOCKED`
  - `RATE_LIMITED`
  - `UNKNOWN`
  - `ERROR`
- Confidence levels:
  - `HIGH`
  - `MEDIUM`
  - `LOW`
- Retry logic with exponential backoff
- Rich CLI output
- Structured JSON reports
- Positive and negative regression matrix
- Unit and integration tests
- Failure-path testing with mocks, fake sessions, and `monkeypatch`

---

## 🛠️ Supported Platforms

Exposure Engine currently supports **12 public username sources**.

| Platform | Detection Strategy | Example Evidence |
| :--- | :--- | :--- |
| **GitHub** | Public API / HTTP + JSON | Username, name, creation date, repositories |
| **GitLab** | Public API / JSON list | Username, name |
| **DockerHub** | Public API / HTTP + JSON | Username existence |
| **Reddit** | Public JSON endpoint / HTTP state | Availability or access restriction |
| **Telegram** | Public HTML markers | Public profile-page evidence |
| **Hacker News** | Public API | Username, karma, creation date, about |
| **DEV Community** | Public API | Username, name, GitHub username, location, website |
| **Codeberg** | Public API | Username, name, creation date, profile metadata |
| **Keybase** | Public API + application-level status | Username, name, location, creation date |
| **Lichess** | Public API | Username existence |
| **Hugging Face** | Public API + user markers | Username, name, creation date, profile information |
| **Chess.com** | Public API + player markers | Username, name, title, creation date, profile metadata |

Platform behavior can change over time.

When a source does not provide enough evidence for a reliable conclusion, Exposure Engine returns `UNKNOWN` rather than forcing a positive or negative result.

---

## 🚦 Result Statuses

| Status | Meaning |
| :--- | :--- |
| `FOUND` | Positive source-specific evidence supports the existence of a public profile |
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

A `FOUND` result means that a public digital trace for that username was found on that specific source.

It does **not** confirm that profiles with the same username belong to the same person.

---

## 📊 Confidence Model

Each result also contains a confidence level.

| Confidence | Meaning |
| :--- | :--- |
| `HIGH` | Strong source-specific evidence supports the classification |
| `MEDIUM` | The result is meaningful but affected by access restrictions or uncertainty |
| `LOW` | The result is incomplete, ambiguous, or based on an error condition |

Status and confidence are stored together inside a standardized `Evidence` object.

---

## 🧹 Normalization and Validation

Username processing happens before network activity.

```text
Raw input
    ↓
Normalizer
    ↓
UsernameValidator
    ↓
Valid?
 ┌──┴──┐
No    Yes
↓      ↓
STOP   Scan platforms
```

The normalizer:

- removes surrounding whitespace;
- removes leading `@` characters;
- converts usernames to lowercase.

The global username validator rejects obvious invalid input such as:

- empty usernames;
- usernames containing whitespace;
- excessively long usernames.

Platform-specific username rules remain separate from the global validator.

Invalid input is rejected **before the HTTP collector or report generator is started**.

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

For normal use:

```bash
python -m pip install -r requirements.txt
```

For development and testing:

```bash
python -m pip install -r requirements-dev.txt
```

### 4. Run Exposure Engine

```bash
python check_username.py
```

The CLI will ask for a username:

```text
Введи username для пошуку: octocat
```

A leading `@` is also accepted:

```text
@octocat
```

---

## 🖥️ CLI Output

Exposure Engine displays a separate result panel for every configured source.

Depending on the source, fields may include:

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

Only metadata actually available from the source is displayed.

At the end of a completed scan, the CLI generates a summary for:

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

Each report contains:

- scan metadata;
- raw and normalized input;
- UTC scan timestamp;
- result count;
- source-specific evidence;
- status and confidence;
- collected metadata;
- HTTP information;
- detector limitations.

Example structure:

```json
{
  "scan": {
    "entity_type": "username",
    "raw_value": "example",
    "normalized_value": "example",
    "scanned_at_utc": "2026-08-17T12:00:00+00:00",
    "results_count": 12
  },
  "results": []
}
```

Generated reports are excluded from Git through `.gitignore`.

---

## 🧪 Testing

The default test suite excludes tests that depend on live external services.

Run local tests:

```bash
python -m pytest -q
```

Current local suite:

```text
97 passed
1 integration test deselected
```

Run integration tests explicitly:

```bash
python -m pytest -m integration -q
```

Current test coverage includes:

- schema tests;
- normalization tests;
- username validation tests;
- detector tests;
- detector registry tests;
- platform configuration tests;
- HTTP collector tests;
- retry and exponential-backoff tests;
- failure-path tests;
- async context-manager tests;
- CLI formatting tests;
- CLI pre-flight validation tests;
- JSON reporting tests;
- positive and negative regression matrices;
- external integration testing.

Mocks, fake HTTP sessions, and `monkeypatch` are used where appropriate so the default test suite remains deterministic and does not depend on live APIs.

The regression matrix currently covers all **12 configured platforms** with positive and negative scenarios.

---

## 🏗️ Architecture

High-level username flow:

```text
Raw Username
     ↓
Normalizer
     ↓
UsernameValidator
     ↓
Platform Configuration
     ↓
Shared HTTPCollector
     ↓
Detector Registry
     ↓
Platform Detector
     ↓
Evidence
     ↓
┌─────────────┬─────────────┐
│             │             │
Rich CLI   JSON Report   Summary
```

### HTTP lifecycle

```text
OPEN shared aiohttp.ClientSession
            ↓
Concurrent platform checks
            ↓
Retry temporary failures
            ↓
Collect Evidence
            ↓
CLOSE ClientSession
```

One shared `aiohttp.ClientSession` is reused for a complete scan.

---

## 🧩 Detector Registry

Platform configuration references a detector by name.

Example:

```text
HuggingFace
     ↓
"huggingface"
     ↓
Detector Registry
     ↓
HuggingFaceDetector
     ↓
JSON response
```

The collector therefore does not need platform-specific `if/elif` branches for every new source.

This keeps HTTP collection separate from response interpretation and reduces coupling between components.

---

## 🧠 Collector vs Detector

Exposure Engine separates **collection** from **interpretation**.

```text
Collector
→ obtains the HTTP response

Detector
→ decides what the response means
```

For example:

```text
HTTP 200
```

only tells us that the server returned a successful HTTP response.

It does not necessarily prove that the requested account exists.

A platform detector evaluates the actual source-specific evidence before assigning a status and confidence level.

---

## 🔁 Retry Strategy

Temporary HTTP failures can be retried.

Retryable states currently include:

```text
429
500
502
503
504
```

Retries use exponential backoff:

```text
request
↓
temporary failure
↓
wait
↓
retry
```

Persistent retryable server failures eventually produce:

```text
ERROR / LOW confidence
```

---

## 🔎 Detection Philosophy

Username enumeration contains many edge cases.

Different platforms may:

- return `HTTP 200` for a missing account;
- return `404` for an explicitly missing account;
- return an empty JSON list;
- return an application-level status inside `HTTP 200`;
- return HTML rather than JSON;
- expose only accounts with particular public activity;
- rate-limit requests;
- block automated traffic.

Because of this, Exposure Engine does not force every source into one generic detection rule.

When available evidence is insufficient, the engine prefers:

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
│   ├── schema.py
│   └── validators.py
│
├── tests/
│   ├── test_cli_formatting.py
│   ├── test_cli_validation.py
│   ├── test_collector.py
│   ├── test_detector_registry.py
│   ├── test_detectors.py
│   ├── test_normalizer.py
│   ├── test_platform_config.py
│   ├── test_regression_matrix.py
│   ├── test_reporting.py
│   ├── test_retry.py
│   ├── test_schema.py
│   └── test_username_validator.py
│
├── reports/              # generated locally, ignored by Git
├── check_username.py
├── pytest.ini
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

---

## ⚠️ Limitations

Exposure Engine works only with publicly accessible information and available public endpoints.

Platform APIs, HTML layouts, rate limits, anti-bot systems, and access policies may change.

A detector that works today may require adjustment in the future.

The project does not attempt to bypass:

```text
authentication
private profiles
platform access controls
anti-bot protections
```

Results should be interpreted as **source-specific evidence**, not automatic identity attribution.

---

## 🎯 Roadmap

The current development phase is focused on stabilizing the **USERNAME** engine.

```text
carefully validated username sources
        ↓
USERNAME v1 stabilization
        ↓
EMAIL entity support
        ↓
PHONE entity support
        ↓
additional lawful public exposure signals
```

The goal is not to maximize the number of supported websites.

The priority is reliable detection, understandable evidence, low false-positive risk, and maintainable architecture.

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

## 📌 Current Status

**Work in progress — USERNAME engine stabilization.**

Current state:

```text
12 username sources
105 local tests
1 integration test
24 regression scenarios
Input normalization
Username pre-flight validation
Shared aiohttp ClientSession
Detector Registry
Source-specific detectors
Retry + exponential backoff
Rich CLI
JSON reporting
```
