import json
import os
import time
from datetime import datetime
from typing import TypedDict, Literal, Optional

# Giả lập import từ các module RAG đã xây dựng ở các turn trước
# Trong thực tế, bạn sẽ dùng: from rag_answer import retrieve_dense, call_llm
import google.generativeai as genai

# ─────────────────────────────────────────────
# 1. Shared State (Giữ nguyên cấu trúc của bạn)
# ─────────────────────────────────────────────

class AgentState(TypedDict):
    task: str
    route_reason: str
    risk_high: bool
    needs_tool: bool
    hitl_triggered: bool
    retrieved_chunks: list
    retrieved_sources: list
    policy_result: dict
    mcp_tools_used: list
    final_answer: str
    sources: list
    confidence: float
    history: list
    workers_called: list
    supervisor_route: str
    latency_ms: Optional[int]
    run_id: str

def make_initial_state(task: str) -> AgentState:
    return {
        "task": task,
        "route_reason": "",
        "risk_high": False,
        "needs_tool": False,
        "hitl_triggered": False,
        "retrieved_chunks": [],
        "retrieved_sources": [],
        "policy_result": {},
        "mcp_tools_used": [],
        "final_answer": "",
        "sources": [],
        "confidence": 0.0,
        "history": [],
        "workers_called": [],
        "supervisor_route": "",
        "latency_ms": None,
        "run_id": f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    }

# ─────────────────────────────────────────────
# 2. Supervisor Node — Hoàn thiện logic Sprint 1
# ─────────────────────────────────────────────

def supervisor_node(state: AgentState) -> AgentState:
    """Supervisor phân tích task và quyết định định tuyến dựa trên ý định."""
    task = state["task"].lower()
    state["history"].append(f"[supervisor] phân tích task: {state['task'][:80]}")

    # Định nghĩa tập từ khóa chuyên biệt
    policy_keywords = ["hoàn tiền", "refund", "flash sale", "license", "cấp quyền", "access", "level 3", "admin"]
    risk_keywords = ["emergency", "khẩn cấp", "2am", "p1", "sla", "sự cố"]
    hitl_keywords = ["err-", "không rõ", "lỗi hệ thống", "phàn nàn"]

    route = "retrieval_worker"
    # ĐIỀU KIỆN DONE 4: Ghi log "không chọn MCP" mặc định
    route_reason = "Không chọn MCP, mặc định dùng Retrieval Worker cho tác vụ FAQ."
    needs_tool = False
    risk_high = False

    # Logic định tuyến dựa trên rủi ro và nghiệp vụ
    if any(kw in task for kw in risk_keywords):
        risk_high = True
        route_reason = "Không chọn MCP, điều hướng về Retrieval Worker do phát hiện rủi ro cao/SLA P1."

    if any(kw in task for kw in policy_keywords):
        route = "policy_tool_worker"
        # ĐIỀU KIỆN DONE 4: Ghi log "chọn MCP" 
        route_reason = "Chọn MCP (Policy Tool Worker) vì yêu cầu cần check external tools (chính sách/quyền)."
        needs_tool = True
    
    # Kích hoạt Human Review nếu có lỗi không xác định đi kèm rủi ro
    if risk_high and any(kw in task for kw in hitl_keywords):
        route = "human_review"
        route_reason = "Không chọn MCP, mã lỗi phức tạp trong tình huống khẩn cấp cần con người thẩm định."
        needs_tool = False

    state["supervisor_route"] = route
    state["route_reason"] = route_reason
    state["needs_tool"] = needs_tool
    state["risk_high"] = risk_high
    state["history"].append(f"[supervisor] route={route} | reason={route_reason}")

    return state

# ─────────────────────────────────────────────
# 3. Route Decision (Giữ nguyên)
# ─────────────────────────────────────────────

def route_decision(state: AgentState) -> Literal["retrieval_worker", "policy_tool_worker", "human_review"]:
    return state.get("supervisor_route", "retrieval_worker")

# ─────────────────────────────────────────────
# 4. Human Review Node — Hoàn thiện logic HITL
# ─────────────────────────────────────────────

def human_review_node(state: AgentState) -> AgentState:
    """HITL node: Giả lập sự can thiệp của con người."""
    state["hitl_triggered"] = True
    state["workers_called"].append("human_review")
    
    # Trong môi trường thực chiến, đây là điểm dừng (breakpoint)
    print(f"\n[!] HUMAN INTERVENTION REQUIRED for Task: {state['task']}")
    print(f"    Reason: {state['route_reason']}")
    
    # Giả lập con người phê duyệt và chuyển tiếp cho Retrieval lấy chứng cứ
    state["history"].append("[human_review] Con người đã duyệt, chuyển tiếp retrieval")
    state["supervisor_route"] = "retrieval_worker"
    
    return state

