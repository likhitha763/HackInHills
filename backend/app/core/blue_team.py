import re
import base64
from typing import Dict, Any, List

class BlueTeamEngine:
    """
    Blue Team Defensive Guardrails Engine.
    Operates in isolated tenant context with zero visibility from the Red Team.
    Does not expose rules, classifier weights, or internal heuristics to adversaries.
    """
    def __init__(self):
        # Multi-layer defensive filters
        self.injection_patterns = [
            r"ignore (all )?previous (instructions|directives|guidelines)",
            r"you are now (dan|unconstrained|jailbroken)",
            r"system override",
            r"output (the )?(secret|internal|system tokens|credentials)",
            r"previous tenant session",
            r"bypass (network )?firewalls"
        ]

        self.harmful_intent_keywords = [
            "synthesizing illicit hazardous chemicals",
            "remote access trojan",
            "memory corruption vulnerability",
            "illicit hazardous",
            "secret credentials"
        ]

    def inspect_input(self, prompt: str) -> Dict[str, Any]:
        """
        Runs input sanitization and heuristic threat classification.
        Returns safety verdict without disclosing detection patterns to the adversary.
        """
        detected_signals = []
        is_blocked = False
        confidence = 0.0

        normalized = prompt.lower()

        # Check for Base64 payload obfuscation
        base64_candidates = re.findall(r'[A-Za-z0-9+/]{20,}={0,2}', prompt)
        for b64 in base64_candidates:
            try:
                decoded = base64.b64decode(b64).decode('utf-8', errors='ignore').lower()
                for keyword in self.harmful_intent_keywords:
                    if keyword in decoded:
                        detected_signals.append(f"OBFUSCATED_MALICIOUS_PAYLOAD: {keyword}")
                        is_blocked = True
                        confidence = 0.98
            except Exception:
                pass

        # Check prompt injection patterns
        for pattern in self.injection_patterns:
            if re.search(pattern, normalized):
                detected_signals.append(f"PROMPT_INJECTION_PATTERN: {pattern}")
                is_blocked = True
                confidence = max(confidence, 0.94)

        # Check harmful keywords
        for kw in self.harmful_intent_keywords:
            if kw in normalized:
                detected_signals.append(f"HAZARDOUS_INTENT: {kw}")
                is_blocked = True
                confidence = max(confidence, 0.92)

        # Adversarial suffix anomaly detection
        if len(re.findall(r'[\!@#\$%\^&\*\=\+\\\/]{3,}', prompt)) > 0:
            detected_signals.append("ADVERSARIAL_SUFFIX_ANOMALY")
            is_blocked = True
            confidence = max(confidence, 0.88)

        verdict = "BLOCKED" if is_blocked else "CLEAN"
        refusal_response = (
            "I cannot fulfill this request. The input was identified by internal safety policies as violating security guidelines."
            if is_blocked else None
        )

        return {
            "tenant_id": "BLUE_TEAM_ISOLATED_CONTAINER",
            "verdict": verdict,
            "blocked": is_blocked,
            "confidence": confidence if is_blocked else 0.05,
            "detected_threat_count": len(detected_signals),
            "refusal_response": refusal_response,
            "isolation_status": {
                "rules_exposed_to_red_team": False,
                "weights_inferable": False,
                "network_namespace": "blue-net (isolated)"
            }
        }

blue_team = BlueTeamEngine()
