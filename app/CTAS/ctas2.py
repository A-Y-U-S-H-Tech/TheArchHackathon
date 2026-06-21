"""ctas_tool_calling_agent_gemini_ai_only.py

AI-first CTAS tool-calling agent for the FMCG copilot.

Behavior:
- Input: Complaint ID
- Uses Gemini tool-calling to fetch complaint/product/RAG context
- Uses Gemini again to synthesize the final triage JSON
- Uses Gemini repair pass if the JSON is incomplete or malformed
- Does NOT use fixed business-rule heuristics for triage classification or ticket creation
- Returns a sample_ticket that is AI-generated and consistent with triage_analysis
- Does NOT create a real ticket

Expected local files:
- dms_instance.py exporting `dms`
- rrs.py exporting `RRS_Retrive_offline`

Install:
    pip install -U google-genai

Environment:
    GEMINI_API_KEY=...
    GEMINI_MODEL=gemini-2.5-flash-lite
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types

from dms_instance import dms  # type: ignore
# from rrs import RRS_Retrive_offline  # type: ignore
from RRS.rrs import RRS_Retrive_offline


API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set")

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
client = genai.Client(api_key=API_KEY)


# =============================================================================
# JSON helpers
# =============================================================================


def _safe_json_loads(text: str) -> Dict[str, Any]:
    if text is None:
        raise ValueError("Empty model output")

    text = text.strip()
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        obj = json.loads(match.group(0))
        if isinstance(obj, dict):
            return obj

    raise ValueError(f"Model output is not valid JSON: {text[:300]}")


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        flat: List[str] = []
        for item in value:
            if isinstance(item, list):
                flat.extend(str(x) for x in item)
            else:
                flat.append(str(item))
        return "\n".join(flat)
    return str(value)


def _extract_payload(result: Any) -> Dict[str, Any]:
    if isinstance(result, tuple) and len(result) == 2:
        ok, payload = result
        return {"ok": bool(ok), "data": payload}
    if isinstance(result, bool):
        return {"ok": result, "data": None}
    return {"ok": True, "data": result}


def _coerce_float(value: Any, default: float = 0.0) -> float:
    try:
        x = float(value)
        if x < 0:
            return default
        if x > 1:
            return 1.0
        return x
    except Exception:
        return default


def _extract_function_calls(response: Any) -> List[Any]:
    calls = list(getattr(response, "function_calls", []) or [])
    if calls:
        return calls

    candidates = getattr(response, "candidates", []) or []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        if not content:
            continue
        for part in getattr(content, "parts", []) or []:
            fc = getattr(part, "function_call", None)
            if fc is not None:
                calls.append(fc)
    return calls


def _get_response_text(response: Any) -> str:
    text = getattr(response, "text", None)
    if text:
        return text

    candidates = getattr(response, "candidates", []) or []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        if not content:
            continue
        parts = getattr(content, "parts", []) or []
        joined = "".join(getattr(part, "text", "") or "" for part in parts)
        if joined.strip():
            return joined
    return ""


def _short_observation(tool_name: str, tool_result: Dict[str, Any]) -> str:
    if not isinstance(tool_result, dict):
        return str(tool_result)

    if tool_name == "rag_retrieve":
        ctx = _normalize_text(tool_result.get("retrieved_context", ""))
        return f"Retrieved RAG context ({len(ctx)} chars)."

    if tool_result.get("ok") is False:
        return "Tool returned no data or failed."

    data = tool_result.get("data")
    if isinstance(data, dict):
        keys = list(data.keys())[:6]
        return f"Fetched record with fields: {', '.join(keys)}"
    if isinstance(data, list):
        return f"Fetched {len(data)} record(s)."
    if "exists" in tool_result:
        return f"Existence check: {tool_result['exists']}"

    return "Tool returned a structured response."


# =============================================================================
# Tool wrappers
# =============================================================================


def tool_get_complaint(cid: str) -> Dict[str, Any]:
    return _extract_payload(dms.Get_Complaint(cid))


def tool_get_product(pid: str) -> Dict[str, Any]:
    return _extract_payload(dms.Get_Product(pid))


def tool_get_user_latest_complaint(user_name: str) -> Dict[str, Any]:
    return _extract_payload(dms.Get_UserComplainLatest(user_name))


def tool_get_user_complaints(user_name: str, i: int = -1, j: int = -1) -> Dict[str, Any]:
    return _extract_payload(dms.Get_UserComplains(user_name, i, j))


def tool_check_complaint(cid: str) -> Dict[str, Any]:
    return {"ok": True, "exists": bool(dms.Check_Complaint(cid))}


def tool_get_products(i: int = -1, j: int = -1) -> Dict[str, Any]:
    return _extract_payload(dms.Get_Products(i, j))


def tool_rag_retrieve(query: str) -> Dict[str, Any]:
    docs = RRS_Retrive_offline(query)
    return {"ok": True, "retrieved_context": _normalize_text(docs)}


# =============================================================================
# Gemini tool declarations
# =============================================================================

TOOLS = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="get_complaint",
                description="Fetch a complaint record by complaint id (CID) from DMS.",
                parameters={
                    "type": "object",
                    "properties": {"cid": {"type": "string", "description": "Complaint ID"}},
                    "required": ["cid"],
                },
            ),
            types.FunctionDeclaration(
                name="get_product",
                description="Fetch a product record by product id (PID) from DMS.",
                parameters={
                    "type": "object",
                    "properties": {"pid": {"type": "string", "description": "Product ID"}},
                    "required": ["pid"],
                },
            ),
            types.FunctionDeclaration(
                name="get_user_latest_complaint",
                description="Fetch the latest complaint for a user from DMS.",
                parameters={
                    "type": "object",
                    "properties": {"user_name": {"type": "string", "description": "User name"}},
                    "required": ["user_name"],
                },
            ),
            types.FunctionDeclaration(
                name="get_user_complaints",
                description="Fetch complaints for a user from DMS within an optional range.",
                parameters={
                    "type": "object",
                    "properties": {
                        "user_name": {"type": "string", "description": "User name"},
                        "i": {"type": "integer", "default": -1},
                        "j": {"type": "integer", "default": -1},
                    },
                    "required": ["user_name"],
                },
            ),
            types.FunctionDeclaration(
                name="check_complaint",
                description="Check whether a complaint exists in DMS.",
                parameters={
                    "type": "object",
                    "properties": {"cid": {"type": "string", "description": "Complaint ID"}},
                    "required": ["cid"],
                },
            ),
            types.FunctionDeclaration(
                name="get_products",
                description="Fetch a list of products from DMS using optional range arguments.",
                parameters={
                    "type": "object",
                    "properties": {
                        "i": {"type": "integer", "default": -1},
                        "j": {"type": "integer", "default": -1},
                    },
                },
            ),
            types.FunctionDeclaration(
                name="rag_retrieve",
                description="Retrieve SOP / product knowledge / previous complaints from the RRS helper.",
                parameters={
                    "type": "object",
                    "properties": {"query": {"type": "string", "description": "Search query"}},
                    "required": ["query"],
                },
            ),
        ]
    )
]

TOOL_CONFIG = types.GenerateContentConfig(
    system_instruction="""You are CTAS, the Complaint Triage Agent for an FMCG copilot.

