import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from gtm_agent import data_service, gtm_agent


class StubScoringModel:
    def __init__(self):
        self.prospect_profile = None

    def invoke(self, messages):
        self.prospect_profile = json.loads(messages[1]["content"].split("\n\nProspect profile:\n", 1)[1])
        return gtm_agent.ProspectScore(
            score=100,
            justification="All required technologies are present.",
            rubric_breakdown={
                "revenue_fit": 100,
                "tech_stack_match": 100,
                "segment_fit": 100,
            },
        )


def test_add_then_score_uses_persisted_technology(monkeypatch):
    prospect_id = "LEAD-71001"
    original_record = copy.deepcopy(data_service.PROSPECTS[prospect_id])
    data_service._PROFILES.clear()
    monkeypatch.setattr(gtm_agent, "_scoring_llm", StubScoringModel())

    try:
        profile = gtm_agent.build_prospect_profile.invoke({"prospect_id": prospect_id})
        result = data_service.update_prospect_info(prospect_id, "Kafka")
        offering = data_service.get_offering("OFFER-10005")
        score = gtm_agent.score_prospect.invoke({
            "prospect_profile": profile["prospect_profile"],
            "offering": offering,
        })

        assert result["updated"] is True
        assert "Kafka" in data_service.fetch_tech_stack(prospect_id)
        assert "Kafka" in gtm_agent._scoring_llm.prospect_profile["tech_stack"]
        assert score["rubric_breakdown"]["tech_stack_match"] == 100
    finally:
        data_service.PROSPECTS[prospect_id] = original_record
        data_service._PROFILES.clear()
