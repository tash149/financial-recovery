# AGENTS.md — project brief (read this before every task)

## What we're building
A **responsive web app** (mobile-first, works on phone and desktop browsers; no native app) that helps an heir find and claim the financial assets of a parent who has died (India first, NRI heirs a key segment), and helps an insurer/bank verify death claims and catch impostors. 

App name placeholder: `{{reclaim}}` (use this string everywhere; it will be replaced later).

## v0 in one sentence
An NRI heir proves who she is, that her father died, and that she's his daughter; connects (simulated) sources; sees her father's assets appear — masked, each with evidence — gets a claim pack; then an insurer's console catches an impostor claiming the same death.

## Non-negotiable rules
1. **Prove before you see.** No search runs and no asset data is returned until the case reaches gate G3. Name + DOB + PAN alone unlock nothing.
2. **Access decisions are deterministic code, never the LLM.** Gemini extracts and explains; the gate engine decides.
3. **Mask by default.** Below G4: institution, asset type, value band (e.g. "₹1–5 lakh"), last 4 digits only. Full identifiers only inside a claim pack at G4.
4. **Read, extract, forget.** Store extracted fields + short evidence snippets. Do not persist raw SMS/email bodies after extraction.
5. **Everything is logged.** Every gate change, connection, lookup and view writes an `AuditEvent` shown to the heir.
6. **Synthetic data only.** Show a visible "Demo · synthetic data" banner on every screen. No real personal data, ever.
7. **Humans confirm.** Every AI conclusion shows its evidence; the user confirms before anything is filed or decided.

## Trust gates (per case)
| Gate | Proof | Unlocks |
|---|---|---|
| G0 Account | phone OTP (simulated) | guides only |
| G1 Identity | DigiLocker consent (simulated) or passport + video selfie (simulated) | create case |
| G2 Death | death certificate (simulated DigiLocker fetch, or scan) matched to deceased's name/DOB | case active, still no lookups |
| G3 Relationship | heir's own document naming the parent (simulated) | discovery runs; results masked |
| G4 Entitlement (per asset) | nominee confirmation or legal-heir certificate (simulated) | full details + claim pack for that asset |

Rules: fuzzy, transliteration-aware name matching; mismatches go to manual review, not rejection; parent must be plausibly older than child; **one case per deceased** — a second claimant for the same person links and freezes both cases.

## Demo case (all synthetic)
- Deceased: **Rajesh Kumar Sharma**, Delhi. Heir: daughter **Ananya Sharma**, Toronto (NRI).
- Sources and what they reveal:
  - SMS (parent's Android phone): SBI fixed deposit, HDFC savings account. A web app cannot read SMS; in the real product this comes from a small Android companion app (later). In v0 it is simulated and the card must say "Needs Android companion · simulated in demo".
  - Email: LIC policy premium reminders; CAMS consolidated MF statement
  - Tax record (AIS): FD interest (SBI), savings interest (HDFC), **dividend from a company with no known holding → hidden shares (suggested)**
  - Registries (mock UDGAM/MITRA/IEPF): one old dormant deposit match
  - Camera scan: one old physical share certificate
- Impostor: "nephew" **Vikram Sharma** files a claim on the LIC policy with an **edited death certificate** (date of death differs; layout/font mismatch).

## Data model (keep to these)
`Case`, `Person` (deceased; PAN stored hashed), `Claimant`, `Consent`, `Signal`, `Evidence`, `Asset`, `AuditEvent`, plus reference table `Institution` (canonical name, aliases, SMS sender IDs, email domains, form templates). Institution-side: `InstitutionClaim`, `CheckResult`.

Asset confidence: **High** = 2+ independent sources or an official statement; **Medium** = one direct source; **Suggested** = inferred. Assets have status `suggested | confirmed | rejected`.

## Stack
- Backend: Python 3.11, FastAPI, Google ADK for agents, `google-genai` for Gemini (structured JSON output with Pydantic schemas).
- Frontend: Next.js (App Router) + TypeScript + Tailwind, mobile-first.
- Storage: SQLite via SQLModel for v0 (re-seeded on startup / via reset endpoint). Files in local `data/` (Cloud Storage optional).
- Deploy: Cloud Run (two services or one container — keep it simple).
- Secrets via env vars (`GEMINI_API_KEY` or Vertex AI credentials). Never commit keys.

## Agents vs code
- Gate service: plain code (not an agent).
- Source readers (SMS, email, AIS, statement, scan): Gemini → `Signal` records.
- Reconciler agent: match signals to `Institution`, merge into `Asset`, score confidence (merge rules deterministic; LLM only for fuzzy institution matching).
- Inference agent: proposes hidden assets, always `suggested`.
- Registry agent: calls mock registry tools, only after G3.
- Verify agent (institution side): consistency + authenticity checks → `CheckResult`; risk score is computed by code from check results.

## Design & tone
Calm, plain language, respectful of grief. No dark patterns, no urgency tricks. Large tap targets, works at 375px width and on desktop (institution console is desktop-first). Use browser features only: camera capture via file input with `capture`, no native APIs. Every screen says what happens next and what we will never do. English UI; Hindi is a stretch goal.

## How to work in this repo
- Build in the step order given by the user; finish and verify one step before starting the next.
- Keep changes small; don't refactor earlier steps unless asked.
- After each step: run tests, list what changed, and show how to see it in the browser.
- If something is ambiguous, choose the simplest option consistent with this file and note it in `DECISIONS.md`.