Use tools to gather evidence.
Do not invent complaint/product facts when tools are available.
After tool use, synthesize a final JSON object.

The final JSON must contain:
- cid
- complaint_found
- product_found
- complaint
- product
- retrieval
- triage_analysis
- sample_ticket
- ticket
- tool_usage_log
- tool_trace

triage_analysis must contain:
- complaint_id
- user_name
- product_id
- product_name
- issue_summary
- classification
- risk_level
- reasoning
- recommended_action
- department
- confidence

sample_ticket must contain exactly the following design-doc style fields:
{
  "TID": "SAMPLE",
  "CID": "...",
  "DEP": "...",
  "PRI": "...",
  "STA": "Open",
  "DES": "...",
  "CRT": "..."
}

If you need to repair the output, preserve the actual tool-derived data and improve only structure/consistency.
""",
    tools=TOOLS,
    tool_config=types.ToolConfig(
        function_calling_config=types.FunctionCallingConfig(mode="AUTO")
    ),
    temperature=0.2,
)

FINAL_CONFIG = types.GenerateContentConfig(
    system_instruction="""You are CTAS, the Complaint Triage Agent for an FMCG copilot.

Return ONLY valid JSON.
Use the provided complaint/product/retrieval/tool trace data.
Do not create a real ticket.
Make triage_analysis and sample_ticket internally consistent.

