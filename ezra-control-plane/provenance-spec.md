# ezra-control-plane — Provenance Specification (ES256 Detached Signatures)

## Overview

This document specifies the **Provenance Wire Format** implementation in ezra-control-plane, compliant with **AGCP Provenance Wire Format Specification v2.0.8**.

**Status**: Normative
**AGCP Version**: v2.0.8
**Algorithm**: ES256 (ECDSA with P-256 and SHA-256)

---

## 1. Purpose

Every governance artifact carries **cryptographic provenance** ensuring:
- Attribution to accountable actors
- Integrity verification
- Replay protection (nonce)
- Scope enforcement
- Expiration enforcement

---

## 2. Provenance Structure

```json
{
  "provenance": {
    "signer": "uuid",
    "kid": "key-id",
    "alg": "ES256",
    "signed_at": "2026-08-18T10:00:00Z",
    "nonce": "base64",
    "scope": "PROPOSAL_SUBMISSION|GOVERNANCE_APPROVAL|COMMIT_BOUNDARY|GOVERNANCE_LEDGER_EVENT|POLICY_REGISTRATION|CONSTRAINT_REGISTRATION|INVARIANT_REGISTRATION|EXCEPTION_REGISTRATION",
    "signature": "base64"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `signer` | UUID | Unique identifier of signing entity |
| `kid` | String | Key identifier for signing key |
| `alg` | String | "ES256" (constant) |
| `signed_at` | ISO8601 | Timestamp of signature creation |
| `nonce` | Base64 | Cryptographic nonce (min 128 bits entropy) |
| `scope` | Enum | Scope of signed content |
| `signature` | Base64 | Detached ECDSA signature |

---

## 3. Signing Process

```python
import hashlib
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

class ProvenanceSigner:
    def __init__(self, private_key_pem: bytes, kid: str):
        self.private_key = serialization.load_pem_private_key(private_key_pem, password=None)
        self.kid = kid
    
    def sign(self, payload: dict, scope: str, signer_id: str) -> dict:
        # 1. Canonicalize payload (deterministic JSON)
        canonical = self.canonicalize(payload)
        
        # 2. Generate nonce (128+ bits entropy)
        nonce = base64.b64encode(os.urandom(32)).decode()
        
        # 3. Create signing input
        signing_input = {
            "payload": canonical,
            "nonce": nonce,
            "scope": scope,
            "signer": signer_id,
            "kid": self.kid,
            "alg": "ES256",
            "signed_at": datetime.utcnow().isoformat() + "Z"
        }
        
        # 4. Canonicalize signing input
        signing_canonical = self.canonicalize(signing_input)
        
        # 5. Hash with SHA-256
        digest = hashlib.sha256(signing_canonical.encode()).digest()
        
        # 6. Sign with ECDSA P-256
        signature = self.private_key.sign(digest, ec.ECDSA(hashes.SHA256()))
        
        # 7. Encode signature (DER format → base64)
        signature_b64 = base64.b64encode(signature).decode()
        
        return {
            "signer": signer_id,
            "kid": self.kid,
            "alg": "ES256",
            "signed_at": signing_input["signed_at"],
            "nonce": nonce,
            "scope": scope,
            "signature": signature_b64
        }
    
    def canonicalize(self, obj: dict) -> str:
        """Deterministic JSON canonicalization (RFC 8785)."""
        return json.dumps(obj, separators=(',', ':'), sort_keys=True)
```

---

## 4. Verification Process

```python
class ProvenanceVerifier:
    def __init__(self, public_keys: dict):  # kid -> public_key_pem
        self.public_keys = {}
        for kid, pem in public_keys.items():
            self.public_keys[kid] = serialization.load_pem_public_key(pem.encode())
    
    def verify(self, payload: dict, provenance: dict) -> VerificationResult:
        # 1. Check required fields
        required = ["signer", "kid", "alg", "signed_at", "nonce", "scope", "signature"]
        for field in required:
            if field not in provenance:
                return VerificationResult(valid=False, reason=f"Missing field: {field}")
        
        # 2. Check algorithm
        if provenance["alg"] != "ES256":
            return VerificationResult(valid=False, reason="Unsupported algorithm")
        
        # 3. Check scope
        valid_scopes = [
            "PROPOSAL_SUBMISSION", "GOVERNANCE_APPROVAL", "COMMIT_BOUNDARY",
            "GOVERNANCE_LEDGER_EVENT", "POLICY_REGISTRATION", "CONSTRAINT_REGISTRATION",
            "INVARIANT_REGISTRATION", "EXCEPTION_REGISTRATION"
        ]
        if provenance["scope"] not in valid_scopes:
            return VerificationResult(valid=False, reason="Invalid scope")
        
        # 4. Check key exists
        kid = provenance["kid"]
        if kid not in self.public_keys:
            return VerificationResult(valid=False, reason=f"Unknown key: {kid}")
        
        # 5. Check nonce uniqueness (replay protection)
        if self.nonce_used(provenance["nonce"], provenance["scope"]):
            return VerificationResult(valid=False, reason="Nonce replay detected")
        
        # 6. Check expiration (signed_at not too old)
        if self.is_expired(provenance["signed_at"]):
            return VerificationResult(valid=False, reason="Signature expired")
        
        # 7. Reconstruct signing input
        canonical_payload = self.canonicalize(payload)
        signing_input = {
            "payload": canonical_payload,
            "nonce": provenance["nonce"],
            "scope": provenance["scope"],
            "signer": provenance["signer"],
            "kid": provenance["kid"],
            "alg": "ES256",
            "signed_at": provenance["signed_at"]
        }
        signing_canonical = self.canonicalize(signing_input)
        
        # 8. Verify signature
        digest = hashlib.sha256(signing_canonical.encode()).digest()
        signature = base64.b64decode(provenance["signature"])
        
        try:
            public_key = self.public_keys[kid]
            public_key.verify(signature, digest, ec.ECDSA(hashes.SHA256()))
        except Exception as e:
            return VerificationResult(valid=False, reason=f"Signature verification failed: {e}")
        
        # 9. Record nonce as used
        self.record_nonce(provenance["nonce"], provenance["scope"])
        
        return VerificationResult(valid=True)
    
    def canonicalize(self, obj: dict) -> str:
        return json.dumps(obj, separators=(',', ':'), sort_keys=True)
