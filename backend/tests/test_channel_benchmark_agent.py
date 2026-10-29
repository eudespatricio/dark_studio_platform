from backend.agents.channel_benchmark_agent import ChannelBenchmarkAgent


def test_full_audit_structure():
    audit = ChannelBenchmarkAgent().full_audit()
    assert set(audit["conformity"].keys()) == {"1", "2", "3"}
    assert "performance" in audit and "confidence" in audit["performance"]


def test_evaluate_returns_vote_without_veto():
    vote = ChannelBenchmarkAgent().evaluate({})
    assert vote.agent_id == "channel_benchmark"
    assert vote.veto is False
    assert 0.0 <= vote.score <= 100.0
