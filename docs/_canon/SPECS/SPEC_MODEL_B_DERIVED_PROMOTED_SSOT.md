# SPEC — Model B: Derived Promoted to SSOT with Verifiable Integrity

**Version:** 1.0  
**Status:** APPROVED  
**Date:** 2026-02-16  
**Scope:** Deterministic documentation artifacts

---

## 1. Objective

Define a deterministic model where generated artifacts are promoted to SSOT and protected by cryptographic integrity. This model ensures that derived documentation artifacts become the single source of truth with verifiable, tamper-proof guarantees.

---

## 2. Definitions

| Term | Definition |
|------|------------|
| **Derived Artifact** | File produced by a generator (e.g., schema.sql, openapi.json) |
| **Promoted SSOT** | Derived artifact treated as canonical truth after generation |
| **Integrity Manifest** | SSOT containing SHA256 checksums for all bundled artifacts |
| **Writer Command** | Single authorized command that produces the complete bundle |
| **Deterministic Regeneration** | Same input always produces identical output |

---

## 3. Normative Rules (BCP14 Keywords)

The following keywords MUST, MUST NOT, SHOULD, and SHOULD NOT are interpreted as specified in RFC 2119.

### 3.1 Artifact Declaration

- **MUST:** Promoted artifacts MUST declare a single writer command
- **MUST:** Promoted artifacts MUST declare their generation source
- **MUST:** Promoted artifacts MUST have a declared purpose in documentation

### 3.2 Integrity Enforcement

- **MUST:** Integrity MUST be enforced via cryptographic checksums (SHA-256)
- **MUST:** The integrity manifest MUST be treated as SSOT
- **MUST NOT:** Manual edits to promoted artifacts MUST NOT bypass integrity checks
- **SHOULD:** Gates SHOULD fail on checksum mismatch

### 3.3 Writer Exclusivity

- **MUST:** Only one writer command MUST exist per artifact bundle
- **MUST NOT:** Parallel writers MUST NOT be allowed for the same artifacts

### 3.4 Determinism

- **MUST:** Regeneration MUST produce identical checksums when inputs are unchanged
- **SHOULD:** Gate validation SHOULD run on every artifact update

---

## 4. Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐     ┌────────┐
│  Generator  │ ──► │   Snapshot   │ ──► │ Integrity       │ ──► │ Gate   │
│  (Python)   │     │  (Artifacts) │     │ Manifest (YAML) │     │(L0-L2) │
└─────────────┘     └──────────────┘     └─────────────────┘     └────────┘
```

### Components

1. **Generator:** Python script that produces schema.sql, openapi.json, alembic_state.txt
2. **Snapshot:** Point-in-time capture of all generated artifacts
3. **Integrity Manifest:** YAML file containing SHA256 checksums of all artifacts
4. **Gate:** Validation script that verifies structure (L0), schema (L1), and integrity (L2)

---

## 5. Invariants

### 5.1 Single-Writer Invariant
Only one command (`pwsh docs/_ssot/update_gen.ps1`) may modify the artifact bundle.

### 5.2 Immutable Bundle Invariant
Once checksums are recorded in `_manifest.yaml`, the artifacts cannot be manually edited without breaking the gate.

### 5.3 Verifiable Integrity Invariant
Every gate run MUST recalculate checksums and compare against the manifest.

### 5.4 Deterministic Regeneration Invariant
Running the writer command with identical inputs MUST produce identical checksums.

---

## 6. Threat Model

| Threat | Protection Mechanism |
|--------|---------------------|
| **Silent manual edits** | Checksum mismatch triggers L2 gate failure |
| **Parallel writers** | Single-writer command enforced; manifest is SSOT |
| **Structural drift** | L0/L1 gates validate schema consistency |
| **Agent hallucination** | SSOT with cryptographic integrity verification |

---

## 7. HB Track Instantiation

### Writer
```powershell
pwsh docs/_ssot/update_gen.ps1
```

### Integrity SSOT
```yaml
docs/_ssot/_manifest.yaml
```

### Gate Script
```python
scripts/checks/check_hb_track_profile.py
```

### Gate Layers

| Layer | Validation | Status |
|-------|------------|--------|
| L0 | Structure (files exist, valid YAML/JSON) | ✅ PASS |
| L1 | Schema (consistency across artifacts) | ✅ PASS |
| L2 | Integrity (checksum verification) | ✅ PASS |

---

## 8. Implementation Files

| File | Purpose |
|------|---------|
| `docs/_ssot/update_gen.ps1` | Writer command |
| `docs/_ssot/_manifest.yaml` | Integrity SSOT |
| `scripts/checks/check_hb_track_profile.py` | Gate validator |
| `docs/_canon/BASELINES/docs-determinism-v1.md` | Frozen baseline |

---

## 9. Governance

- Any modification to this spec requires approval via ARCHITECT_HANDSHAKE
- Baseline changes require a new version (e.g., docs-determinism-v2)
- Drift detection is automated via gate runs in CI

---

**End of SPEC — Model B**
