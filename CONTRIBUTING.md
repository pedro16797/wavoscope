# Contributing to Wavoscope

Hopefully this will provide a simple, easy to understand guide to making safe contributions to the project, happy coding!

---

## Why This Matters

Wavoscope is a precision audio analysis and transcription tool. It supports a wide variety of audio formats, sample rates, and bit depths. A change that works perfectly on one setup can unintentionally break another if scope is not tightly controlled.

The goal is **predictable, low-risk contributions** that maintainers can trust and merge with confidence.

---

## Core Principles for Contributors

### Solve One Problem at a Time
- Keep each PR focused on **a single bug or feature**.
- Do **not** mix refactors, formatting, and behaviour changes unless absolutely required.

### Minimize Blast Radius
- Touch **only** the files and functions required for the fix.
- Avoid “drive-by improvements” in unrelated code.

### Prove the Change
- Add or run **targeted checks** for the affected path.
- Include a short **regression checklist** in the PR description.

### Be Explicit About Risk
- Call out edge cases and trade-offs up front.
- If uncertain, say so and ask maintainers for preferred direction.

Clarity beats confidence.

---

## AI Prompt Guardrails

If you are using an AI agent to contribute, please give it these instructions explicitly:

- Ask for a proposal and plan before making code changes.
- Make only the **minimum required changes** for the target issue.
- Do **not** refactor unrelated code.
- Preserve existing behaviour and interfaces unless the bug fix requires change.

These guardrails dramatically reduce accidental regressions from broad AI edits.

---

## Recommended AI-Assisted Workflow

### Step 1: Commit-Scoped Review
Once work is complete and tests pass, commit your work. Ask your agent (or a different one) to review **only your commit diff**, not the whole repo.

### Step 2: Validate Findings
Classify findings as **Accept** (real issue), **Rebut** (incorrect concern), or **Pre-existing**.

### Step 3: Apply Minimal Fixes
Fix accepted issues with the smallest possible patch. Do **not** broaden scope or refactor opportunistically.

### Step 4: PR-Scoped Review
Run a final review on the entire PR diff. Prioritize regression risk across different audio handling paths.

---

## PR Description Template

### Summary
- What bug or feature is addressed
- Why this change is needed

### Scope
- Files changed
- What is explicitly **out of scope**

### Risk and Compatibility
- Target area (e.g., Audio engine, UI, Export)
- Confirmation that unrelated paths are unchanged

### Regression Checks
- Checks run (manual and/or automated)
- Key scenarios validated

---

Maintainers are balancing **correctness, stability, and review bandwidth**. PRs that are tightly scoped, clearly explained, and minimally risky are much more likely to be merged quickly.

Thanks for helping keep Wavoscope stable and enjoyable to use.
