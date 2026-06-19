"""fmcg_ctas_gemini_agent.py

LLM-first Complaint Triage Agent for an FMCG copilot, integrated with Gemini.

Flow:
1) Complaint ID in
2) Fetch complaint from CMS via injected client
3) Retrieve supporting context via injected RAG client
4) Ask Gemini to return structured triage JSON
5) Validate and normalize the model output
6) Create ticket via injected ticket client
7) Return final recommendation + ticket metadata

This file intentionally does NOT implement internal endpoints.
It is designed to be plugged into your existing CMS / RAG / TGS endpoints.

Gemini integration notes:
- Uses the Google GenAI SDK (google-genai), which Google documents as the official production-ready SDK.
- Uses generateContent with structured JSON output via response_mime_type="application/json".
- The generateContent API remains supported; Google currently recommends it for stable production use.
"""

from __future__ import annotations
from fastapi import APIRouter
from fastapi.responses import Response,JSONResponse
from fastapi.requests import Request
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable
import json
import os
import re
import sys
from dms_instance import dms
from RRS import rrs
from datetime import datetime
try:
    from google import genai
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Missing dependency: google-genai. Install with: pip install -U google-genai"
    ) from exc


# =============================================================================
# Interfaces
# =============================================================================


@runtime_checkable
class StateStore(Protocol):
    def save_ctas_result(self, cid: str, result: Dict[str, Any]) -> None:
        ...


# =============================================================================
# Domain models
# =============================================================================