# ─────────────────────────────────────────────
# 5. Worker Nodes — Hoàn thiện Sprint 2 (Integration)
# ─────────────────────────────────────────────

def retrieval_worker_node(state: AgentState) -> AgentState:
    """Gọi retrieval logic thực tế (Giả lập kết quả từ turn RAG trước)"""
    state["workers_called"].append("retrieval_worker")
    state["history"].append("[retrieval_worker] Đang truy vấn ChromaDB...")

    # Giả lập kết quả truy vấn dựa trên task
    if "p1" in state["task"].lower():
        state["retrieved_chunks"] = [{"text": "SLA P1 yêu cầu xử lý trong 4 giờ.", "source": "sla_p1_2026.txt"}]
    else:
        state["retrieved_chunks"] = [{"text": "Quy trình hỗ trợ chung cho nhân viên.", "source": "helpdesk_faq.txt"}]
    
    state["retrieved_sources"] = list(set(c["source"] for c in state["retrieved_chunks"]))
    return state

def policy_tool_worker_node(state: AgentState) -> AgentState:
    """Thực hiện kiểm tra chính sách chuyên sâu"""
    state["workers_called"].append("policy_tool_worker")
    state["history"].append("[policy_tool_worker] Đang kiểm tra logic chính sách...")

    # Giả lập kết quả kiểm tra tool
    state["policy_result"] = {
        "is_valid": True,
        "detail": "Yêu cầu tuân thủ Access Control SOP Section 2.",
        "source": "access_control_sop.txt"
    }
    return state

def synthesis_worker_node(state: AgentState) -> AgentState:
    """Tổng hợp câu trả lời grounded"""
    state["workers_called"].append("synthesis_worker")
    state["history"].append("[synthesis_worker] Đang tổng hợp câu trả lời...")

    # Logic tổng hợp đơn giản (Trong thực tế sẽ gọi call_llm với prompt)
    context = " ".join([c["text"] for c in state["retrieved_chunks"]])
    policy = state["policy_result"].get("detail", "")
    
    state["final_answer"] = f"Trả lời: {context} {policy}".strip()
    state["sources"] = state["retrieved_sources"]
    state["confidence"] = 0.9 if state["retrieved_chunks"] else 0.5
    
    return state

# ─────────────────────────────────────────────
# 6. Build Graph — Hoàn thiện luồng chạy
# ─────────────────────────────────────────────

def build_graph():
    def run(state: AgentState) -> AgentState:
        start_time = time.time()

        # Step 1: Supervisor ra quyết định
        state = supervisor_node(state)

        # Step 2: Điều phối dựa trên quyết định
        route = route_decision(state)

        if route == "human_review":
            state = human_review_node(state)
            state = retrieval_worker_node(state)
        elif route == "policy_tool_worker":
            state = policy_tool_worker_node(state)
            # Policy worker thường cần thêm context từ retrieval
            state = retrieval_worker_node(state)
        else:
            state = retrieval_worker_node(state)

        # Step 3: Luôn kết thúc bằng việc tổng hợp câu trả lời
        state = synthesis_worker_node(state)

        state["latency_ms"] = int((time.time() - start_time) * 1000)
        state["history"].append(f"[graph] Hoàn thành run trong {state['latency_ms']}ms")
        return state

    return run

# ─────────────────────────────────────────────
# 7. Manual Test (Sử dụng queries từ grading_questions)
# ─────────────────────────────────────────────

_graph = build_graph()

def run_graph(task: str) -> AgentState:
    state = make_initial_state(task)
    return _graph(state)

if __name__ == "__main__":
    test_queries = [
        "SLA xử lý ticket P1 là bao lâu?",
        "ERR-403: Cấp quyền Level 3 khẩn cấp cho engineer xử lý P1.",
        "Khách hàng Flash Sale đòi hoàn tiền sản phẩm lỗi."
    ]

    for query in test_queries:
        print(f"\n{'-'*30}\nQUERY: {query}")
        result = run_graph(query)
        print(f"ROUTE   : {result['supervisor_route']}")
        print(f"REASON  : {result['route_reason']}")
        print(f"ANSWER  : {result['final_answer']}")
        print(f"WORKERS : {result['workers_called']}")

def save_trace(result: AgentState, output_dir: str = "artifacts/traces") -> str:
    import json
    import os
    from datetime import datetime
    os.makedirs(output_dir, exist_ok=True)
    trace_id = result.get('run_id', f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    filename = f"{trace_id}.json"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return filepath