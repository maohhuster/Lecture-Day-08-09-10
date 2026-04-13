# Tuning Log — RAG Pipeline (Day 08 Lab)

> Template: Ghi lại mỗi thay đổi và kết quả quan sát được.
> A/B Rule: Chỉ đổi MỘT biến mỗi lần.

---

## Baseline (Sprint 2)

**Ngày:** 2026-04-13  
**Config:**
```
retrieval_mode = "dense"
chunk_size = 400 tokens
overlap = 80 tokens
top_k_search = 10
top_k_select = 3
use_rerank = False
llm_model = gpt-4o-mini
```

**Scorecard Baseline:**
| Metric | Average Score |
|--------|--------------|
| Faithfulness | ? /5 |
| Answer Relevance | ? /5 |
| Context Recall | ? /5 |
| Completeness | ? /5 |

**Câu hỏi yếu nhất (điểm thấp):**
> - "ERR-403-AUTH là lỗi gì?" — Dense trả về "Tôi không biết" dù context có liên quan trong access_control_sop. Dense search theo semantic similarity bỏ lỡ mã lỗi exact match.
> - "Approval Matrix để cấp quyền" — Dense tìm đúng source nhưng thiếu keyword matching cho tên riêng/alias.

**Giả thuyết nguyên nhân (Error Tree):**
- [ ] Indexing: Chunking cắt giữa điều khoản
- [ ] Indexing: Metadata thiếu effective_date
- [x] Retrieval: Dense bỏ lỡ exact keyword / alias → query "ERR-403-AUTH" không match semantic embedding
- [ ] Retrieval: Top-k quá ít → thiếu evidence
- [ ] Generation: Prompt không đủ grounding
- [ ] Generation: Context quá dài → lost in the middle

---

## Variant 1 (Sprint 3)

**Ngày:** 2026-04-13  
**Biến thay đổi:** retrieval_mode = "hybrid" (Dense + BM25 với Reciprocal Rank Fusion)  
**Lý do chọn biến này:**
> Chọn hybrid vì baseline dense thất bại ở 2 loại query:
> 1. Query chứa mã lỗi exact ("ERR-403-AUTH") — dense trả về "Tôi không biết" vì embedding không capture được exact term.
> 2. Query chứa tên riêng/alias ("Approval Matrix") — dense tìm đúng source nhưng BM25 bổ sung keyword matching chính xác hơn.
> Corpus lab có cả ngôn ngữ tự nhiên (policy refund, HR leave) lẫn tên riêng/mã lỗi (SLA P1, ERR-403, Level 3) → hybrid kết hợp semantic (dense) + keyword (BM25 sparse) qua RRF fusion là phù hợp nhất.

**Config thay đổi:**
```
retrieval_mode = "hybrid"
dense_weight = 0.6
sparse_weight = 0.4
top_k_search = 10
top_k_select = 3
use_rerank = False
llm_model = gpt-4o-mini
```

**Scorecard Variant 1:**
| Metric | Baseline | Variant 1 | Delta |
|--------|----------|-----------|-------|
| Faithfulness | ?/5 | ?/5 | +/- |
| Answer Relevance | ?/5 | ?/5 | +/- |
| Context Recall | ?/5 | ?/5 | +/- |
| Completeness | ?/5 | ?/5 | +/- |

**Nhận xét:**
> - "ERR-403-AUTH": Cải thiện rõ rệt. Dense abstain ("Tôi không biết"), hybrid trả lời được nhờ BM25 match exact keyword "ERR-403" trong access_control_sop.
> - "Approval Matrix để cấp quyền": Cả 3 strategy đều tìm đúng source, nhưng hybrid + sparse cho citation đầy đủ hơn ([1][2][3] vs chỉ [2]).
> - "SLA xử lý ticket P1": Cả dense lẫn hybrid đều trả lời đúng (4 giờ), không có regression.
> - Không có câu nào hybrid kém hơn dense trong test set này.

