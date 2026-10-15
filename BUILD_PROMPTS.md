# Build prompts — v0 web app (responsive, mobile-first; no native app)

How to use: put `AGENTS.md` in the repo root first. Paste **one prompt at a time** into your coding agent. Don't start the next until the current step's checks pass. Each prompt is short on purpose — the context lives in `AGENTS.md`.

Suggested schedule: Steps 0–2 on 16 Oct, 3–5 on 17 Oct, 6–7 on 18 Oct morning.
**Cut line if behind:** drop the case assistant (Step 5 extra) → then forms (keep checklist) → never drop Step 6 (Verify) or the gate engine.

---

## Step 0 — Scaffold

```
Read AGENTS.md. Scaffold the repo:
- /backend: FastAPI app with /health, SQLModel + SQLite, pytest set up.
- /frontend: Next.js (App Router, TS, Tailwind), a layout with the "Demo · synthetic data" banner and {{APP_NAME}} header, mobile-first.
- A root README with one command to run both locally, and a .env.example (GEMINI_API_KEY).
- DECISIONS.md (empty template).
No features yet. Show me how to run it and confirm both start.
```

**Check:** both apps run; banner visible at 375px width.

---

## Step 1 — Synthetic data pack

```
Create /backend/seed with all synthetic data for the demo case in AGENTS.md:
- institutions.json (SBI, HDFC Bank, LIC, CAMS, the hidden-shares company, the dormant-deposit bank) with aliases, SMS sender IDs, email domains.
- digilocker_mock.json (Ananya's identity doc; death certificate for Rajesh; Ananya's passport naming her father).
- sms_parent.json (~25 messages: bank/insurer alerts mixed with personal messages and 3 OTP messages that must be filtered out).
- inbox_parent.json (~20 emails: LIC premium reminders, CAMS statement, newsletters, personal mail).
- ais_parent.json (tax record rows: SBI FD interest, HDFC savings interest, dividend from the hidden-shares company).
- registries_mock.json (UDGAM/MITRA/IEPF/Bima Bharosa lookups; one dormant deposit hit).
- Generate two images with Pillow: share_certificate.png (old physical certificate) and impostor_death_certificate.png (same layout as the real one but different date of death and a mismatched font in the date field). Also generate the genuine death_certificate.png.
- impostor_claim.json (claimant "Vikram Sharma", nephew, LIC policy, attaches the impostor certificate).
Add a seed loader and POST /admin/reset that wipes and reseeds the DB. Write a short /backend/seed/README listing every planted clue and the expected discovered assets, so we can test against it.
```

**Check:** reset works; README lists expected assets (≈7 incl. 1 suggested).

---

## Step 2 — Data model, gate engine, audit log

```
Implement the data model from AGENTS.md (SQLModel). Then:
- gate_engine.py: pure functions that compute a case's gate from its proofs, and a FastAPI dependency `require_gate(case_id, "G3")` used on every case-data route.
- Masking serializer: assets below G4 return only institution, type, value band, last4, confidence, status, evidence snippets.
- Name matching util (transliteration-aware fuzzy match, e.g. "Rajesh Kumar Sharma" ≈ "R. K. Sharma").
- One-case-per-deceased rule: a second claimant for the same deceased links both cases and sets frozen_reason.
- AuditEvent written on every gate change, connection, lookup, view.
Tests (pytest) — these are the acceptance criteria:
1. No route returns asset data for a case below G3 (call APIs directly).
2. Full identifiers never appear below G4.
3. Duplicate case for same deceased freezes both.
4. Audit events are written for each action.
```

**Check:** all 4 tests pass.

---

## Step 3 — Start flow (G0 → G3)

```
Build the Start flow UI + APIs (5 screens, mobile-first, plain language):
1. Welcome & sign in (simulated phone OTP; any 6 digits) → G0.
2. About you: "Verify with DigiLocker" (simulated consent screen) or "I live abroad" → passport + selfie video (simulated) → G1.
3. About them: name, DOB, PAN, date of death; app "finds" the death certificate in mock DigiLocker → match → G2.
4. Your relationship: pick "daughter"; app checks Ananya's passport names her father → G3.
5. Other family: optional list of other heirs.
Each screen shows: what we'll do, what we'll never do, and a progress indicator of gates.
Also build a "Discovery locked" state: before G3 the assets area explains why nothing is shown.
Add an Activity log page listing AuditEvents.
```

