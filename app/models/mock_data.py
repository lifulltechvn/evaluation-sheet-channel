EMPLOYEES_DB: dict[str, dict] = {
    "EMP001": {
        "employee_id": "EMP001",
        "name": "Nguyen Van A",
        "email": "a@example.com",
        "position": "application_engineer",
        "grade": "G2",
    },
    "EMP002": {
        "employee_id": "EMP002",
        "name": "Tran Thi B",
        "email": "b@example.com",
        "position": "bse",
        "grade": "G1",
    },
    "EMP003": {
        "employee_id": "EMP003",
        "name": "Le Van C",
        "email": "c@example.com",
        "position": "qa",
        "grade": "G3",
    },
    "EMP004": {
        "employee_id": "EMP004",
        "name": "Pham Thi D",
        "email": "d@example.com",
        "position": "hr",
        "grade": "G0",
    },
    "EMP005": {
        "employee_id": "EMP005",
        "name": "Hoang Van E",
        "email": "e@example.com",
        "position": "admin",
        "grade": "G1",
    },
}

SHEETS_DB: dict[str, dict] = {}

HISTORY_DB: dict[str, list] = {
    "EMP001": [
        {
            "period": "2025-H2",
            "grade": "G2",
            "position": "application_engineer",
            "total_score": 82,
            "google_sheet_url": "https://docs.google.com/spreadsheets/d/mock-2025h2-001",
        },
        {
            "period": "2025-H1",
            "grade": "G1",
            "position": "application_engineer",
            "total_score": 75,
            "google_sheet_url": "https://docs.google.com/spreadsheets/d/mock-2025h1-001",
        },
    ],
    "EMP002": [
        {
            "period": "2025-H2",
            "grade": "G1",
            "position": "bse",
            "total_score": 78,
            "google_sheet_url": "https://docs.google.com/spreadsheets/d/mock-2025h2-002",
        },
    ],
}

SCORING_RULES: dict[str, dict] = {
    "application_engineer": {
        "G0": {"programming": 5, "communication": 3, "teamwork": 2},
        "G1": {"programming": 1, "communication": 4, "teamwork": 3, "leadership": 2},
        "G2": {"programming": 1, "communication": 3, "teamwork": 3, "leadership": 3},
    },
    "bse": {
        "G0": {"programming": 4, "communication": 4, "japanese": 2},
        "G1": {"programming": 2, "communication": 4, "japanese": 2, "leadership": 2},
    },
    "qa": {
        "G0": {"testing": 5, "communication": 3, "documentation": 2},
        "G1": {"testing": 3, "communication": 3, "documentation": 2, "leadership": 2},
    },
    "hr": {
        "G0": {"hr_knowledge": 5, "communication": 3, "organization": 2},
    },
    "admin": {
        "G0": {"admin_skills": 5, "communication": 3, "organization": 2},
    },
}
