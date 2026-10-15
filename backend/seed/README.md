# Seed data — demo case (all synthetic)

Every name, number, document and message here is made up. Real institution names (SBI, HDFC Bank, LIC, CAMS, PNB) are used only as labels; the two companies (Narmada Polymers, Bharat Textile Mills) are fictional. Images carry a "SYNTHETIC DEMO DOCUMENT" mark.

**Reset:** `POST /admin/reset` (or `POST /api/admin/reset` through the frontend) drops every table, recreates the schema and reloads `institutions.json`. The app also resets on every startup. The other files are mock external sources that later steps read from disk when the heir connects them.

**Regenerate images:** `cd backend && .venv/bin/python -m seed.generate_images` (deterministic; needs Liberation and DejaVu fonts).

## The people

| Who | Facts |
|---|---|
| Deceased | **Rajesh Kumar Sharma**, DOB 14-03-1952, died 02-06-2026, C-42 Lajpat Nagar II, New Delhi. Father: Om Prakash Sharma. Wife Sunita died earlier. PAN `ABCPS1234D` (example value; store hashed). |
| Heir | **Ananya Sharma**, daughter, DOB 21-09-1988, lives in Toronto (NRI), only child. Passport `Z9900123` names father RAJESH KUMAR SHARMA. Nominee on the LIC policy and the SBI FD. |
| Impostor | **Vikram Sharma**, "nephew", DOB 03-11-1979, Ghaziabad. |

## Files

| File | What it simulates |
|---|---|
| `institutions.json` | Reference table: canonical name, aliases, SMS sender IDs, email domains, claim-form templates (7 institutions). |
| `digilocker_mock.json` | Ananya's DigiLocker (Aadhaar e-KYC, passport) and a death-registry lookup (genuine certificate + one decoy). |
| `sms_parent.json` | 26 SMS from Rajesh's phone. |
| `inbox_parent.json` | 20 emails from Rajesh's mailbox. |
| `ais_parent.json` | Income-tax AIS for FY 2024-25 and 2025-26. |
| `registries_mock.json` | Mock UDGAM, MITRA, IEPF, Bima Bharosa. |
| `impostor_claim.json` | Vikram's claim on the LIC policy. |
| `lic_policy_record.json` | LIC's own policy record (console only): nominee is Ananya. |
| `expected_assets.json` | Machine-readable answer key for tests (this README in JSON). |
| `death_certificate.png` | Genuine certificate. |
| `impostor_death_certificate.png` | Edited copy of the genuine certificate. |
| `share_certificate.png` | 1994 physical share certificate. |

## Expected discovered assets (7, one suggested)

Value bands: Under ₹1 lakh · ₹1–5 lakh · ₹5–15 lakh · ₹15–50 lakh · Over ₹50 lakh. Every asset lands with status `suggested` and only the heir's "Yes" confirms it; the confidence column is what distinguishes the inferred one.

| # | Asset | Masked (last 4) | Band | Confidence | Found from |
|---|---|---|---|---|---|
| 1 | SBI fixed deposit, ₹6,00,000 @ 7.10%, matures 15-01-2027 (₹7,41,045) | 4821 | ₹5–15 lakh | **High** | SMS sms-02, 12, 19, 25 + AIS interest rows (two independent sources) |
| 2 | HDFC Bank savings account, balance ₹2,34,518.40 (30-04-2026) | 0937 | ₹1–5 lakh | **High** | SMS sms-01, 05, 10, 15, 20, 22, 26 + AIS savings interest |
| 3 | LIC New Jeevan Anand, policy 112345678, sum assured ₹10,00,000 | 5678 | ₹5–15 lakh | **Medium** | Email em-01, 02, 16, 19 (one source, not a statement) |
| 4 | Kotak MF via CAMS, folio 10433902, ₹3,80,442 (two schemes) | 3902 | ₹1–5 lakh | **High** | Email em-14 CAS = official statement; em-12 SIP note merges in |
| 5 | Narmada Polymers shares, ~700 shares × ₹412 ≈ ₹2.9 lakh | — | ₹1–5 lakh | **Suggested** | AIS dividend rows only; no holding found anywhere |
| 6 | PNB dormant savings, ₹48,312, inoperative since 2014, moved to DEA Fund | 7702 | Under ₹1 lakh | **Medium** | UDGAM record udgam-0001 (one registry hit) |
| 7 | Bharat Textile Mills, 200 physical shares, folio R001893, cert 0041172 | 1893 | Under ₹1 lakh | **Medium** | Camera scan of share_certificate.png |

## Planted clues

