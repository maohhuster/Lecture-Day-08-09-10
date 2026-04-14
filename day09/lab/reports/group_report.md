# Báo Cáo Nhóm — Lab Day 09: Multi-Agent Orchestration

**Tên nhóm:** C401  
**Thành viên:**
| Tên | Vai trò | Email |
|-----|---------|-------|
| Lê Hà An | Supervisor Owner |  |
| Nguyễn Anh Hào | Worker Owner |  |
| Lê Đức Hải | Worker Owner + Trace & Docs Owner |  |
| Nguyễn Đức Mạnh | Trace & Docs Owner |  |
| Cường | MCP Owner |  |
**Ngày nộp:** 14/04/2026  
**Repo:** maohhuster/Lecture-Day-08-09-10  
**Độ dài khuyến nghị:** 600–1000 từ

---

> **Hướng dẫn nộp group report:**
> 
> - File này nộp tại: `reports/group_report.md`
> - Deadline: Được phép commit **sau 18:00** (xem SCORING.md)
> - Tập trung vào **quyết định kỹ thuật cấp nhóm** — không trùng lặp với individual reports
> - Phải có **bằng chứng từ code/trace** — không mô tả chung chung
> - Mỗi mục phải có ít nhất 1 ví dụ cụ thể từ code hoặc trace thực tế của nhóm

---

## 1. Kiến trúc nhóm đã xây dựng (150–200 từ)

> Mô tả ngắn gọn hệ thống nhóm: bao nhiêu workers, routing logic hoạt động thế nào,
> MCP tools nào được tích hợp. Dùng kết quả từ `docs/system_architecture.md`.

**Hệ thống tổng quan:**

Nhóm xây dựng hệ thống **Supervisor-Worker** gồm 1 Supervisor và 3 Workers chuyên biệt: `retrieval_worker`, `policy_tool_worker`, và `synthesis_worker`. Supervisor phân tích query đầu vào, phân loại theo từ khóa rủi ro/nghiệp vụ rồi route đến worker phù hợp. Kết quả từ mỗi worker được ghi vào `AgentState` dùng chung và luôn kết thúc ở `synthesis_worker` để tổng hợp câu trả lời grounded. Toàn bộ pipeline được triển khai trong `graph.py` với `AgentState` (TypedDict) làm Shared State xuyên suốt. Trong 30 traces đã chạy, hệ thống phân phối: 16/30 (53%) route `retrieval_worker`, 14/30 (47%) route `policy_tool_worker`. Human Review (HITL) là node dự phòng khi gặp lỗi phức tạp kết hợp rủi ro cao.

```
User Request
     │
     ▼
┌──────────────┐
│  Supervisor  │  ← keyword matching: risk_keywords, policy_keywords, hitl_keywords
└──────┬───────┘
       │ route_decision()
   ┌───┴──────────────────────┐
   │                          │
   ▼                          ▼
retrieval_worker     policy_tool_worker
   (FAQ/SLA)          (refund/access)
   │                          │
   └──────────┬───────────────┘
              │
              ▼
       synthesis_worker
         (answer + cite)
              │
              ▼
           Output
```

**Routing logic cốt lõi:**
> Supervisor dùng **keyword matching** (rule-based) để định tuyến. Ba tập từ khóa được định nghĩa trong `graph.py`:

- `policy_keywords = ["hoàn tiền", "refund", "flash sale", "license", "cấp quyền", "access", "level 3", "admin"]` → route `policy_tool_worker`
- `risk_keywords = ["emergency", "khẩn cấp", "2am", "p1", "sla", "sự cố"]` → đặt `risk_high=True`, giữ route `retrieval_worker`
- `hitl_keywords = ["err-", "không rõ", "lỗi hệ thống", "phàn nàn"]` + `risk_high=True` → route `human_review`

**MCP tools đã tích hợp:**
> Nhóm (Cường – MCP Owner) implement đầy đủ 4 tools trong `mcp_server.py`, expose qua `dispatch_tool()`:

- `search_kb`: Semantic search ChromaDB → trả `chunks`, `sources`, `total_found`; delegate sang `workers/retrieval.py` khi ChromaDB ready
- `get_ticket_info`: Tra cứu ticket mock (VD: `P1-LATEST` → IT-9847, status `in_progress`, SLA deadline 02:47)
- `check_access_permission`: Kiểm tra quyền Level 1/2/3 + emergency bypass; Level 2 có thể cấp tạm thời khi P1 emergency
- `create_ticket`: Tạo ticket mock Jira (không tạo thật trong lab)

---

## 2. Quyết định kỹ thuật quan trọng nhất (200–250 từ)

> Chọn **1 quyết định thiết kế** mà nhóm thảo luận và đánh đổi nhiều nhất.
> Phải có: (a) vấn đề gặp phải, (b) các phương án cân nhắc, (c) lý do chọn phương án đã chọn.

**Quyết định:** Dùng Keyword Matching (rule-based) hay LLM Classifier cho routing logic của Supervisor?

**Bối cảnh vấn đề:**

Supervisor cần phân tích query để quyết định route `retrieval_worker` hay `policy_tool_worker`. Ban đầu nhóm cân nhắc dùng LLM để phân loại ý định (intent classification), nhưng trong môi trường lab với budget LLM call hạn chế và cần trace rõ ràng, nhóm phải đưa ra quyết định đánh đổi giữa accuracy vs. explainability + cost.

**Các phương án đã cân nhắc:**

| Phương án | Ưu điểm | Nhược điểm |
|-----------|---------|-----------|
| Keyword Matching (rule-based) | Nhanh, không tốn LLM call, `route_reason` rõ ràng trong trace | Brittle — miss variant từ khóa, không xử lý được ambiguous query |
| LLM Classifier (gọi Gemini để phân loại) | Hiểu ngữ nghĩa tốt hơn, xử lý câu phức tạp | Tốn thêm 1 LLM call/query, latency tăng, khó test deterministic |
| Hybrid (keyword first, LLM fallback) | Kết hợp tốc độ + accuracy | Phức tạp hơn, debug khó hơn |

**Phương án đã chọn và lý do:**

Nhóm chọn **Keyword Matching** vì: (1) Lab yêu cầu `route_reason` phải ghi được vào trace để debug — keyword matching cho phép viết `route_reason` deterministically; (2) Với 30 test queries đã định sẵn, tập keyword đủ để cover; (3) Tiết kiệm LLM call — synthesis worker đã dùng ít nhất 1 call, không muốn supervisor tốn thêm; (4) Dễ test từng nhánh độc lập.

**Bằng chứng từ trace/code:**

```json
// Trace q02 — policy_tool_worker được route đúng
{
  "task": "Khách hàng có thể yêu cầu hoàn tiền trong bao nhiêu ngày?",
  "supervisor_route": "policy_tool_worker",
  "route_reason": "Chọn MCP (Policy Tool Worker) vì yêu cầu cần check external tools (chính sách/quyền).",
  "needs_tool": true,
  "workers_called": ["policy_tool_worker", "retrieval_worker", "synthesis_worker"]
}

// graph.py — keyword matching logic
policy_keywords = ["hoàn tiền", "refund", "flash sale", "license", "cấp quyền", "access", "level 3", "admin"]
if any(kw in task for kw in policy_keywords):
    route = "policy_tool_worker"
    route_reason = "Chọn MCP (Policy Tool Worker) vì yêu cầu cần check external tools..."
    needs_tool = True
```

---

## 3. Kết quả grading questions (150–200 từ)

> Sau khi chạy pipeline với grading_questions.json (public lúc 17:00):
> - Nhóm đạt bao nhiêu điểm raw?
> - Câu nào pipeline xử lý tốt nhất?
> - Câu nào pipeline fail hoặc gặp khó khăn?

**Tổng điểm raw ước tính:** ~32 / 96  
_(Routing đúng cho phần lớn câu nhưng synthesis bị fallback do ChromaDB chưa có dữ liệu đủ — confidence 0.1 toàn bộ)_