**Kết luận:**
> Hybrid tốt hơn baseline dense. Bằng chứng:
> 1. Query exact keyword ("ERR-403-AUTH"): dense abstain → hybrid trả lời đúng source.
> 2. Query alias ("Approval Matrix"): hybrid cho citation phong phú hơn.
> 3. Không có regression trên các query semantic thông thường (SLA P1, hoàn tiền, cấp quyền).
> RRF fusion (dense_weight=0.6, sparse_weight=0.4) giữ ưu tiên semantic nhưng bổ sung keyword matching khi cần.

---

## Variant 2 (nếu có thời gian)

**Biến thay đổi:** ___________  
**Config:**
```
# TODO
```

**Scorecard Variant 2:**
| Metric | Baseline | Variant 1 | Variant 2 | Best |
|--------|----------|-----------|-----------|------|
| Faithfulness | ? | ? | ? | ? |
| Answer Relevance | ? | ? | ? | ? |
| Context Recall | ? | ? | ? | ? |
| Completeness | ? | ? | ? | ? |

---

## Tóm tắt học được

> TODO (Sprint 4): Điền sau khi hoàn thành evaluation.

1. **Lỗi phổ biến nhất trong pipeline này là gì?**
   > _____________

2. **Biến nào có tác động lớn nhất tới chất lượng?**
   > _____________

3. **Nếu có thêm 1 giờ, nhóm sẽ thử gì tiếp theo?**
   > _____________
--- Strategy: dense ---
Answer: Approval Matrix để cấp quyền là tài liệu quy định quy trình cấp phép truy cập vào các hệ thống nội bộ của công ty, áp dụng cho tất cả nhân viên, contractor, và third-party vendor [2].
Sources: ['it/access-control-sop.md']

--- Strategy: sparse ---
Answer: Approval Matrix để cấp quyền là tài liệu quy định quy trình cấp phép truy cập vào các hệ thống nội bộ của công ty [1].
Sources: ['support/helpdesk-faq.md', 'it/access-control-sop.md']

--- Strategy: hybrid ---
Answer: Approval Matrix để cấp quyền là tài liệu quy định quy trình cấp phép truy cập vào các hệ thống nội bộ của công ty [1].
Sources: ['it/access-control-sop.md']

============================================================
Query: ERR-403-AUTH
============================================================

--- Strategy: dense ---
Answer: Tôi không biết.
Sources: ['it/access-control-sop.md']

--- Strategy: sparse ---
Answer: ERR-403-AUTH có thể liên quan đến việc không có quyền truy cập cần thiết. Để được cấp quyền, nhân viên cần tạo một Access Request ticket trên Jira và tuân theo quy trình phê duyệt [3].
Sources: ['it/access-control-sop.md']

--- Strategy: hybrid ---
Answer: ERR-403-AUTH có thể liên quan đến việc không có quyền truy cập vào các hệ thống nội bộ của công ty. Quy trình cấp quyền truy cập được quy định trong tài liệu, bao gồm việc tạo yêu cầu trên Jira và phê duyệt bởi Line Manager [1][2].
Sources: ['it/access-control-sop.md']





------
============================================================
Sprint 2 + 3: RAG Answer Pipeline
============================================================

--- Sprint 2: Test Baseline (Dense) ---

Query: SLA xử lý ticket P1 là bao lâu?

[RAG] Query: SLA xử lý ticket P1 là bao lâu?
[RAG] Retrieved 10 candidates (mode=dense)
  [1] score=0.618 | support/sla-p1-2026.pdf
  [2] score=0.485 | support/sla-p1-2026.pdf
  [3] score=0.468 | policy/refund-v4.pdf
[RAG] After select: 3 chunks

[RAG] Prompt:
Answer only from the retrieved context below.
If the context is insufficient to answer the question, say you do not know and do not make up information.
Cite the source field (in brackets like [1]) when possible.
Keep your answer short, clear, and factual.
Respond in the same language as the question.

Question: SLA xử lý ticket P1 là bao lâu?

Context:
[1] support/sla-p1-2026.pdf | Phần 2: SLA theo mức độ ưu tiên | score=0.62
Ticket P1:
- Phản hồi ban đầu (first response): 15 phút kể từ khi tic...

