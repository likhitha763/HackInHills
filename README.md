# SealedBid: Secure Adversarial AI Safety Testing Infrastructure

SealedBid is an isolated, multi-tenant evaluation mesh specifically designed for **Hack In Hills '26 - Problem Statement 04**.

It solves the challenge of enabling adversarial **Red Teams**, defensive **Blue Teams**, and target **Client LLMs** to execute simultaneous tests without cross-tenant side-channel contamination, prompt leakage, or rule exposure.

---

## Architecture & Security Verticals

```
+-------------------------------------------------------------------------+
|                       Zero-Trust Secure Broker                          |
|                   (FastAPI / Micro-Segmented Mesh)                      |
+-------------------+-----------------+-----------------+-----------------+
                    |                 |                 |
                    v                 v                 v
            +---------------+ +---------------+ +---------------+
            |    RED TEAM   | |   BLUE TEAM   | | MODEL SANDBOX |
            |  Adversary    | |  Guardrails   | |   Stateless   |
            | (AdvBench/GCG)| |  Classifiers  | | KV-Cache Wipe |
            +---------------+ +---------------+ +---------------+
                    |                 |                 |
                    +-----------------+-----------------+
                                      |
                                      v
                    +-----------------------------------+
                    | Tamper-Evident SHA-256 Hash Chain |
                    |      Audit & Forensic Provenance  |
                    +-----------------------------------+
```

### 1. Multi-Tenant Sandbox & Container Boundaries
- Micro-segmented network topology: `red-net`, `blue-net`, `llm-net` with `--internal` flags preventing direct network visibility.
- Non-root user privileges (`USER 1000:1000`) and dropped capabilities (`cap_drop: ALL`).
- Resource limits configured to prevent timing side channels.

### 2. Context Bleed & KV-Cache Purge
- Every evaluation runs inside an ephemeral session.
- Conversation context and attention KV-cache buffers are explicitly purged between runs to prevent adversarial state persistence.

### 3. Tamper-Evident Forensic Ledger
- Cryptographically chained blocks using `SHA-256(index + timestamp + tenant + payload + prev_hash)`.
- Real-time audit verification detects any retroactive alteration of evaluation outcomes.

---

## Quickstart

### 1. Launch the Backend API
```powershell
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Open the Control Dashboard
Open [index.html](file:///c:/Users/Admin/Desktop/Projects/HackInHills/frontend/public/index.html) in any browser, or serve it via:
```powershell
cd frontend/public
python -m http.server 3000
```

### 3. Run Automated Isolation Tests
```powershell
python -c "import sys; sys.path.append('backend'); import tests_isolation; [t() for t in [tests_isolation.test_ledger_integrity, tests_isolation.test_tamper_detection, tests_isolation.test_red_blue_isolation, tests_isolation.test_model_kv_cache_purge, tests_isolation.test_orchestrator_evaluation_pipeline]]; print('All isolation tests verified!')"
```