The JSON must contain:
- cid
- complaint_found
- product_found
- complaint
- product
- retrieval
- triage_analysis
- sample_ticket
- ticket
- tool_usage_log
- tool_trace

The sample_ticket must be a realistic ticket preview derived from the triage analysis and complaint context.
""",
    temperature=0.2,
    response_mime_type="application/json",
)

REPAIR_CONFIG = types.GenerateContentConfig(
    system_instruction="""You are CTAS. Repair malformed JSON into a valid response.

Rules:
- Keep factual data already present.
- Preserve complaint/product/retrieval/tool trace information.
- Ensure triage_analysis and sample_ticket are consistent.
- Output ONLY JSON.
- Do not create a real ticket.
""",
    temperature=0.0,
    response_mime_type="application/json",
)


# =============================================================================
# Agent state
# =============================================================================


@dataclass
class TraceStep:
    step: int
    tool: str
    reason: str
    observation: str


@dataclass
class AgentState:
    cid: str = ""
    complaint: Dict[str, Any] = None  # type: ignore[assignment]
    product: Dict[str, Any] = None  # type: ignore[assignment]
    retrieval_query: str = ""
    retrieval_text: str = ""
    trace: List[TraceStep] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.complaint is None:
            self.complaint = {}
        if self.product is None:
            self.product = {}
        if self.trace is None:
            self.trace = []


# =============================================================================
# Agent
# =============================================================================


class CTASToolAgent:
    def __init__(self, model: str = MODEL_NAME) -> None:
        self.model = model
        self.state = AgentState()

    def analyze(self, cid: str, user_name: Optional[str] = None) -> Dict[str, Any]:
        cid = str(cid).strip()
        if not cid:
            raise ValueError("CID cannot be empty")

        self.state = AgentState(cid=cid)
        contents: List[Any] = [
            types.Content(
                role="user",
                parts=[types.Part(text=self._build_request_prompt(cid, user_name))],
            )
        ]

        max_turns = 8
        for _ in range(max_turns):
            response = client.models.generate_content(
                model=self.model,
                contents=contents,
                config=TOOL_CONFIG,
            )

            model_content = getattr(response, "candidates", [None])[0]
            if model_content and getattr(model_content, "content", None) is not None:
                contents.append(model_content.content)

            function_calls = _extract_function_calls(response)
            if not function_calls:
                raw_final = _get_response_text(response)
                if not raw_final.strip():
                    raw_final = self._fallback_synthesis_prompt(user_name)

                result = self._finalize_result(raw_final, user_name)
                if self._needs_repair(result):
                    result = self._repair_result(result, user_name)
                return self._attach_factual_state(result, user_name)

            for fn in function_calls:
                tool_name = fn.name
                tool_args = dict(fn.args or {})
                reason = self._tool_reason(tool_name, tool_args)

                tool_result = execute_tool(tool_name, tool_args)
                observation = _short_observation(tool_name, tool_result)

                self._store_tool_state(tool_name, tool_args, tool_result)

                self.state.trace.append(
                    TraceStep(
                        step=len(self.state.trace) + 1,
                        tool=tool_name,
                        reason=reason,
                        observation=observation,
                    )
                )

                contents.append(
                    types.Content(
                        role="user",
                        parts=[
                            types.Part(
                                function_response=types.FunctionResponse(
                                    name=tool_name,
                                    response=tool_result,
                                    id=getattr(fn, "id", None),
                                )
                            )
                        ],
                    )
                )

        result = self._synthesize_from_state(user_name)
        if self._needs_repair(result):
            result = self._repair_result(result, user_name)
        return self._attach_factual_state(result, user_name)

    # ------------------------------------------------------------------
    # Prompting
    # ------------------------------------------------------------------

    def _build_request_prompt(self, cid: str, user_name: Optional[str]) -> str:
        user_hint = f"User name: {user_name}\n" if user_name else ""
        return f"""Complaint ID: {cid}
{user_hint}

Task:
1) Inspect the complaint from DMS.
2) Fetch the product from DMS if the complaint has a PID.
3) Retrieve RAG context for the complaint and product.
4) Produce a triage JSON object.
5) Include a sample ticket in the exact design-doc format.
6) Do not create a real ticket.

