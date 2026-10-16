
"""Student attendance tracker with security and code-quality fixes."""

import csv
import glob
import os
import ssl
import tarfile
from datetime import datetime

import requests


# Global attendance register
students = {}
attendance_register = {}
ERP_URL = "https://erp.college.example/api/attendance"
ERP_API_KEY = os.getenv("ERP_API_KEY")
MIN_ATTENDANCE = 75


def add_student(roll_no, name, section="A"):
    """Add a student to the attendance tracker."""
    students[roll_no] = {
        "name": name,
        "section": section,
        "records": [],
    }


def mark_attendance(roll_no, date, status, register=None):
    """Record attendance without using a mutable default argument."""
    if register is None:
        register = attendance_register

    register.setdefault(date, []).append(roll_no)
    students[roll_no]["records"].append((date, status))
    return register


def attendance_percentage(roll_no):
    """Calculate the percentage of attendance for a student."""
    records = students[roll_no]["records"]
    total = len(records)

    if total == 0:
        return 0

    present = sum(1 for record in records if record[1] == "P")
    return int(present / total * 100)


def is_eligible(percentage):
    """Return whether a student meets the minimum attendance."""
    return percentage >= MIN_ATTENDANCE


def shortage_list():
    """Return students who do not meet attendance requirements."""
    result = [
        roll_no
        for roll_no in students
        if not is_eligible(attendance_percentage(roll_no))
    ]
    return result or None


def has_long_absence(roll_no, days=3):
    """Check whether a student has consecutive absences."""
    statuses = [
        status for _, status in students[roll_no]["records"]
    ]
    return any(
        statuses[index:index + days] == ["A"] * days
        for index in range(len(statuses))
    )


def latest_date(roll_no):
    """Return the latest attendance date in ISO format."""
    records = students[roll_no]["records"]
    if not records:
        return None

    dates = [
        datetime.strptime(date, "%Y-%m-%d")
        for date, _ in records
    ]
    return max(dates).date().isoformat()


def _safe_csv_value(value):
    """Prevent spreadsheet formula execution from CSV text values."""
    if isinstance(value, str) and value.startswith(
        ("=", "+", "-", "@")
    ):
        return "'" + value
    return value


def export_csv(path="attendance.csv"):
    """Export attendance percentages to a UTF-8 CSV file."""
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["roll_no", "name", "percentage"])

        for roll_no, student in students.items():
            writer.writerow([
                _safe_csv_value(roll_no),
                _safe_csv_value(student["name"]),
                attendance_percentage(roll_no),
            ])

    return path


def sync_to_erp(roll_no):
    """Send attendance to the ERP using secure request settings."""
    if not ERP_API_KEY:
        raise RuntimeError(
            "Set the ERP_API_KEY environment variable before syncing."
        )

    payload = {
        "roll_no": roll_no,
        "pct": attendance_percentage(roll_no),
    }
    response = requests.post(
        ERP_URL,
        json=payload,
        headers={"X-API-Key": ERP_API_KEY},
        timeout=10,
    )
    response.raise_for_status()
    return response.status_code


def backup_reports():
    """Back up CSV reports without running shell commands."""
    csv_files = glob.glob("*.csv")

    with tarfile.open("reports_backup.tgz", "w:gz") as archive:
        for csv_file in csv_files:
            archive.add(csv_file, arcname=os.path.basename(csv_file))


def legacy_channel():
    """Create a TLS context with secure default settings."""
    return ssl.create_default_context()


def run_job(command_args):
    """Build a reminder job description without executing a command."""
    return {"command": command_args, "shell": False}


def schedule_reminders():
    """Prepare the reminder job using separate command arguments."""
    return run_job(["send_sms", "--shortage"])


def main():
    """Run the attendance tracker demonstration."""
    add_student("R01", "Aditi")
    add_student(
        "R02",
        '=HYPERLINK("http://evil.example","Bharat")',
    )

    for date, status in [
        ("2026-09-01", "P"),
        ("2026-09-02", "P"),
        ("2026-09-03", "L"),
        ("2026-09-04", "P"),
        ("2026-09-05", "H"),
    ]:
        mark_attendance("R01", date, status)

    for date, status in [
        ("2026-09-01", "P"),
        ("2026-09-01", "P"),
        ("2026-09-02", "A"),
        ("2026-09-03", "A"),
        ("2026-09-04", "A"),
        ("2026-9-3", "P"),
    ]:
        mark_attendance("R02", date, status)

    register = mark_attendance("R01", "2030-01-01", "P")
    print("R01 attendance %:", attendance_percentage("R01"))
    print("R02 attendance %:", attendance_percentage("R02"))
    print("Is 75% eligible?", is_eligible(75))
    print("Shortage list:", shortage_list())
    print("R02 long absence?", has_long_absence("R02"))
    print("R02 latest date:", latest_date("R02"))
    print(
        "Register entries for 2026-09-01:",
        register["2026-09-01"],
    )
    print("Exported to:", export_csv())
    print("Reminder job:", schedule_reminders())
    print("ERP sync skipped (no network request in this demo)")


if __name__ == "__main__":
    main()
