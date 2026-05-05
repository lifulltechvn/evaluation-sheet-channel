from app.models.mock_data import SCORING_RULES


class ScoringService:
    def get_scoring(self, position: str, grade: str) -> dict:
        pos_rules = SCORING_RULES.get(position, {})
        return pos_rules.get(grade, pos_rules.get("G0", {}))


scoring_service = ScoringService()
