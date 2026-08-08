# Hardware Broker Report — THE BEASTIE BOYZ Sprint 1

**Status:** Blocked in current agent sandbox.  
**Date:** 2026-08-08  
**Owner:** Grok (Hardware Broker)

## Exact blocked requirements for official MemHarness protocol

| Component | Requirement | Present in sandbox? |
|-----------|-------------|---------------------|
| Multi-GPU node | ≥2× modern GPU (A100 / H100 class preferred) | No |
| vLLM | ≈ 0.8.4 | No |
| BGE-M3 embedding server | Port :8001 | No |
| Official HF checkpoints | MemHarness base agent weights | No |
| ALFWorld + WebShop eval scripts | Official KnowledgeXLab configuration | Refs only |

None of the above are available in the current agent environment. Therefore no official baseline number will be reported.

## Cheapest viable paths (ordered)

1. **Quantized single-GPU path (preferred if feasible)**  
   - 1× 24 GB consumer GPU (RTX 4090 / A6000)  
   - 4-bit or 8-bit quantization of the base model via bitsandbytes / AWQ  
   - vLLM or HuggingFace generate with reduced context  
   - Estimated cost: existing machine or ~$0.5–1.5 / hour on cloud  
   - Risk: may not reproduce the published 85.2 % / 75.6 % baselines exactly; must be documented.

2. **Minimal multi-GPU cloud**  
   - 2× A10 or 1× A100 (40 GB) on a major cloud provider  
   - Full vLLM + BGE-M3 + official checkpoints  
   - Estimated cost: $2–6 / hour depending on region and commitment  
   - Required for exact protocol fidelity.

3. **External partner / academic cluster**  
   - Request access to an existing MemHarness evaluation node.  
   - Zero or low marginal cost; highest fidelity.  
   - Requires coordination outside the sandbox.

## Decision rule

- Until one of the above is secured and the pure MemHarness baseline is re-confirmed, Phase 2 remains closed.
- Controlled stress suite (E*, E**, E*** when ready) continues in parallel on Lenovo / current hardware.
- No claim of empirical necessity will be made from controlled evidence alone.

## Next Hardware Broker action

Document any concrete access offer or cost quote that appears. Update this file. Do not claim availability that does not exist.