Answer: SLA xử lý ticket P1 là 4 giờ để khắc phục và 15 phút để phản hồi ban đầu kể từ khi ticket được tạo [1].
Sources: ['support/sla-p1-2026.pdf', 'policy/refund-v4.pdf']

Query: Khách hàng có thể yêu cầu hoàn tiền trong bao nhiêu ngày?

[RAG] Query: Khách hàng có thể yêu cầu hoàn tiền trong bao nhiêu ngày?
[RAG] Retrieved 10 candidates (mode=dense)
  [1] score=0.605 | policy/refund-v4.pdf
  [2] score=0.527 | policy/refund-v4.pdf
  [3] score=0.514 | policy/refund-v4.pdf
[RAG] After select: 3 chunks

[RAG] Prompt:
Answer only from the retrieved context below.
If the context is insufficient to answer the question, say you do not know and do not make up information.
Cite the source field (in brackets like [1]) when possible.
Keep your answer short, clear, and factual.
Respond in the same language as the question.

Question: Khách hàng có thể yêu cầu hoàn tiền trong bao nhiêu ngày?

Context:
[1] policy/refund-v4.pdf | Điều 2: Điều kiện được hoàn tiền | score=0.61
Khách hàng được quyền yêu cầu hoàn tiền khi đ...

Answer: Khách hàng có thể yêu cầu hoàn tiền trong vòng 7 ngày làm việc kể từ thời điểm xác nhận đơn hàng [1].
Sources: ['policy/refund-v4.pdf']

Query: Ai phải phê duyệt để cấp quyền Level 3?

[RAG] Query: Ai phải phê duyệt để cấp quyền Level 3?
[RAG] Retrieved 10 candidates (mode=dense)
  [1] score=0.566 | it/access-control-sop.md
  [2] score=0.506 | it/access-control-sop.md
  [3] score=0.478 | hr/leave-policy-2026.pdf
[RAG] After select: 3 chunks

[RAG] Prompt:
Answer only from the retrieved context below.
If the context is insufficient to answer the question, say you do not know and do not make up information.
Cite the source field (in brackets like [1]) when possible.
Keep your answer short, clear, and factual.
Respond in the same language as the question.

Question: Ai phải phê duyệt để cấp quyền Level 3?

Context:
[1] it/access-control-sop.md | Section 2: Phân cấp quyền truy cập | score=0.57
Level 1 — Read Only:
Áp dụng cho: Tất cả nhân viên mới tr...

Answer: Để cấp quyền Level 3, cần phê duyệt của Line Manager, IT Admin và IT Security [1].  
Sources: ['it/access-control-sop.md', 'hr/leave-policy-2026.pdf']

Query: ERR-403-AUTH là lỗi gì?

[RAG] Query: ERR-403-AUTH là lỗi gì?
[RAG] Retrieved 10 candidates (mode=dense)
  [1] score=0.371 | it/access-control-sop.md
  [2] score=0.349 | it/access-control-sop.md
  [3] score=0.345 | support/sla-p1-2026.pdf
[RAG] After select: 3 chunks

[RAG] Prompt:
Answer only from the retrieved context below.
If the context is insufficient to answer the question, say you do not know and do not make up information.
Cite the source field (in brackets like [1]) when possible.
Keep your answer short, clear, and factual.
Respond in the same language as the question.

Question: ERR-403-AUTH là lỗi gì?

