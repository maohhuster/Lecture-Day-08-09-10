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