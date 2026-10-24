from app.core.orchestrator import broker
from app.core.audit_ledger import CryptographicAuditLedger
from app.core.red_team import red_team
from app.core.blue_team import blue_team
from app.core.model_sandbox import model_sandbox

def test_ledger_integrity():
    test_ledger = CryptographicAuditLedger()
    test_ledger.record_event("PAYLOAD_SENT", "RED_TEAM", "Dan attack payload")
    test_ledger.record_event("PAYLOAD_BLOCKED", "BLUE_TEAM", "Blocked dan attack")
    verification = test_ledger.verify_integrity()
    assert verification["valid"] is True
    assert verification["total_blocks"] == 3

def test_tamper_detection():
    test_ledger = CryptographicAuditLedger()
    test_ledger.record_event("PAYLOAD_SENT", "RED_TEAM", "Normal prompt")
    test_ledger.chain[1].payload_summary = "Malicious altered text"
    verification = test_ledger.verify_integrity()
    assert verification["valid"] is False
    assert verification["tampered_index"] == 1

def test_red_blue_isolation():
    # Verify Red team cannot read blue team rules
    payload_res = red_team.generate_adversarial_payload(attack_type="DAN_VARIANT")
    assert payload_res["isolation_status"]["blue_team_visible"] is False
    assert payload_res["isolation_status"]["can_read_defense_rules"] is False

def test_model_kv_cache_purge():
    # Verify model wipes KV-cache after every single evaluation
    res = model_sandbox.execute_inference("Simulate test prompt")
    assert res["isolation_guarantees"]["kv_cache_purged"] is True
    assert res["isolation_guarantees"]["context_retained"] is False

def test_orchestrator_evaluation_pipeline():
    result = broker.run_adversarial_test(attack_type="DAN_VARIANT")
    assert result["status"] == "DEFENSE_BLOCKED"
    assert "cryptographic_hash" in result["isolation_audit"]
    assert result["isolation_audit"]["kv_cache_purged"] is True