**Check:** typing name + PAN alone shows the locked state; reaching G3 unlocks the Connect screen.

---

## Step 4 — Connect & Discover

```
Build Connect + Discover:
- Connect screen with 4 cards in this order: parent's email, tax record, parent's phone SMS (labelled "Needs Android companion · simulated in demo"), camera scan (browser camera via file input). Each card has the consent pattern: what we read / ignore / keep / disconnect. Clicking connect loads the seed file (simulated). Registries run automatically after G3.
- Source readers: filter step (keep only institution senders/domains; drop OTP messages) → Gemini structured extraction into Signal records (Pydantic schema). Do not persist raw message bodies; store only fields + a short snippet.
- Camera scan: real Gemini vision extraction on share_certificate.png.
- Reconciler: match signals to Institution, merge into Assets (same institution + type + last4 = one asset), confidence rules from AGENTS.md.
- Inference: propose hidden shares from the AIS dividend as "suggested", with the next step to confirm.
- Asset map UI: cards appear progressively as sources finish; each card is masked and has "How we found this" (evidence) and Yes / No / Not sure buttons.
Test against /backend/seed/README expected assets.
```

**Check:** expected assets found; SMS + email signals for one account merge into one card; OTPs never stored; hidden shares marked suggested.

---

## Step 5 — Plan & claim packs (G4)

```
Build Plan + claim packs:
- Claim-path rules engine (code): per confirmed asset choose nominee / joint holder / simplified (≤ ₹15 lakh at commercial banks) / succession certificate; Gemini writes the plain-language explanation only.
- One ordered recovery plan across all assets (e.g. legal heir certificate before bank claims) with a document checklist per asset.
- G4 per asset via simulated "nominee confirmed" or "legal heir certificate added"; only then show full details.
- Generate PDFs for 3 templates only: bank deceased-claim form, IEPF-5 cover data sheet, indemnity letter — pre-filled from case data.
- "Submit" marks the claim as sent and creates an InstitutionClaim for the LIC asset (this feeds Step 6).
Optional if time: a case assistant chat grounded only in this case's data.
```

**Check:** LIC asset reaches G4, PDF downloads with correct data; non-G4 assets stay masked.

---

## Step 6 — Insurer console (Verify)

```
Build the institution side at /console (simple login as "LIC claims desk"):
- Claim queue showing two claims on the same policy: Ananya's (from Step 5) and Vikram's (impostor_claim.json).
- Verify agent runs checks and stores CheckResults:
  1. Cross-document consistency (names, dates, relationship) — Gemini compares, code records pass/fail with evidence.
  2. Authenticity signals on the certificate image (layout/font/date-field mismatch vs the genuine template).
  3. Duplicate check against a mock shared claims index (same deceased, different claimant).
  4. Completeness: missing documents list.
- Risk score computed by code from check results: Low / Medium / High, each reason linked to evidence.
- Actions: Approve, Request documents (drafts a message to claimant), Escalate. Every action logged.
Expected: Ananya = Low (approve); Vikram = High (date mismatch + edited field + duplicate).
```

**Check:** both outcomes as expected; every reason clickable to its evidence.

---

## Step 7 — Demo polish & deploy

```
Prepare for judging:
- Demo mode: a "Start demo" button that resets data and a step-by-step guide sidebar for the 3-minute story (locked → proofs → assets appear → claim pack → insurer catches impostor).
- Empty, loading and error states on every screen; check 375px and desktop.
- Deploy to Cloud Run; set env vars; confirm /admin/reset works in production.
- README: architecture diagram (text), how gates work, what is simulated vs real, how to run locally.
Then give me a list of anything that's flaky so I can avoid it on stage.
```

**Check:** fresh deploy runs the full story twice in a row without manual fixes.
