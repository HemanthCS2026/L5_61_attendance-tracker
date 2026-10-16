
"""Attendance tracker with static-analysis and security improvements."""

import os
import csv
import ssl
import tarfile
from pathlib import Path

import requests

# Global attendance register
students = {}
ERP_URL = "https://erp.college.example/api/attendance"
ERP_API_KEY = os.getenv("ERP_API_KEY")
MIN_ATTENDANCE = 75


def addStudent(roll_no, name, section="A"):
    """Add a student to the attendance register."""
    students[roll_no] = {
        "name": name,
        "section": section,
        "records": [],
    }


def markAttendance(roll_no, date, status, register=None):
    """Record attendance and update the register."""
    if register is None:
        register = {}

    register.setdefault(date, []).append(roll_no)
    students[roll_no]["records"].append((date, status))
    return register


def attendancePercentage(roll_no):
    """Calculate a student's attendance percentage."""
    records = students[roll_no]["records"]
    present = sum(record[1] == "P" for record in records)
    total = len(records)

    if total == 0:
        return 0

    return int(present / total * 100)


def isEligible(percentage):
    """Check whether the attendance meets the minimum requirement."""
    return percentage >= MIN_ATTENDANCE


def shortageList():
    """Return students who do not meet the attendance requirement."""
    result = []

    for roll_no in students:
        if not isEligible(attendancePercentage(roll_no)):
            result.append(roll_no)

    return result or None


def hasLongAbsence(roll_no, days=3):
    """Check for consecutive recorded absences."""
    statuses = [
        status for _, status in students[roll_no]["records"]
    ]

    return any(
        statuses[index:index + days] == ["A"] * days
        for index in range(len(statuses) - days + 1)
    )


def latestDate(roll_no):
    """Return the latest recorded attendance date."""
    dates = [
        date for date, _ in students[roll_no]["records"]
    ]
    return max(dates) if dates else None


def _safeCsvValue(value):
    """Protect exported text from spreadsheet formula injection."""
    text = str(value)

    if text.startswith(("=", "+", "-", "@", "\t", "\r")):
        return "'" + text

    return text


def exportCsv(path="attendance.csv"):
    """Export attendance summaries to a CSV file."""
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["roll_no", "name", "percentage"])

        for roll_no, student in students.items():
            writer.writerow([
                _safeCsvValue(roll_no),
                _safeCsvValue(student["name"]),
                attendancePercentage(roll_no),
            ])

    return path


def syncToErp(roll_no):
    """Send attendance to the ERP over verified HTTPS."""
    if not ERP_API_KEY:
        print("ERP sync skipped: ERP_API_KEY is not configured.")
        return None

    payload = {
        "roll_no": roll_no,
        "pct": attendancePercentage(roll_no),
    }
    response = requests.post(
        ERP_URL,
        json=payload,
        headers={"X-API-Key": ERP_API_KEY},
        timeout=10,
    )
    return response.status_code


def backupReports():
    """Create a compressed backup of CSV reports safely."""
    report_files = sorted(
        path for path in Path.cwd().glob("*.csv") if path.is_file()
    )

    with tarfile.open("reports_backup.tgz", "w:gz") as archive:
        for report_file in report_files:
            archive.add(report_file, arcname=report_file.name)


def legacyChannel():
    """Create a TLS context using secure default settings."""
    return ssl.create_default_context()


def runJob(command, shell=False):
    """Describe a job without executing a shell command."""
    if shell:
        raise ValueError("Shell execution is not permitted.")

    if not isinstance(command, (list, tuple)):
        raise ValueError("Command must be a list or tuple of arguments.")

    if not command or not all(
        isinstance(argument, str) for argument in command
    ):
        raise ValueError("Command arguments must be non-empty strings.")

    return {"command": list(command), "shell": False}


def scheduleReminders():
    """Prepare the attendance-shortage reminder job."""
    return runJob(["send_sms", "--shortage"])


def main():
    """Run the attendance tracker demonstration."""
    addStudent("R01", "Aditi")
    addStudent("R02", '=HYPERLINK("http://evil.example","Bharat")')

    register = {}

    for date, status in [
        ("2026-09-01", "P"),
        ("2026-09-02", "P"),
        ("2026-09-03", "L"),
        ("2026-09-04", "P"),
        ("2026-09-05", "H"),
    ]:
        markAttendance("R01", date, status, register)

    for date, status in [
        ("2026-09-01", "P"),
        ("2026-09-01", "P"),
        ("2026-09-02", "A"),
        ("2026-09-03", "A"),
        ("2026-09-04", "A"),
        ("2026-9-3", "P"),
    ]:
        markAttendance("R02", date, status, register)

    markAttendance("R01", "2030-01-01", "P", register)

    print("R01 attendance %:", attendancePercentage("R01"))
    print("R02 attendance %:", attendancePercentage("R02"))
    print("Is 75% eligible?", isEligible(75))
    print("Shortage list:", shortageList())
    print("R02 long absence?", hasLongAbsence("R02"))
    print("R02 latest date:", latestDate("R02"))
    print(
        "Register entries for 2026-09-01:",
        register["2026-09-01"],
    )
    print("Exported to:", exportCsv())
    print("Reminder job:", scheduleReminders())
    print("ERP sync skipped (no network request in this demo)")


if __name__ == "__main__":
    main()