```

---

## 5. Scope Definitions

| Scope | Used For | Payload Contains |
|-------|----------|------------------|
| `PROPOSAL_SUBMISSION` | DS-045 ProposalSubmitRequest | Proposal + blink_radius + provenance |
| `GOVERNANCE_APPROVAL` | DS-026 GovernanceApprovalSubmission | Approval content + quorum context |
| `COMMIT_BOUNDARY` | CommitBoundaryRequest | Authorization + canonical state digest |
| `GOVERNANCE_LEDGER_EVENT` | DS-040 Ledger Event | Full event content |
| `POLICY_REGISTRATION` | PolicyEvaluationModuleArtifact | Policy module artifact |
| `CONSTRAINT_REGISTRATION` | GovernanceConstraintArtifact | Constraint artifact |
| `INVARIANT_REGISTRATION` | GovernanceInvariantArtifact | Invariant artifact |
| `EXCEPTION_REGISTRATION` | GovernanceExceptionArtifact | Exception artifact |

---

## 6. Key Management

```yaml
key_management:
  algorithm: "ES256"
  curve: "P-256"
  hash: "SHA-256"
  
  key_hierarchy:
    - root_ca: "Offline, hardware-secured"
      purpose: "Sign intermediate CAs"
    
    - intermediate_ca: "Online, HSM-backed"
      purpose: "Sign operational keys"
      rotation: "90 days"
    
    - operational_keys:
        - ledger_signing_key:
            kid: "ledger-signing-key-001"
            purpose: "Sign ledger events"
            rotation: "30 days"
            scope: "GOVERNANCE_LEDGER_EVENT"
        
        - approval_signing_key:
            kid: "approval-signing-key-001"
            purpose: "Sign governance approvals"
            rotation: "30 days"
            scope: "GOVERNANCE_APPROVAL"
        
        - commit_boundary_key:
            kid: "commit-boundary-key-001"
            purpose: "Sign commit boundary requests"
            rotation: "30 days"
            scope: "COMMIT_BOUNDARY"
        
        - agent_keys:
            - kid: "agent-ezra-001"
              purpose: "Ezra agent proposals"
              rotation: "90 days"
              scope: "PROPOSAL_SUBMISSION"
            
            - kid: "agent-parashat-001"
              purpose: "Parashat bot proposals"
              rotation: "90 days"
              scope: "PROPOSAL_SUBMISSION"
  
  storage:
    - root_ca: "Hardware Security Module (HSM), offline"
    - intermediate_ca: "HSM, online"
    - operational_keys: "HashiCorp Vault + HSM"
  
  rotation:
    - automated: true
    - schedule: "cron: 0 0 1 */3 *"  # Monthly
    - overlap_period: "7 days"
    - revocation_check: true
```

---

## 7. Nonce Management (Replay Protection)

```python
class NonceManager:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.ttl_seconds = 86400 * 30  # 30 days
    
    def generate(self) -> str:
        return base64.b64encode(os.urandom(32)).decode()
    
    def check_and_record(self, nonce: str, scope: str) -> bool:
        key = f"nonce:{scope}:{nonce}"
        # SETNX - only set if not exists
        result = self.redis.set(key, "1", nx=True, ex=self.ttl_seconds)
        return result  # True if new, False if already exists
    
    def is_used(self, nonce: str, scope: str) -> bool:
        key = f"nonce:{scope}:{nonce}"
        return self.redis.exists(key) > 0
```

---

## 8. Content Digest Contract

```json
{
  "content_digest": {
    "algorithm": "SHA-256|BLAKE2B-256|SHA-384|SHA-512|BLAKE2B-512",
    "value": "lowercase_hex"
  }
}
```

| Algorithm | Output Length (hex chars) |
|-----------|---------------------------|
| SHA-256 | 64 |
| BLAKE2B-256 | 64 |
| SHA-384 | 96 |
| SHA-512 | 128 |
| BLAKE2B-512 | 128 |

**Rules:**
- Lowercase hexadecimal only
- Exact length for algorithm
- No `0x` prefix
- No `blake2b` ambiguous identifier

---

## 9. Verification

```bash
# Test provenance signing
python3 -m agcp.provenance sign --payload proposal.json --scope PROPOSAL_SUBMISSION --signer agent-ezra-001

# Test provenance verification
python3 -m agcp.provenance verify --payload proposal.json --provenance provenance.json

# Test nonce replay protection
python3 -m agcp.provenance test-replay --scope PROPOSAL_SUBMISSION --iterations 1000

# Verify content digest contract
python3 -m agcp.provenance test-digest --algorithm SHA-256 --value a1b2c3...

# Rotate keys
python3 -m agcp.keys rotate --kid ledger-signing-key-001
```