**SMS (`sms_parent.json`)**
- Sender IDs come as `XX-HEADER` (e.g. `VM-HDFCBK`); match on the 6-letter header after the dash.
- **OTPs to drop (3):** sms-04 (from HDFCBK — a known sender, so the filter must check content, not just sender), sms-09 (SBIOTP), sms-14 (unknown app). The card XX5521 inside sms-04 must never surface.
- **Same account, many messages:** all HDFC alerts say `XX0937` → one asset. SBI messages say `XXXXXXX4821` → one asset.
- **Name variant:** sms-19 addresses him as "R K SHARMA"; also says the FD nominee is "ANANYA S" (useful later for the nominee claim path).
- **Decoys:** sms-06 `SBICRD` is SBI Card, not SBI (and not in the sender list); sms-16 is an HDFC loan promo (known sender, no asset).
- **Personal / sensitive, to ignore:** sms-03, 08, 13, 18, 21 (clinic appointment), 24 (condolence). Plus utility/retail noise sms-07, 11, 17, 23.
- **After death:** sms-25, 26 still show interest accruing — the accounts are live.

**Email (`inbox_parent.json`)**
- **LIC:** em-01 and em-16 premium reminders, em-02 receipt (attachment text gives plan + branch), em-19 grace-period notice after the death that says the nominee may claim.
- **CAMS:** em-14 CAS attachment text has folio, both schemes, units, NAV, value, "Nominee: Registered". em-12 SIP note mentions the same folio → merges into the same asset.
- **Phishing decoy:** em-06 "LIC bonus refund" from `licindia-bonus-refund.example` — not an LIC domain, must be filtered out.
- **Known domain, no asset:** em-08 HDFC fraud-tips newsletter from `hdfcbank.net`.
- **Personal mail mentioning assets:** em-09 from Ananya mentions the SBI FD and LIC premium. Personal mail is not read; those assets are found from other sources anyway.
- **Noise:** newsletters em-03, 07, 18; retail/travel em-05, 10, 13; RWA em-11; yoga club em-17; security alert em-15; condolence em-20.

**Tax record (`ais_parent.json`)**
- Name appears as "RAJESH K SHARMA" (variant).
- SBI interest rows carry account `XXXXXXX4821`, HDFC rows `XXXXXXXXXX0937` → they merge with the SMS assets, lifting both to High.
- **Hidden shares:** Narmada Polymers paid dividends both years (₹2,800 and ₹3,150). `institutions.json` public reference: ₹4.00 and ₹4.50 per share → 700 shares both years; × ₹412 ≈ ₹2.9 lakh. No SMS, email or demat statement mentions this company → `Suggested`. Next step for the heir: ask the registrar (Link Intime) or the depositories for a holding statement.

**Registries (`registries_mock.json`)** — only after G3
- **One hit:** UDGAM udgam-0001 — same name, DOB, Lajpat Nagar, PAN last 4 `234D`.
- **Decoys (no match):** udgam-0002 "RAJESH SHARMA", Jaipur, DOB 1966; MITRA "RAJESH KUMAR SHARMAN", Pune, DOB 1975; IEPF "R K SHARMA", Kolkata, father HARI PRASAD SHARMA (his father is Om Prakash); Bima Bharosa "RAJESHWARI SHARMA", Lucknow.

**Camera scan (`share_certificate.png`)**
- Holder RAJESH KUMAR SHARMA, 200 shares of ₹10, distinctive nos. 1045201–1045400, cert 0041172, folio R001893, dated 12-08-1994. Not linked to the Narmada dividend (different company). Physical shares must be transmitted and dematerialised.

**DigiLocker (`digilocker_mock.json`)**
- Ananya's e-KYC and passport: same name and DOB → G1. Passport's "father / legal guardian" = RAJESH KUMAR SHARMA → G3.
- Death registry: genuine record DEMO-DL-2026-061472 matches name + DOB → G2. Decoy record "RAJESH SHARMA", DOB 1961, died 07-03-2026 in Rohini must **not** match (DOB differs).
- Parent plausibly older than child: 1952 vs 1988 (36 years).

## Impostor (Verify console)

`impostor_claim.json` + `impostor_death_certificate.png`, checked against `death_certificate.png`, `digilocker_mock.json` and `lic_policy_record.json`. Expected risk: **High**.

| Check | What's wrong |
|---|---|
| Consistency | Stated and certificate date of death **18-05-2026**; registry and genuine certificate say **02-06-2026**. Same registration number DEMO-DL-2026-061472 as the genuine one. |
| Authenticity | Only the date-of-death value differs from the genuine image: it sits on a pure-white patch (paper is off-white), is set in **DejaVu Sans** while every other value is **Liberation Serif**, is slightly larger and ~5 px below the baseline of its label. |
| Duplicate | Same deceased and same policy as Ananya's claim (created in Step 5), different claimant. |
| Relationship / entitlement | Claimant is a nephew; nominee on file is Ananya Sharma (daughter). His statement says she "cannot be reached". |
| Completeness | No nominee consent/NOC, no legal-heir or succession certificate, no policy bond, no relationship proof. Payout to his own account at a different bank. |

Ananya's claim (from Step 5) should score **Low**: nominee matches, genuine certificate, consistent dates.
