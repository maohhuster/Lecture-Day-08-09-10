# Tuning Log — Grading Questions (Day 08 Lab)

> Template: Ghi lại mỗi thay đổi và kết quả quan sát được.  
> A/B Rule: Chỉ đổi **MỘT biến** mỗi lần.

---

## Baseline — Grading Run 1 (Sprint 4)

**Ngày:** 2026-04-13  
**Input:** `data/grading_questions.json` (10 câu)  
**Output log:** `logs/grading_run.json`  
**Scorecard (auto):** `results/scorecard_grading_questions.md`

### Config

```
retrieval_mode = "hybrid"
top_k_search = 10
top_k_select = 3
use_rerank = True

# Embedding
EMBEDDING_PROVIDER = "hash"
```

### Lý do (notes)

- **Hybrid + rerank**: dùng config “tốt nhất hiện có” để maximize khả năng kéo đúng evidence (đặc biệt các câu cross-document như gq02, gq06).
- **`EMBEDDING_PROVIDER=hash`**: môi trường hiện tại gặp lỗi permission/proxy khi tải model SentenceTransformers từ HuggingFace; dùng hash embedding để pipeline **chạy end-to-end ổn định** (dense vẫn chạy được, BM25 vẫn hỗ trợ keyword), tránh crash khi chạy grading.

---

## Scorecard Baseline (Auto from expected_sources)

**Kết quả tổng:**
| Metric | Value |
|--------|-------|
| Context Recall (avg, theo expected_sources) | **0.83** |
| Answered (không phải “Tôi không biết”) | **6/10** |
| Abstain (“Tôi không biết”) | **4/10** |

**Các câu đáng chú ý:**
- **Abstain dù có expected_sources**: gq04, gq08, gq09  
- **Thiếu expected_sources trong retrieval (theo `sources` log)**: gq02, gq08

---

## Per-question Notes (Quick Triage)

### Nhóm trả lời tốt (đúng hướng, có evidence)

- **gq01 (SLA version reasoning)**: trả lời được “6h → 4h” và có cite từ `support/sla-p1-2026.pdf`.  
- **gq03 (Refund exception chain)**: kết luận “không hoàn tiền” đúng hướng; cite `policy/refund-v4.pdf`.  
- **gq06 (Emergency temp access + cross-doc)**: trả lời đúng quy trình temp access + giới hạn 24h + log Security Audit; cite `it/access-control-sop.md` và `support/sla-p1-2026.pdf`.  
- **gq10 (Temporal scoping)**: kết luận “không áp dụng trước 01/02/2026; đơn cũ theo v3” đúng hướng; cite `policy/refund-v4.pdf`.

### Nhóm có rủi ro “thiếu điều kiện / thiếu nguồn / answer lệch”

- **gq02 (Cross-doc: VPN bắt buộc + 2 thiết bị)**:
  - Output hiện tại chỉ trả lời phần “2 thiết bị”.
  - `expected_sources` cần **2 nguồn** (HR + Helpdesk). Scorecard cho thấy thiếu `hr/leave-policy-2026.pdf` trong retrieval → **Context Recall 0.50**.

- **gq05 (Admin Access cho contractor)**:
  - Answer hiện tại bị “trượt” sang **emergency temporary access 24h** (nội dung hợp với gq06) thay vì trả đúng **Level 4 Admin Access**: approvers (IT Manager + CISO), **5 ngày làm việc**, **training bắt buộc**.
  - Đây là dấu hiệu **rerank/select bị hút vào chunk emergency** (highly relevant lexical cues: “tạm thời”, “khẩn cấp”) → sai scope.

### Nhóm bị abstain (cần sửa retrieval/prompt)

- **gq04 (Store credit 110%)**:
  - Retriever có `policy/refund-v4.pdf` nhưng model vẫn “Tôi không biết” → khả năng **chunk select không chứa câu có “110%”** hoặc prompt chưa ép “đọc số”.

- **gq08 (Disambiguation: 3 ngày phép vs 3 ngày ốm)**:
  - `expected_sources`: `hr/leave-policy-2026.pdf`, nhưng retrieval không có → Context Recall 0.00, nên abstain là dễ hiểu.

- **gq09 (Password policy 90 ngày + nhắc 7 ngày + reset URL/ext)**:
  - `expected_sources`: `support/helpdesk-faq.md`. Log có retrieve `support/helpdesk-faq.md` nhưng vẫn abstain → tương tự gq04: **chunk select không đúng section** hoặc prompt/generation issue.

- **gq07 (Insufficient context / abstain bait)**:
  - Abstain là **đúng hành vi mong muốn** (không bịa penalty).

---

## Kết luận Baseline

- Pipeline **chạy grading end-to-end** và tạo được artifact đúng format nộp bài (`logs/grading_run.json`, scorecard).
- Các lỗi chính hiện thấy rơi vào 3 nhóm:
  - **Cross-document recall** chưa ổn (gq02, gq08).
  - **Select/rerank sai scope** (gq05).
  - **Numeric/detail extraction** còn yếu dù có đúng source (gq04, gq09).

---

## Variant kế tiếp (đề xuất — chỉ đổi 1 biến)

### Variant A — Tăng `top_k_select` (3 → 5)

**Giả thuyết:** gq04/gq09 cần đúng 1 câu chứa số (110%, 90 ngày, 7 ngày). Nếu top_k_select=3 bỏ lỡ câu này thì model sẽ abstain.  
**Biến đổi duy nhất:**
```
top_k_select = 5
```
**Kỳ vọng:** giảm abstain ở gq04/gq09 mà không tăng hallucination.

### Variant B — Prompt tweak cho “numeric facts”

**Giả thuyết:** model “Tôi không biết” dù có context vì chưa bị ép “scan for numbers”.  
**Biến đổi duy nhất:** sửa `build_grounded_prompt()` để thêm 1 rule: “Nếu trong context có con số/%, phải trích đúng con số; nếu không có thì mới abstain.”  
**Kỳ vọng:** gq04/gq09 cải thiện, không làm hại gq07.

### Variant C — Query expansion nhẹ cho cross-doc

**Giả thuyết:** gq02 cần kéo HR policy chunk, query hiện tại có thể match yếu.  
**Biến đổi duy nhất:** `transform_query()` (expansion) tạo 2-3 biến thể query có keyword “remote”, “VPN bắt buộc”, “HR Portal/leave policy” và hợp nhất retrieval.  
**Kỳ vọng:** tăng Context Recall cho gq02/gq08.