**Câu pipeline xử lý tốt nhất:**
- ID: **gq06** — "Nhân viên mới trong probation period muốn làm remote" → `final_answer` trả đúng: _"Nhân viên trong probation period KHÔNG được phép làm remote. Điều kiện: qua probation, Team Lead phê duyệt, tối đa 2 ngày/tuần, on-site Thứ 3 và Thứ 5"_; `supervisor_route=retrieval_worker`, routing đúng vì không có policy/risk keyword.
- ID: **gq08** — "Nhân viên phải đổi mật khẩu sau bao nhiêu ngày?" → synthesis trả đúng: _"90 ngày, hệ thống nhắc 7 ngày trước"_, confidence = 0.1 do fallback nhưng content đúng.

**Câu pipeline fail hoặc partial:**
- ID: **gq07** — "Mức phạt tài chính khi vi phạm SLA P1" → answer chỉ trả _"Dựa trên tài liệu nội bộ [2]"_, không có nội dung cụ thể.  
  Root cause: `synthesis_worker` gọi `workers/synthesis.py` nhưng ChromaDB chưa index đủ document thực tế; fallback dùng `retrieved_chunks` mock chỉ có _"SLA P1 yêu cầu xử lý trong 4 giờ"_ — không đủ context để trả lời câu hỏi về mức phạt.
- ID: **gq01, gq03, gq04, gq05, gq09, gq10** — tương tự, synthesis bị fallback → answer generic.

**Câu gq07 (abstain):** Pipeline không có cơ chế abstain tường minh — synthesis trả lời chung chung thay vì explict "Không đủ thông tin". Nhóm nhận ra đây là điểm yếu: cần thêm logic kiểm tra `len(chunks) == 0 or confidence < threshold → abstain`.

**Câu gq09 (multi-hop khó nhất):** _"Sự cố P1 lúc 2am + cần cấp Level 2 access cho contractor"_ — Trace ghi nhận `workers_called = ["policy_tool_worker", "retrieval_worker", "synthesis_worker"]`, tức 2 workers (policy + retrieval) đã được gọi. Tuy nhiên do synthesis fallback, câu trả lời không tổng hợp được đủ 2 luồng thông tin cùng lúc. Routing detection đúng (policy_keywords + risk_keywords nhận diện cả hai phần của query).

---

## 4. So sánh Day 08 vs Day 09 — Điều nhóm quan sát được (150–200 từ)

> Dựa vào `docs/single_vs_multi_comparison.md` — trích kết quả thực tế.

**Metric thay đổi rõ nhất (có số liệu):**

| Metric | Day 08 (Single Agent) | Day 09 (Multi-Agent) | Delta |
|--------|----------------------|---------------------|-------|
| Routing visibility | ✗ Không có | ✓ `route_reason` mỗi trace | N/A |
| Routing distribution | N/A | 53% retrieval / 47% policy | N/A |
| Total traces | 10 queries | 30 traces (15 questions × 2 runs) | +20 |
| Avg confidence | 0.76 | 0.10 (synthesis fallback) | -0.66 |
| Avg latency (ms) | 2500 ms | ~1 ms (mock, không có real LLM call) | -2499 |
| Debuggability | Đọc toàn code | Đọc `route_reason` → test worker độc lập | ↑↑ |

**Điều nhóm bất ngờ nhất khi chuyển từ single sang multi-agent:**

Bất ngờ lớn nhất là **overhead tổ chức state**. Với single agent (Day 08), chỉ cần pass `query` → `answer`. Với multi-agent, phải thiết kế `AgentState` với 13 fields (`task`, `route_reason`, `risk_high`, `needs_tool`, `hitl_triggered`, `retrieved_chunks`, `retrieved_sources`, `policy_result`, `mcp_tools_used`, `final_answer`, `sources`, `confidence`, `workers_called`...). Lúc đầu nhóm không đủ fields nên synthesis_worker không đọc được kết quả của retrieval_worker → phải refactor state schema.

