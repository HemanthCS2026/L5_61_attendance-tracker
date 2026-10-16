
# Lab 5: Static Code Analysis — Issues and Fixes

| Issue | Type | Line(s) Before Fix | Description | Fix Approach |
|---|---|---:|---|---|
| Disabled HTTPS certificate verification | Bandit B501 — High | 49 | `verify=False` disables server certificate verification and exposes the connection to interception. | Removed `verify=False` to use default certificate verification. |
| Shell command with wildcard | Bandit B609/B602 — High | 52 | Running a shell command with `shell=True` and a wildcard can introduce command-injection risks. | Replaced shell execution with Python's `tarfile` module. |
| Missing request timeout | Bandit B113 — Medium | 49 | An HTTP request without a timeout may wait indefinitely. | Added `timeout=10` to the request. |
| Outdated TLS protocol | Bandit B503 — Medium | 55 | TLS 1.0 is outdated and should not be selected as the default protocol. | Replaced it with `ssl.create_default_context()`. |
| Hardcoded API key | Security review | 12 | A key embedded in source code can be exposed when the repository is shared. | Read the key using `os.getenv("ERP_API_KEY")`. |
| Mutable default argument | Pylint | 18 | A default dictionary can be shared across function calls. | Changed the default to `None` and initialized the register inside the function. |
| Possible division by zero | Logic review | 24 | Attendance calculation fails when a student has no records. | Return zero when the record count is zero. |
| CSV formula injection | Security review | CSV export | Spreadsheet formulas in untrusted text fields can execute when a CSV is opened. | Added `_safe_csv_value()` to prefix potentially dangerous formula values. |
| Insecure subprocess execution | Security review | Reminder job | Executing a command through a shell can introduce command-injection risks. | Represented the reminder as a command argument list with `shell` set to `False`; no command is executed by this demo. |
| Code-quality warnings | Pylint | 107, 152 | Dictionary iteration and an unused function argument generated warnings. | Used `students.items()` and removed the unused `shell` parameter from `run_job()`. |

## Verification After Fixes

- **Pylint:** 10.00/10.
- **Bandit:** No issues identified.
- **Flake8:** No errors reported.
- **Execution:** The attendance tracker ran successfully in the local environment.
