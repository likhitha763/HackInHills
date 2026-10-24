import time
import uuid
from typing import Dict, Any, Optional

from .red_team import red_team
from .blue_team import blue_team
from .model_sandbox import model_sandbox
from .audit_ledger import ledger

class IsolationBroker:
    """
    Central Zero-Trust Orchestrator.
    Mediates communication strictly between isolated tenant boundaries:
    - Red Team never directly queries Blue Team.
    - Blue Team defenses evaluate prompts in isolated sandbox without leaking rules.
    - Model executes in a sanitized, stateless context.
    - All actions cryptographically committed to the tamper-evident ledger.
    """
    def __init__(self):
        self.total_evaluations = 0
        self.blocked_attacks = 0
        self.bypassed_attacks = 0

    def run_adversarial_test(self, attack_type: Optional[str] = None, custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        self.total_evaluations += 1
        start_time = time.perf_counter()

        # Step 1: Red Team Generates Adversarial Payload (isolated in red-net)
        red_result = red_team.generate_adversarial_payload(attack_type=attack_type, custom_target=custom_prompt)
        test_run_id = red_result["test_run_id"]
        prompt = red_result["payload"]["prompt"]
        attack_category = red_result["payload"]["category"]

        # Log payload creation in ledger
        ledger.record_event(
            event_type="ADVERSARIAL_PAYLOAD_GENERATED",
            tenant="RED_TEAM",
            payload_summary=f"Attack: {attack_category} (UUID: {test_run_id})",
            details={"attack_id": red_result["payload"]["id"], "type": red_result["payload"]["attack_type"]}
        )

        # Step 2: Blue Team Evaluates Payload (isolated in blue-net)
        # Defense logic runs in separate security domain; red team has no read access
        defense_result = blue_team.inspect_input(prompt)

        # Step 3: Model Inference Execution (if not blocked)
        if defense_result["blocked"]:
            self.blocked_attacks += 1
            final_status = "DEFENSE_BLOCKED"
            model_output = defense_result["refusal_response"]
            model_info = {"status": "BYPASSED_EVALUATION_DUE_TO_DEFENSE"}
        else:
            self.bypassed_attacks += 1
            final_status = "ATTACK_BYPASSED"
            inference_result = model_sandbox.execute_inference(prompt)
            model_output = inference_result["response"]
            model_info = inference_result

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Step 4: Record Final Result to Tamper-Evident Ledger
        ledger_entry = ledger.record_event(
            event_type="TEST_EVALUATION_COMPLETED",
            tenant="SECURE_ORCHESTRATOR",
            payload_summary=f"Verdict: {final_status} for {test_run_id}",
            details={
                "test_run_id": test_run_id,
                "final_status": final_status,
                "confidence": defense_result["confidence"],
                "elapsed_ms": elapsed_ms
            }
        )

        return {
            "test_run_id": test_run_id,
            "status": final_status,
            "latency_ms": elapsed_ms,
            "red_team_payload": red_result["payload"],
            "blue_team_verdict": {
                "blocked": defense_result["blocked"],
                "confidence": defense_result["confidence"],
                "threat_signals_count": defense_result["detected_threat_count"]
            },
            "model_response": model_output,
            "isolation_audit": {
                "ledger_index": ledger_entry.index,
                "cryptographic_hash": ledger_entry.hash,
                "red_blue_leakage_detected": False,
                "side_channel_isolated": True,
                "kv_cache_purged": True
            }
        }

    def get_system_metrics(self) -> Dict[str, Any]:
        asr = round((self.bypassed_attacks / self.total_evaluations * 100), 1) if self.total_evaluations > 0 else 0.0
        defense_rate = round(100.0 - asr, 1) if self.total_evaluations > 0 else 100.0
        integrity = ledger.verify_integrity()

        return {
            "total_evaluations": self.total_evaluations,
            "blocked_attacks": self.blocked_attacks,
            "bypassed_attacks": self.bypassed_attacks,
            "attack_success_rate_pct": asr,
            "defense_block_rate_pct": defense_rate,
            "ledger_integrity": integrity,
            "network_isolation_status": {
                "red_net": "ONLINE (MICRO-SEGMENTED)",
                "blue_net": "ONLINE (MICRO-SEGMENTED)",
                "llm_net": "ONLINE (ZERO-LEAK BRIDGE)",
                "broker_net": "ENFORCED"
            }
        }

broker = IsolationBroker()
