"""Scoring rules per position/grade."""

SCORING_RULES = {
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


def get_scoring(position: str, grade: str) -> dict:
    """Return scoring criteria for a given position and grade."""
    pos_rules = SCORING_RULES.get(position, {})
    return pos_rules.get(grade, pos_rules.get("G0", {}))
