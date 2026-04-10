# Dependency Safety Policy

This project follows a conservative dependency process to reduce the risk of
malicious or unsafe packages.

## Scope

This policy applies to:

- Python dependencies added to `pyproject.toml`
- Any direct `pip install` command used for project work

## Core Rules

- Prefer the Python standard library first.
- Reuse already-declared project dependencies when possible.
- Add new dependencies only when there is a clear, documented need.
- Pin dependency versions for reproducibility.
- Do not install dependencies globally for project work.

## Required Pre-Install Checklist

Before adding any new dependency, complete all items:

- Confirm no existing dependency can solve the task.
- Confirm the package name is exact (to avoid typosquatting).
- Verify package legitimacy:
  - Official docs/repo link from trusted sources
  - Active maintenance and recent releases
  - Reasonable community adoption
- Review known security signals:
  - Open advisories/CVEs
  - Suspicious maintainer or release activity
- Record why the dependency is needed in commit or PR notes.

## Safe Install Workflow (Python)

1. Create and activate a virtual environment.
2. Install a pinned version.
3. Verify import/use in a small script or test.
4. Run tests.
5. Commit dependency declaration changes with related code.

Example commands:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install "<package>==<version>"
python -m pip freeze | rg "<package>"
python -m unittest
```

## Vulnerability Scanning

After dependency changes, run at least one scanner:

```bash
pip install pip-audit
pip-audit
```

If vulnerabilities are reported:

- Do not merge/deploy until triaged.
- Upgrade, replace, or remove vulnerable dependencies.
- Document accepted risk if temporary exceptions are required.

## Update Policy

- Batch updates on a regular cadence (for example, monthly).
- Prefer patch/minor upgrades first.
- Review changelogs before upgrading major versions.
- Re-run tests and vulnerability scan after updates.

## Emergency Response

If a dependency is suspected malicious or compromised:

- Stop new deployments.
- Remove or pin away from the affected version.
- Rotate any potentially exposed credentials.
- Audit recent commits and runtime logs for suspicious behavior.