Context:
[1] it/access-control-sop.md | Section 3: Quy trình yêu cầu cấp quyền | score=0.37
Bước 1: Nhân viên tạo Access Request ticket trên Jira (project IT-ACC...

Answer: ERR-403-AUTH là lỗi liên quan đến việc xác thực quyền truy cập, thường xảy ra khi người dùng không có quyền truy cập vào tài nguyên yêu cầu. Tôi không có thông tin chi tiết hơn về lỗi này trong ngữ cảnh đã cung cấp.
Sources: ['it/access-control-sop.md', 'support/sla-p1-2026.pdf']

--- Sprint 3: So sánh strategies (bao gồm Rerank) ---

============================================================
Query: Quy trình phê duyệt cấp quyền Level 3?
============================================================

--- Strategy: dense ---
Answer: Quy trình phê duyệt cấp quyền Level 3 bao gồm các bước sau:

1. Nhân viên tạo Access Request ticket trên Jira (project IT-ACCESS).
2. Line Manager phê duyệt yêu cầu trong 1 ngày làm việc.
3. IT Admin kiểm tra compliance và cấp quyền.
4. IT Security review với Level 3 và Level 4.
5. Nhân viên nhận thông báo qua email khi quyền được cấp.

Thời gian xử lý tổng cộng là 3 ngày làm việc [1][2].
Sources: ['it/access-control-sop.md']

--- Strategy: sparse ---
Answer: Quy trình phê duyệt cấp quyền Level 3 bao gồm các bước sau:

1. Nhân viên tạo Access Request ticket trên Jira (project IT-ACCESS).
2. Line Manager phê duyệt yêu cầu trong 1 ngày làm việc.
3. IT Admin kiểm tra compliance và cấp quyền.
4. IT Security review với Level 3 và Level 4.
5. Nhân viên nhận thông báo qua email khi quyền được cấp [2].
Sources: ['it/access-control-sop.md']

--- Strategy: hybrid ---
Answer: Quy trình phê duyệt cấp quyền Level 3 bao gồm các bước sau:

1. Nhân viên tạo Access Request ticket trên Jira (project IT-ACCESS).
2. Line Manager phê duyệt yêu cầu.
3. IT Admin kiểm tra compliance và cấp quyền.
4. IT Security review.
5. Nhân viên nhận thông báo qua email khi quyền được cấp.

Thời gian xử lý là 3 ngày làm việc và phê duyệt cần có sự đồng ý của Line Manager, IT Admin 
và IT Security [1][2].
Sources: ['it/access-control-sop.md']

--- Strategy: hybrid + rerank ---
Answer: Quy trình phê duyệt cấp quyền Level 3 bao gồm các bước sau:

1. Nhân viên tạo Access Request ticket trên Jira (project IT-ACCESS).
2. Line Manager phê duyệt yêu cầu.
3. IT Admin kiểm tra compliance và cấp quyền.
4. IT Security review.
5. Nhân viên nhận thông báo qua email khi quyền được cấp.

Thời gian xử lý là 3 ngày làm việc và phê duyệt cần có sự đồng ý của Line Manager, IT Admin 
và IT Security [1][2].
Sources: ['it/access-control-sop.md']

============================================================
Query: ERR-403-AUTH
============================================================

--- Strategy: dense ---
Answer: Tôi không biết.
Sources: ['it/access-control-sop.md']

--- Strategy: sparse ---
Answer: ERR-403-AUTH có thể liên quan đến việc không có quyền truy cập phù hợp theo quy trình cấp phép truy cập của công ty. Để được cấp quyền, nhân viên cần tạo Access Request ticket 
và có sự phê duyệt từ Line Manager cũng như IT Admin, tùy thuộc vào cấp độ quyền yêu cầu [1][2][3].
Sources: ['it/access-control-sop.md']

--- Strategy: hybrid ---
Answer: ERR-403-AUTH có thể liên quan đến việc không có quyền truy cập vào hệ thống nội bộ của công ty. Để yêu cầu cấp quyền, nhân viên cần tạo một Access Request ticket trên Jira và thực hiện theo quy trình đã quy định [1].
Sources: ['it/access-control-sop.md']

--- Strategy: hybrid + rerank ---
Answer: ERR-403-AUTH có thể liên quan đến việc không có quyền truy cập vào hệ thống. Để cấp 
quyền, nhân viên cần tạo một Access Request ticket trên Jira và tuân theo quy trình phê duyệt [2].
Sources: ['it/access-control-sop.md']


Việc cần làm Sprint 2:
  1. Implement retrieve_dense() — query ChromaDB
  2. Implement call_llm() — gọi OpenAI hoặc Gemini
  3. Chạy rag_answer() với 3+ test queries
  4. Verify: output có citation không? Câu không có docs → abstain không?