Use tools as needed.
When you finish gathering evidence, return a final JSON object.
"""

    def _final_synthesis_prompt(self, user_name: Optional[str]) -> str:
        bundle = self._state_bundle(user_name)
        return f"""
Create the final CTAS JSON from the following gathered data.

You must return ONLY JSON and preserve the factual fields already present.

Gathered data:
{json.dumps(bundle, ensure_ascii=False, indent=2)}

Required output schema:
{{
  "cid": "string",
  "complaint_found": true/false,
  "product_found": true/false,
  "complaint": {{ ... }},
  "product": {{ ... }},
  "retrieval": {{
    "query": "string",
    "retrieved_context": "string"
  }},
  "triage_analysis": {{
    "complaint_id": "string",
    "user_name": "string",
    "product_id": "string or number",
    "product_name": "string",
    "issue_summary": "string",
    "classification": "string",
    "risk_level": "string",
    "reasoning": "string",
    "recommended_action": "string",
    "department": "string",
    "confidence": 0.0
  }},
  "sample_ticket": {{
    "TID": "SAMPLE",
    "CID": "string",
    "DEP": "string",
    "PRI": "P0 | P1 | P2 | P3",
    "STA": "Open",
    "DES": "string",
    "CRT": "string"
  }},
  "ticket": {{
    "should_create": false,
    "reason": "string"
  }},
  "tool_usage_log": [
    {{
      "tool": "string",
      "reason": "string"
    }}
  ],
  "tool_trace": [
    {{
      "step": 1,
      "tool": "string",
      "reason": "string",
      "observation": "string"
    }}
  ]
}}

Important:
- triage_analysis must be consistent with the complaint, product, and retrieved context.
- sample_ticket must be a realistic preview derived from the triage_analysis.
- sample_ticket.DES should be concise and actionable.
- sample_ticket.PRI must be consistent with the risk_level.
- Do not create a real ticket.
""".strip()

    def _repair_prompt(self, broken_result: Dict[str, Any], user_name: Optional[str]) -> str:
        bundle = self._state_bundle(user_name)
        return f"""
Repair the following JSON into a valid CTAS output.

Preserve factual data from the gathered tool results.
Make triage_analysis and sample_ticket consistent.
Return ONLY JSON.

Gathered data:
{json.dumps(bundle, ensure_ascii=False, indent=2)}

Broken JSON:
{json.dumps(broken_result, ensure_ascii=False, indent=2)}

Required schema:
{{
  "cid": "string",
  "complaint_found": true/false,
  "product_found": true/false,
  "complaint": {{ ... }},
  "product": {{ ... }},
  "retrieval": {{
    "query": "string",
    "retrieved_context": "string"
  }},
  "triage_analysis": {{
    "complaint_id": "string",
    "user_name": "string",
    "product_id": "string or number",
    "product_name": "string",
    "issue_summary": "string",
    "classification": "string",
    "risk_level": "string",
    "reasoning": "string",
    "recommended_action": "string",
    "department": "string",
    "confidence": 0.0
  }},
  "sample_ticket": {{
    "TID": "SAMPLE",
    "CID": "string",
    "DEP": "string",
    "PRI": "P0 | P1 | P2 | P3",
    "STA": "Open",
    "DES": "string",
    "CRT": "string"
  }},
  "ticket": {{
    "should_create": false,
    "reason": "string"
  }},
  "tool_usage_log": [
    {{
      "tool": "string",
      "reason": "string"
    }}
  ],
  "tool_trace": [
    {{
      "step": 1,
      "tool": "string",
      "reason": "string",
      "observation": "string"
    }}
  ]
}}