**Trường hợp multi-agent KHÔNG giúp ích hoặc làm chậm hệ thống:**

Với câu hỏi FAQ đơn giản như gq08 ("đổi mật khẩu sau bao nhiêu ngày?"), multi-agent tốn 3 node calls (supervisor → retrieval → synthesis) trong khi single agent chỉ cần 1 RAG call. Routing overhead không tạo ra giá trị thêm cho câu hỏi không có policy/multi-hop.

---

## 5. Phân công và đánh giá nhóm (100–150 từ)

> Đánh giá trung thực về quá trình làm việc nhóm.

**Phân công thực tế:**

| Thành viên | Phần đã làm | Sprint |
|------------|-------------|--------|
| Lê Hà An | Supervisor node (`graph.py` — routing logic, HITL condition, AgentState schema), docs `system_architecture.md` | Sprint 1 + 3 |
| Nguyễn Anh Hào | Retrieval Worker (`workers/retrieval.py`), ChromaDB integration, `docs/routing_decisions.md` | Sprint 1 + 2 |
| Lê Đức Hải | Policy Tool Worker (`workers/policy_tool.py`), Synthesis Worker (`workers/synthesis.py`), `docs/single_vs_multi_comparison.md` | Sprint 2 |
| Nguyễn Đức Mạnh | `eval_trace.py`, trace artifacts, group report + docs | Trace |
| Cường | MCP Server (`mcp_server.py` — 4 tools) | Sprint 3 |

**Điều nhóm làm tốt:**

Phân chia ownership rõ ràng theo Sprint giúp tránh conflict. Trace artifacts được lưu đầy đủ (`artifacts/traces/` — 30 files) nhờ `save_trace()` trong `graph.py`, tạo bằng chứng cụ thể cho report. MCP Server được thiết kế modular với `dispatch_tool()` interface chuẩn, dễ extend thêm tool mà không sửa worker.

**Điều nhóm làm chưa tốt hoặc gặp vấn đề về phối hợp:**

- ChromaDB integration chưa hoàn chỉnh → synthesis fallback → confidence thấp (0.1) toàn bộ, ảnh hưởng điểm grading.
- Thiếu abstain logic tường minh: khi `retrieved_chunks` empty, synthesis nên trả "Không đủ thông tin" thay vì hallucinate.
- Nhóm review synthesis_worker quá muộn (Sprint 2 cuối), không kịp fix trước grading run.

**Nếu làm lại, nhóm sẽ thay đổi gì trong cách tổ chức?**

Định nghĩa `AgentState` schema và contract giữa các workers trước (interface-first), sau đó mỗi người implement worker độc lập. Như vậy tránh được việc synthesis_worker không đọc được output của retrieval_worker do field name khác nhau.

---

## 6. Nếu có thêm 1 ngày, nhóm sẽ làm gì? (50–100 từ)

> 1–2 cải tiến cụ thể với lý do có bằng chứng từ trace/scorecard.

**Cải tiến 1: Fix ChromaDB integration + abstain logic**  
Từ trace: 8/10 grading questions trả `"Dựa trên tài liệu nội bộ [2]"` do synthesis fallback. Nếu index đúng document vào ChromaDB và thêm `if not chunks: return {"answer": "Không đủ thông tin", "confidence": 0.0}` trong synthesis, dự kiến confidence tăng từ 0.10 → ≥0.70 và gq07 abstain đúng thay vì trả lời sai.

**Cải tiến 2: Upgrade Supervisor sang LLM Classifier cho câu ambiguous**  
gq09 (multi-hop) route đúng workflow nhưng synthesis không tổng hợp được 2 luồng. Dùng LLM phân loại intent phức tạp hơn + cho phép supervisor gọi nhiều workers song song (fan-out) thay vì sequential, sẽ xử lý được multi-hop tốt hơn.

---

*File này lưu tại: `reports/group_report.md`*  
*Commit sau 18:00 được phép theo SCORING.md*
