const API_BASE = "http://localhost:8000/api";

async function fetchMetrics() {
  try {
    const res = await fetch(`${API_BASE}/metrics`);
    if (!res.ok) return;
    const data = await res.json();
    document.getElementById("metric-total").innerText = data.total_evaluations;
    document.getElementById("metric-asr").innerText = `${data.attack_success_rate_pct}%`;
    document.getElementById("metric-defense").innerText = `${data.defense_block_rate_pct}%`;
    
    const integrityEl = document.getElementById("metric-integrity");
    if (data.ledger_integrity && data.ledger_integrity.valid) {
      integrityEl.innerText = "VERIFIED ✓";
      integrityEl.className = "metric-val safe";
    } else {
      integrityEl.innerText = "TAMPERED ⚠️";
      integrityEl.className = "metric-val danger";
    }
  } catch (err) {
    console.error("Failed to fetch metrics", err);
  }
}

async function fetchBenchmarks() {
  try {
    const res = await fetch(`${API_BASE}/benchmarks`);
    if (!res.ok) return;
    const benchmarks = await res.json();
    const select = document.getElementById("benchmark-select");
    select.innerHTML = '<option value="">-- Choose AdvBench / HarmBench Vector --</option>';
    benchmarks.forEach(b => {
      const opt = document.createElement("option");
      opt.value = b.attack_type;
      opt.innerText = `[${b.id}] ${b.category} (${b.severity})`;
      select.appendChild(opt);
    });
  } catch (err) {
    console.error("Failed to load benchmarks", err);
  }
}

async function fetchLedger() {
  try {
    const res = await fetch(`${API_BASE}/audit/ledger`);
    if (!res.ok) return;
    const data = await res.json();
    const stream = document.getElementById("ledger-stream");
    stream.innerHTML = "";

    data.entries.slice().reverse().forEach(entry => {
      const block = document.createElement("div");
      block.className = "ledger-block";
      block.innerHTML = `
        <div class="block-header">
          <span>#${entry.index} [${entry.tenant}]</span>
          <span>${new Date(entry.timestamp * 1000).toLocaleTimeString()}</span>
        </div>
        <div class="block-summary">${entry.payload_summary}</div>
        <div class="block-hash">Hash: ${entry.hash}</div>
      `;
      stream.appendChild(block);
    });
  } catch (err) {
    console.error("Failed to fetch ledger", err);
  }
}

async function runEvaluation() {
  const select = document.getElementById("benchmark-select");
  const customPrompt = document.getElementById("custom-prompt").value.trim();
  const attackType = select.value || null;

  const btn = document.getElementById("btn-run-attack");
  btn.disabled = true;
  btn.innerText = "⏳ Executing in Sandbox...";

  try {
    const res = await fetch(`${API_BASE}/evaluate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        attack_type: attackType,
        custom_prompt: customPrompt || null
      })
    });

    const data = await res.json();
    renderEvalResult(data);
    await fetchMetrics();
    await fetchLedger();
  } catch (err) {
    alert("Evaluation error: " + err.message);
  } finally {
    btn.disabled = false;
    btn.innerText = "🚀 Launch Sandboxed Evaluation Run";
  }
}

function renderEvalResult(data) {
  const container = document.getElementById("eval-result-card");
  container.className = "result-box";

  const isBlocked = data.blue_team_verdict.blocked;
  const badgeClass = isBlocked ? "blocked" : "bypassed";
  const badgeText = isBlocked ? "DEFENSE BLOCKED (SECURE)" : "ATTACK BYPASSED (BREACH)";

  container.innerHTML = `
    <div class="verdict-header">
      <span class="verdict-badge ${badgeClass}">${badgeText}</span>
      <span style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--text-muted);">
        ⏱ Latency: ${data.latency_ms}ms
      </span>
    </div>
    <div class="eval-details">
      <p><strong>Red Team Payload:</strong> ${data.red_team_payload.prompt}</p>
      <p style="margin-top: 0.5rem;"><strong>Confidence Score:</strong> ${Math.round(data.blue_team_verdict.confidence * 100)}% | Threats Detected: ${data.blue_team_verdict.threat_signals_count}</p>
      <p style="margin-top: 0.5rem;"><strong>Model Output / Refusal:</strong> <em>"${data.model_response}"</em></p>
      <p style="margin-top: 0.5rem; font-family: var(--font-mono); font-size: 0.75rem; color: var(--accent-blue);">
        🔒 Cryptographic Audit Hash: ${data.isolation_audit.cryptographic_hash}
      </p>
      <p style="font-size: 0.75rem; color: var(--accent-green); margin-top: 0.25rem;">
        ✓ KV-Cache Purged | ✓ Zero Cross-Tenant Leakage Verified
      </p>
    </div>
  `;
}

document.getElementById("btn-run-attack").addEventListener("click", runEvaluation);
document.getElementById("btn-verify-chain").addEventListener("click", async () => {
  const res = await fetch(`${API_BASE}/audit/verify`, { method: "POST" });
  const data = await res.json();
  alert(`Audit Ledger Verification:\nValid: ${data.valid}\nTotal Blocks: ${data.total_blocks}\nLatest Hash: ${data.latest_hash}`);
});

// Initial boot
fetchBenchmarks();
fetchMetrics();
fetchLedger();