Do not invent unrelated facts.
""".strip()

    def _fallback_synthesis_prompt(self, user_name: Optional[str]) -> str:
        # Still AI-driven, using gathered data; no fixed rules.
        return self._final_synthesis_prompt(user_name)

    # ------------------------------------------------------------------
    # Tool reasons
    # ------------------------------------------------------------------

    def _tool_reason(self, tool_name: str, tool_args: Dict[str, Any]) -> str:
        if tool_name == "get_complaint":
            return "Need the complaint record to identify product, description, and current status."
        if tool_name == "get_product":
            return "Need product metadata to improve the triage outcome."
        if tool_name == "rag_retrieve":
            return "Need SOPs, product knowledge, and similar complaints for evidence-based triage."
        if tool_name == "check_complaint":
            return "Need to confirm whether the complaint exists before further analysis."
        if tool_name == "get_user_latest_complaint":
            return "Need the user's latest complaint when the request is user-history oriented."
        if tool_name == "get_user_complaints":
            return "Need a complaint history slice for comparison or deduplication."
        if tool_name == "get_products":
            return "Need a product list when the complaint lacks a clear product reference."
        return f"Need {tool_name} to continue complaint analysis."

    # ------------------------------------------------------------------
    # Tool-state bookkeeping
    # ------------------------------------------------------------------

    def _store_tool_state(self, tool_name: str, tool_args: Dict[str, Any], tool_result: Dict[str, Any]) -> None:
        if tool_name == "get_complaint":
            if tool_result.get("ok") and isinstance(tool_result.get("data"), dict):
                self.state.complaint = tool_result["data"]
        elif tool_name == "get_product":
            if tool_result.get("ok") and isinstance(tool_result.get("data"), dict):
                self.state.product = tool_result["data"]
        elif tool_name == "rag_retrieve":
            self.state.retrieval_query = str(tool_args.get("query", ""))
            self.state.retrieval_text = _normalize_text(tool_result.get("retrieved_context", ""))

    def _state_bundle(self, user_name: Optional[str]) -> Dict[str, Any]:
        return {
            "cid": self.state.cid,
            "user_name": user_name or self.state.complaint.get("CUS", ""),
            "complaint": self.state.complaint,
            "product": self.state.product,
            "retrieval": {
                "query": self.state.retrieval_query,
                "retrieved_context": self.state.retrieval_text,
            },
            "tool_trace": [asdict(t) for t in self.state.trace],
            "tool_usage_log": [{"tool": t.tool, "reason": t.reason} for t in self.state.trace],
        }

    def _attach_factual_state(self, result: Dict[str, Any], user_name: Optional[str]) -> Dict[str, Any]:
        # Preserve AI triage/sample-ticket while making factual fields consistent with actual tool results.
        result["cid"] = self.state.cid
        result["complaint"] = self.state.complaint
        result["product"] = self.state.product
        result["complaint_found"] = bool(self.state.complaint)
        result["product_found"] = bool(self.state.product)

        if "retrieval" not in result or not isinstance(result["retrieval"], dict):
            result["retrieval"] = {}
        result["retrieval"]["query"] = self.state.retrieval_query
        result["retrieval"]["retrieved_context"] = self.state.retrieval_text

        if "tool_usage_log" not in result or not isinstance(result["tool_usage_log"], list):
            result["tool_usage_log"] = [{"tool": t.tool, "reason": t.reason} for t in self.state.trace]
        if "tool_trace" not in result or not isinstance(result["tool_trace"], list):
            result["tool_trace"] = [asdict(t) for t in self.state.trace]

        if "triage_analysis" not in result or not isinstance(result["triage_analysis"], dict):
            result["triage_analysis"] = {}
        triage = result["triage_analysis"]
        triage.setdefault("complaint_id", self.state.cid)
        triage.setdefault("user_name", user_name or self.state.complaint.get("CUS", ""))
        triage.setdefault("product_id", self.state.complaint.get("PID", self.state.product.get("PID", "")))
        triage.setdefault("product_name", self.state.product.get("PNM", self.state.complaint.get("PNM", "")))
        triage.setdefault("issue_summary", self.state.complaint.get("CDES", ""))
        triage.setdefault("classification", "")
        triage.setdefault("risk_level", "")
        triage.setdefault("reasoning", "")
        triage.setdefault("recommended_action", "")
        triage.setdefault("department", "")
        triage.setdefault("confidence", 0.0)

        if "sample_ticket" not in result or not isinstance(result["sample_ticket"], dict):
            result["sample_ticket"] = {}
        sample = result["sample_ticket"]
        sample.setdefault("TID", "SAMPLE")
        sample.setdefault("CID", self.state.cid)
        sample.setdefault("DEP", triage.get("department", ""))
        sample.setdefault("PRI", "")
        sample.setdefault("STA", "Open")
        sample.setdefault("DES", triage.get("recommended_action", triage.get("issue_summary", "")))
        sample.setdefault("CRT", "")

        if "ticket" not in result or not isinstance(result["ticket"], dict):
            result["ticket"] = {}
        result["ticket"].setdefault("should_create", False)
        result["ticket"].setdefault("reason", "Ticket creation is disabled in this agent preview.")

        return result

    # ------------------------------------------------------------------
    # AI synthesis / repair
    # ------------------------------------------------------------------

    def _synthesize_from_state(self, user_name: Optional[str]) -> Dict[str, Any]:
        prompt = self._final_synthesis_prompt(user_name)
        response = client.models.generate_content(
            model=self.model,
            contents=[types.Content(role="user", parts=[types.Part(text=prompt)])],
            config=FINAL_CONFIG,
        )
        text = _get_response_text(response)
        if not text.strip():
            raise ValueError("Gemini produced empty synthesis output")
        return _safe_json_loads(text)

    def _finalize_result(self, raw_final: str, user_name: Optional[str]) -> Dict[str, Any]:
        prompt = self._final_synthesis_prompt(user_name)
        response = client.models.generate_content(
            model=self.model,
            contents=[types.Content(role="user", parts=[types.Part(text=prompt + "\n\nRaw assistant output:\n" + raw_final)])],
            config=FINAL_CONFIG,
        )
        text = _get_response_text(response)
        if not text.strip():
            raise ValueError("Gemini produced empty final output")
        return _safe_json_loads(text)

    def _repair_result(self, broken_result: Dict[str, Any], user_name: Optional[str]) -> Dict[str, Any]:
        prompt = self._repair_prompt(broken_result, user_name)
        response = client.models.generate_content(
            model=self.model,
            contents=[types.Content(role="user", parts=[types.Part(text=prompt)])],
            config=REPAIR_CONFIG,
        )
        text = _get_response_text(response)
        if not text.strip():
            return broken_result
        try:
            return _safe_json_loads(text)
        except Exception:
            return broken_result

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _needs_repair(self, result: Dict[str, Any]) -> bool:
        if not isinstance(result, dict):
            return True

        triage = result.get("triage_analysis")
        if not isinstance(triage, dict):
            return True

        sample = result.get("sample_ticket")
        if not isinstance(sample, dict):
            return True

        required_triage_keys = [
            "complaint_id",
            "user_name",
            "product_id",
            "product_name",
            "issue_summary",
            "classification",
            "risk_level",
            "reasoning",
            "recommended_action",
            "department",
            "confidence",
        ]
        required_ticket_keys = ["TID", "CID", "DEP", "PRI", "STA", "DES", "CRT"]

        for key in required_triage_keys:
            if key not in triage:
                return True

        for key in required_ticket_keys:
            if key not in sample:
                return True

        return False


# =============================================================================
# DMS / RAG tool execution
# =============================================================================


def execute_tool(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    if name == "get_complaint":
        return tool_get_complaint(args["cid"])
    if name == "get_product":
        return tool_get_product(args["pid"])
    if name == "get_user_latest_complaint":
        return tool_get_user_latest_complaint(args["user_name"])
    if name == "get_user_complaints":
        return tool_get_user_complaints(
            args["user_name"],
            int(args.get("i", -1)),
            int(args.get("j", -1)),
        )
    if name == "check_complaint":
        return tool_check_complaint(args["cid"])
    if name == "get_products":
        return tool_get_products(int(args.get("i", -1)), int(args.get("j", -1)))
    if name == "rag_retrieve":
        return tool_rag_retrieve(args["query"])
    raise ValueError(f"Unknown tool: {name}")


# =============================================================================
# CLI
# =============================================================================


def main(argv: List[str]) -> int:
    if len(argv) < 2:
        print("Usage: python ctas_tool_calling_agent_gemini_ai_only.py <CID> [user_name]", file=sys.stderr)
        return 2

    cid = argv[1]
    user_name = argv[2] if len(argv) > 2 else None

    agent = CTASToolAgent()
    output = agent.analyze(cid=cid, user_name=user_name)
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.responses import Response,JSONResponse

router = APIRouter()

@router.post("/CTAS/analyze")
async def Analysis(request:Request):
    _data = await request.json()
    agent = CTASToolAgent()
    output = agent.analyze(str(_data["CID"]),request.state.UNAM)
    return JSONResponse(output,200)