class Severity(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class Priority(str, Enum):
    P3 = "P3"
    P2 = "P2"
    P1 = "P1"
    P0 = "P0"


ALLOWED_DEPARTMENTS = {
    "Quality Control",
    "Quality Assurance",
    "Manufacturing",
    "Supply Chain",
    "Logistics",
    "Customer Support",
    "Regulatory",
    "Regulatory / QA",
}

ALLOWED_SEVERITIES = {s.value for s in Severity}
ALLOWED_PRIORITIES = {p.value for p in Priority}

PRIORITY_BY_SEVERITY = {
    Severity.CRITICAL: Priority.P0,
    Severity.HIGH: Priority.P1,
    Severity.MEDIUM: Priority.P2,
    Severity.LOW: Priority.P3,
}

DEFAULT_PROMPT_TEMPLATE = """You are an FMCG complaint triage expert.

You will receive a customer complaint and RAG-retrieved context from SOPs, product docs,
and similar complaints.

Return ONLY valid JSON with this schema:
{{
  "category": "Packaging Issue | Quality Issue | Labeling Issue | Supply Chain Issue | Manufacturing Issue | Customer Experience Issue | General Issue",
  "severity": "Low | Medium | High | Critical",
  "department": "one valid department from the allowed list",
  "recommended_action": "clear and actionable operational recommendation",
  "root_cause": "short root cause hypothesis",
  "confidence": 0.0,
  "priority": "P3 | P2 | P1 | P0"
}}

Allowed departments:
- Quality Control
- Quality Assurance
- Manufacturing
- Supply Chain
- Logistics
- Customer Support
- Regulatory
- Regulatory / QA

Rules:
- Use the complaint + retrieved context to infer the answer.
- Severity must reflect customer impact and business risk.
- Recommended action must be operational, not generic.
- Confidence must be a number between 0 and 1.
- Do not include markdown, explanations, or code fences.

Complaint:
{complaint}

Retrieved Context:
{context}
"""


@dataclass(slots=True)
class CTASEvidence:
    source: str
    text: str


@dataclass(slots=True)
class CTASDecision:
    cid: str
    category: str
    severity: Severity
    department: str
    priority: Priority
    recommended_action: str
    root_cause: str
    ticket_created: bool
    tid: Optional[str]
    confidence: float
    evidence: List[CTASEvidence]
    gemini_output: Dict[str, Any]
    raw_retrieval: str
    complaint_snapshot: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["severity"] = self.severity.value
        payload["priority"] = self.priority.value
        payload["evidence"] = [asdict(item) for item in self.evidence]
        return payload


# =============================================================================
# Helpers
# =============================================================================


def _safe_join(parts: List[str]) -> str:
    return " ".join(p for p in parts if p).strip()


def _extract_text(obj: Dict[str, Any]) -> str:
    if not isinstance(obj, dict):
        return str(obj)
    for key in ("retrieved_context", "context", "CONTEXT", "text", "result", "data"):
        val = obj.get(key)
        if isinstance(val, str):
            return val
        if isinstance(val, list):
            return " ".join(str(x) for x in val)
        if isinstance(val, dict):
            return " ".join(f"{k}:{v}" for k, v in val.items())
    return " ".join(f"{k}:{v}" for k, v in obj.items())


def _extract_json(text: str) -> Dict[str, Any]:
    """Best-effort JSON extraction from Gemini output."""
    if text is None:
        raise ValueError("Gemini returned empty output")

    text = text.strip()

    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        chunk = match.group(0)
        try:
            parsed = json.loads(chunk)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass

    raise ValueError(f"Gemini output was not valid JSON: {text[:300]}")


# =============================================================================
# Gemini wrapper
# =============================================================================


class GeminiClient:
    """Thin wrapper around the Google GenAI SDK."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Missing GEMINI_API_KEY")

        self.model = model or os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        self.client = genai.Client(api_key=api_key)

    def generate_json(self, prompt: str) -> Dict[str, Any]:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "temperature": 0.2,
            },
        )

        # The SDK response object exposes text for text responses.
        raw_text = getattr(response, "text", None)
        if raw_text is None:
            # Fallback for unusual response shapes.
            raw_text = str(response)

        return _extract_json(raw_text)


# =============================================================================
# Agent
# =============================================================================


class CTASAgent(GeminiClient):
    def __init__(
        self,
        gemini_client:GeminiClient,
        state_store: Optional[StateStore] = None,
        *,
        prompt_template: str = DEFAULT_PROMPT_TEMPLATE,
        confidence_floor: float = 0.35,
    ) -> None:
        self.state_store = state_store
        self.prompt_template = prompt_template
        self.confidence_floor = confidence_floor
        self.gemini_client = gemini_client

    def analyze(self, cid: int) -> Dict[str, Any]:
        if not cid:
            raise ValueError("CID cannot be empty")

        if(type(cid) == str):
            cid = int(cid)
        complaint = dms.Get_Complaint(cid)
        if not complaint[0]:
            raise LookupError(f"Complaint not found for CID={cid}")

        retrieval_query = self._build_retrieval_query(complaint[1])
        retrieval = str(rrs.RRS_Retrive_offline(retrieval_query))
        # context_text = _extract_text(retrieval)
        context_text = retrieval

        gemini_output = self._run_gemini(complaint=complaint[1], context_text=context_text)

        category = self._normalize_category(gemini_output.get("category"))
        severity = self._normalize_severity(gemini_output.get("severity"), complaint[1], context_text)
        department = self._normalize_department(gemini_output.get("department"), category)
        priority = self._normalize_priority(gemini_output.get("priority"), severity)
        recommended_action = self._normalize_text_field(
            gemini_output.get("recommended_action"),
            fallback=f"Review complaint and execute {department} workflow.",
        )
        root_cause = self._normalize_text_field(
            gemini_output.get("root_cause"),
            fallback="Insufficient evidence in complaint and retrieval context.",
        )
        confidence = self._normalize_confidence(gemini_output.get("confidence"))

        ticket = dms.Create_Ticket(
            cid,
            department,
            str(priority.value),
            False,
            datetime.now().timestamp(),
            recommended_action+"\n"+root_cause
        )
        tid = 1

        evidence = self._build_evidence(complaint[1], retrieval, gemini_output, recommended_action, root_cause)

        decision = CTASDecision(
            cid=str(cid),
            category=category,
            severity=severity,
            department=department,
            priority=priority,
            recommended_action=recommended_action,
            root_cause=root_cause,
            ticket_created=True,
            tid=str(tid),
            confidence=confidence,
            evidence=evidence,
            gemini_output=gemini_output,
            raw_retrieval=retrieval,
            complaint_snapshot=complaint[1],
        )

        result = decision.to_dict()
        if self.state_store is not None:
            self.state_store.save_ctas_result(str(cid), result)
        return result

    def _build_retrieval_query(self, complaint: Dict[str, Any]) -> str:
        parts = [
            complaint.get("CID", ""),
            complaint.get("CUS", ""),
            complaint.get("PID", ""),
            complaint.get("PNM", ""),
            complaint.get("PCAT", ""),
            complaint.get("CDES", ""),
        ]
        base = _safe_join([str(p) for p in parts if p])
        return _safe_join([base, "sop", "similar complaints", "resolution", "root cause"])

    def _run_gemini(self, complaint: Dict[str, Any], context_text: str) -> Dict[str, Any]:
        prompt = self.prompt_template.format(
            complaint=json.dumps(complaint, ensure_ascii=False, indent=2),
            context=context_text,
        )
        return self.gemini_client.generate_json(prompt)

    def _normalize_category(self, value: Any) -> str:
        text = str(value).strip() if value is not None else ""
        return text if text else "General Issue"

    def _normalize_severity(self, value: Any, complaint: Dict[str, Any], context_text: str) -> Severity:
        text = str(value).strip().capitalize() if value is not None else ""
        if text in ALLOWED_SEVERITIES:
            return Severity(text)
        return self._fallback_severity(complaint, context_text)

    def _normalize_department(self, value: Any, category: str) -> str:
        text = str(value).strip() if value is not None else ""
        if text in ALLOWED_DEPARTMENTS:
            return text
        if category == "Packaging Issue":
            return "Quality Control"
        if category == "Quality Issue":
            return "Quality Assurance"
        if category == "Labeling Issue":
            return "Regulatory / QA"
        if category == "Supply Chain Issue":
            return "Supply Chain"
        if category == "Manufacturing Issue":
            return "Manufacturing"
        if category == "Customer Experience Issue":
            return "Customer Support"
        return "Quality Control"

    def _normalize_priority(self, value: Any, severity: Severity) -> Priority:
        text = str(value).strip() if value is not None else ""
        if text in ALLOWED_PRIORITIES:
            return Priority(text)
        return PRIORITY_BY_SEVERITY[severity]

    def _normalize_text_field(self, value: Any, fallback: str) -> str:
        text = str(value).strip() if value is not None else ""
        return text if text else fallback

    def _normalize_confidence(self, value: Any) -> float:
        try:
            confidence = float(value)
            if 0.0 <= confidence <= 1.0:
                return confidence
        except Exception:
            pass
        return self.confidence_floor

    def _fallback_severity(self, complaint: Dict[str, Any], context_text: str) -> Severity:
        corpus = _safe_join([json.dumps(complaint, ensure_ascii=False), context_text]).lower()
        if any(k in corpus for k in ["contamination", "unsafe", "recall", "injury", "hazard"]):
            return Severity.CRITICAL
        if any(k in corpus for k in ["batch", "repeated", "multiple", "widespread", "leaking", "spoilage"]):
            return Severity.HIGH
        if any(k in corpus for k in ["broken", "missing", "wrong", "damage", "issue"]):
            return Severity.MEDIUM
        return Severity.LOW

    def _build_evidence(
        self,
        complaint: Dict[str, Any],
        retrieval: str,
        gemini_output: Dict[str, Any],
        recommended_action: str,
        root_cause: str,
    ) -> List[CTASEvidence]:
        items: List[CTASEvidence] = []

        complaint_text = complaint.get("CDES") or complaint.get("description") or "Complaint details unavailable"
        items.append(CTASEvidence(source="CMS", text=str(complaint_text)))

        retrieved_context = retrieval
        if retrieved_context:
            items.append(CTASEvidence(source="RAG", text=retrieved_context[:1000]))

        gemini_summary = {
            "category": gemini_output.get("category"),
            "severity": gemini_output.get("severity"),
            "department": gemini_output.get("department"),
            "confidence": gemini_output.get("confidence"),
            "root_cause": root_cause,
        }
        items.append(CTASEvidence(source="Gemini", text=json.dumps(gemini_summary, ensure_ascii=False)))
        items.append(CTASEvidence(source="CTAS", text=recommended_action))
        return items


# =============================================================================
# Local test doubles
# =============================================================================


class InMemoryStateStore:
    def __init__(self) -> None:
        self.storage: Dict[str, Dict[str, Any]] = {}

    def save_ctas_result(self, cid: str, result: Dict[str, Any]) -> None:
        self.storage[cid] = result

router = APIRouter()

@router.post("/CTAS/analyze")
async def Analysis(request:Request):
    _data = await request.json()
    gemini_client = GeminiClient(
        api_key=os.environ.get("GEMINI_API_KEY"),
        model=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
    )
    Agent = CTASAgent(
        gemini_client,
        state_store=InMemoryStateStore(),
    )
    return JSONResponse(Agent.analyze(_data["CID"]),200)