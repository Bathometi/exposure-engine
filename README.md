# 🔍 Exposure Engine

**Exposure Engine** is an asynchronous, evidence-based OSINT framework for analyzing public username and email exposure across multiple sources.

The project is built around one core principle:

> A successful HTTP response is not automatically proof that an account exists.

Instead of treating every `HTTP 200 OK` as a positive result, Exposure Engine uses source-specific detection logic, structured evidence, confidence levels, explicit result states, and pre-flight input validation.

The project is being developed as a practical Python, OSINT, and cybersecurity learning project.

---

## ✨ Key Features

- Asynchronous scanning with `asyncio` and `aiohttp`
- Shared HTTP session for concurrent platform checks
- Username and email normalization before scanning
- Pre-flight username and email validation before HTTP requests
- Email identifier transforms for source-specific lookups
- Email-domain intelligence via MX, SPF, and DMARC
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

## 🛠️ Supported Username Platforms

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

## ✉️ Supported Email Sources

Exposure Engine currently supports **3 public email sources** plus domain-level DNS enrichment.

| Source | Detection Strategy | Example Evidence |
| :--- | :--- | :--- |
| **Gravatar** | Public profile API using normalized email hash | Public profile, name, avatar, location, profile metadata |
| **HIBP** | Authorized Have I Been Pwned API lookup | Publicly reported breach names and breach count |
| **GitHub Commits** | Public GitHub Commit Search using exact `author-email:<email>` query | Commit count, linked GitHub users, repositories |

### DNS Intelligence

Email scans also collect domain-level mail infrastructure context:

- MX records
- SPF record
- DMARC record

DNS intelligence describes the **email domain**, not the individual mailbox.

For example, MX, SPF, and DMARC results for `user@gmail.com` describe `gmail.com`.

Important OSINT interpretation:

```text
GitHub Commits FOUND
≠
confirmed identity or mailbox ownership
```

A positive GitHub Commit result means that public GitHub commit metadata was returned for the exact author-email query.

A linked GitHub account is strong public association evidence, but should not be treated as automatic identity confirmation.

HIBP access requires an appropriate API key. A `404` means that the API returned no matching breach records for that query; it does not prove that the address has never appeared in a breach.

---

## 🚦 Result Statuses

| Status | Meaning |
| :--- | :--- |
| `FOUND` | Positive source-specific evidence supports a public trace for the requested entity |
| `NOT_FOUND` | Explicit negative evidence indicates that the source returned no matching trace |
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

A `FOUND` result means that source-specific public evidence was found for the requested username or email.

It does **not** automatically confirm identity, account ownership, or that matching traces across different sources belong to the same person.

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

Username and email processing happens before network activity.

```text
Raw input
    ↓
Normalizer
    ↓
Entity Validator
    ↓
Valid?
 ┌──┴──┐
No    Yes
↓      ↓
STOP   Scan sources
```

For usernames, the normalizer:

- removes surrounding whitespace;
- removes leading `@` characters;
- converts usernames to lowercase.

The global username validator rejects obvious invalid input such as:

- empty usernames;
- usernames containing whitespace;
- excessively long usernames.

For emails, the normalizer:

- removes surrounding whitespace;
- converts the address to lowercase.

The email validator rejects malformed input before any HTTP requests are made, including:

- empty values;
- whitespace inside the address;
- missing or multiple `@` characters;
- empty local or domain parts;
- invalid Unicode sequences.

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

#### Username scan

Interactive mode:

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

#### Email scan

Scan a single email address:

```bash
python check_email.py user@example.com
```

Multiple email addresses can also be scanned in one command:

```bash
python check_email.py first@example.com second@example.com
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
Breach Count
Breaches
Commit Count
Linked Users
Repositories
```

Only metadata actually available from the source is displayed.

Email scans also display a separate `DNS Intelligence` panel with MX, SPF, and DMARC information. These records describe the email domain and should not be interpreted as evidence that a specific mailbox exists.

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
- detector limitations;
- optional enrichments such as email-domain DNS intelligence;
- source-specific metadata such as GitHub commit count, linked users, and repositories.

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

Email reports may also include an `enrichments` object. DNS intelligence is stored under `enrichments.dns`, while GitHub Commit Footprint data is preserved inside the relevant `results[].details` object.

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
164 passed
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
- email validation and malformed-Unicode tests;
- email identifier tests;
- email DNS intelligence tests;
- GitHub email commit-footprint tests;
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

High-level entity flow:

```text
Raw Input
    ↓
Normalizer
    ↓
Entity Validator
    ↓
Source Configuration
    ↓
Shared HTTPCollector
    ↓
Detector Registry
    ↓
Source Detector
    ↓
Evidence
    ↓
┌─────────────┬─────────────┬─────────────┐
│             │             │             │
Rich CLI   JSON Report    Summary
```

### Username flow

Username scans use the configured public username platforms and source-specific detectors.

```text
Username
   ↓
Normalize + Validate
   ↓
12 Username Sources
   ↓
Concurrent HTTP Checks
   ↓
Evidence
```

### Email flow

Email scans combine source-specific HTTP evidence with separate domain-level DNS enrichment.

```text
Email
  ↓
Normalize + Validate
  ↓
3 Email Sources
  ├── Gravatar
  ├── HIBP
  └── GitHub Commits
  ↓
Concurrent HTTP Checks
  ↓
Evidence Results
  ↓
DNS Intelligence
(MX / SPF / DMARC)
  ↓
Rich CLI + JSON Report + Summary
```

GitHub Commit Footprint uses query parameters such as `author-email:<email>` and is interpreted by its own detector.

DNS enrichment is collected separately from source evidence and stored under `enrichments.dns` in email JSON reports.

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

A source-specific detector evaluates the available evidence before assigning a status and confidence level.

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

Public exposure analysis contains many edge cases.

Different sources may:

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
│   ├── dns_intelligence.py
│   ├── identifiers.py
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
│   ├── test_email_cli_validation.py
│   ├── test_email_dns.py
│   ├── test_email_identifier.py
│   ├── test_email_validator.py
│   ├── test_normalizer.py
│   ├── test_platform_config.py
│   ├── test_regression_matrix.py
│   ├── test_reporting.py
│   ├── test_retry.py
│   ├── test_schema.py
│   └── test_username_validator.py
│
├── reports/              # generated locally, ignored by Git
├── .gitignore
├── check_email.py
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

The **USERNAME v1** engine is stable. Current development is focused on expanding and stabilizing **EMAIL** exposure analysis.

```text
USERNAME v1 stable
        ↓
EMAIL analysis
        ↓
additional validated email exposure signals
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

The project is not intended for unauthorized access, bypassing technical restrictions, or identity attribution based only on username similarity or a single matching public trace.

---

## 📌 Current Status

**Work in progress — EMAIL exposure analysis and framework expansion.**

Current state:

```text
12 stable username sources
3 email sources
DNS intelligence: MX / SPF / DMARC
Email normalization + pre-flight validation
GitHub Commit Footprint
Gravatar public profile lookup
HIBP API integration
Batch email scanning
Shared aiohttp ClientSession
Detector Registry
Source-specific detectors
Query-parameter support
Retry + exponential backoff
Rich CLI
Structured JSON reporting
164 local tests passing
1 integration test deselected by default
```
