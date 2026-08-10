# 🔍 Exposure Engine

**Exposure Engine** is an asynchronous, evidence-based OSINT framework for username normalization and public-profile enumeration across multiple platforms.

Unlike simple username checkers that rely only on `HTTP 200 OK`, Exposure Engine uses platform-specific detection rules to distinguish confirmed profiles, missing accounts, blocked requests, rate limits, and inconclusive responses.

---

## ✨ Key Features

- **⚡ Async Architecture** — concurrent platform checks using `aiohttp` and `asyncio`.
- **🎯 Evidence-Based Detection** — platform-specific verification instead of treating every `HTTP 200` as a valid profile.
- **🧹 Input Normalization** — centralized username cleanup, including removal of leading `@` and unnecessary whitespace.
- **🛡️ Explicit Status Model** — separates confirmed results from blocked, rate-limited, unknown, and error states.
- **🧩 Modular Design** — normalization, collection, detection, configuration, and evidence handling are separated into independent components.
- **📦 Structured Evidence** — each platform check returns standardized information about the source, status, confidence, URL, and available metadata.

---

## 🛠️ Supported Platforms

| Platform | Verification Method | Details |
| :--- | :--- | :--- |
| **GitHub** | REST API / HTTP status | Profile name, creation date, public repositories |
| **GitLab** | REST API / HTTP status | Name, username, account creation data |
| **DockerHub** | REST API / HTTP status | Username existence verification |
| **Reddit** | JSON endpoint | User existence and access-state verification |
| **Telegram** | HTML detection | Public profile-page verification |

Platform behavior may change over time. Exposure Engine therefore treats ambiguous responses as `UNKNOWN` instead of automatically reporting a false positive.

---

## 🚦 Result Statuses

Exposure Engine uses explicit result states:

| Status | Meaning |
| :--- | :--- |
| `FOUND` | Positive evidence confirms that the profile exists |
| `NOT_FOUND` | Explicit evidence confirms that the profile does not exist |
| `BLOCKED` | The platform refused or restricted the request |
| `RATE_LIMITED` | Too many requests were sent to the platform |
| `UNKNOWN` | The response does not provide enough evidence |
| `ERROR` | A network, parsing, configuration, or runtime error occurred |

The main principle is:

```text
No positive evidence ≠ NOT_FOUND
No negative evidence ≠ FOUND
```

When the result cannot be confirmed reliably, the engine returns `UNKNOWN`.

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
python3 -m venv .venv
source .venv/bin/activate
```

If the repository is stored under `/mnt/c/` in WSL and creating the environment there causes problems, use a Linux-side environment instead:

```bash
mkdir -p ~/.venvs
python3 -m venv ~/.venvs/exposure-engine
source ~/.venvs/exposure-engine/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run a username scan

```bash
python check_username.py "@octocat"
```

You can also provide a username without `@`:

```bash
python check_username.py octocat
```

The normalizer converts both forms to the same normalized username before scanning.

---

## 🧪 Run Tests

```bash
pytest
```

The test suite is intended to verify normalization, collectors, detectors, and platform-specific result handling.

---

## 🏗️ Architecture Design

```text
[Input Raw Username]
          |
          v
     [Normalizer]
          |
          |  Cleaned Username
          v
   [Platform Config]
          |
          |  URL + Detection Rules
          v
   [HTTP Collector]
          |
          |  Async HTTP Response
          v
      [Detectors]
          |
          |  Status / HTML / JSON Analysis
          v
       [Evidence]
          |
          v
 [Standardized Result]
```

### Processing Flow

```text
Raw Input
   ↓
Normalize Username
   ↓
Load Platform Configuration
   ↓
Send Requests Concurrently
   ↓
Apply Platform-Specific Detector
   ↓
Generate Evidence
   ↓
Return FOUND / NOT_FOUND / BLOCKED /
RATE_LIMITED / UNKNOWN / ERROR
```

The collector is responsible for retrieving data.

The detector is responsible for interpreting that data.

This separation prevents a generic HTTP response from being incorrectly treated as proof that an account exists.

---

## 📁 Project Structure

```text
exposure-engine/
├── config/
│   └── platforms.py
│
├── core/
│   ├── collector.py
│   ├── detectors.py
│   ├── normalizer.py
│   └── schema.py
│
├── check_username.py
├── requirements.txt
├── README.md
└── tests/
```

The exact structure may evolve as new collectors, detectors, and entity types are added.

---

## 🔎 Detection Philosophy

Username enumeration contains many edge cases.

Some platforms:

- return `HTTP 200` for missing profiles;
- redirect requests to login pages;
- return JavaScript or generic splash pages;
- apply rate limits;
- block automated requests;
- expose structured JSON APIs;
- require HTML-specific verification.

Because of this, Exposure Engine does not use one universal rule for every platform.

Instead, each platform can use its own verification strategy.

Examples:

```text
GitHub
→ API / HTTP status detection

GitLab
→ API response detection

Reddit
→ JSON endpoint detection

Telegram
→ HTML marker detection

DockerHub
→ API / HTTP status detection
```

This makes the result more reliable and easier to debug.

---

## ⚠️ Limitations

Exposure Engine only analyzes publicly accessible information.

Platform layouts, APIs, anti-bot systems, authentication requirements, and rate limits can change without notice. A detector that works today may require adjustment in the future.

A result of `UNKNOWN` is intentional when the available evidence is insufficient to classify a profile reliably.

The project does not attempt to bypass authentication systems or platform access controls.

---

## 🎯 Project Goals

Exposure Engine is being developed as a practical OSINT and cybersecurity learning project focused on:

- asynchronous Python;
- HTTP and API analysis;
- normalization;
- evidence-based detection;
- defensive error handling;
- structured OSINT results;
- modular software architecture;
- testing platform edge cases.

Future development may include additional public platforms, richer metadata extraction, CLI improvements, export formats, and support for additional entity types.

---

## ⚖️ Responsible Use

This project is intended for educational, defensive security, and legitimate OSINT research purposes.

Use it only with publicly accessible information and in accordance with applicable laws and platform terms.

---

## 📌 Status

**Work in progress.**

Current development is focused on improving platform-specific detection accuracy, reducing false positives, expanding test coverage, and adding reliable public-platform integrations.
