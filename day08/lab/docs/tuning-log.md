# Tuning Log — RAG Pipeline (Day 08 Lab)

> Template: Ghi lại mỗi thay đổi và kết quả quan sát được.
> A/B Rule: Chỉ đổi MỘT biến mỗi lần.

---

## Baseline (Sprint 2)

**Ngày:** ___________  
**Config:**
```
retrieval_mode = "dense"
chunk_size = _____ tokens
overlap = _____ tokens
top_k_search = 10
top_k_select = 3
use_rerank = False
llm_model = _____
```

**Scorecard Baseline:**
| Metric | Average Score |
|--------|--------------|
| Faithfulness | ? /5 |
| Answer Relevance | ? /5 |
| Context Recall | ? /5 |
| Completeness | ? /5 |

**Câu hỏi yếu nhất (điểm thấp):**
> TODO: Liệt kê 2-3 câu hỏi có điểm thấp nhất và lý do tại sao.
> Ví dụ: "q07 (Approval Matrix) - context recall = 1/5 vì dense bỏ lỡ alias."

**Giả thuyết nguyên nhân (Error Tree):**
- [ ] Indexing: Chunking cắt giữa điều khoản
- [ ] Indexing: Metadata thiếu effective_date
- [ ] Retrieval: Dense bỏ lỡ exact keyword / alias
- [ ] Retrieval: Top-k quá ít → thiếu evidence
- [ ] Generation: Prompt không đủ grounding
- [ ] Generation: Context quá dài → lost in the middle

---

## Variant 1 (Sprint 3)

**Ngày:** ___________  
**Biến thay đổi:** ___________  
**Lý do chọn biến này:**
> TODO: Giải thích theo evidence từ baseline results.
> Ví dụ: "Chọn hybrid vì q07 (alias query) và q09 (mã lỗi ERR-403) đều thất bại với dense.
> Corpus có cả ngôn ngữ tự nhiên (policy) lẫn tên riêng/mã lỗi (ticket code, SLA label)."

**Config thay đổi:**
```
retrieval_mode = "hybrid"   # hoặc biến khác
# Các tham số còn lại giữ nguyên như baseline
```

**Scorecard Variant 1:**
| Metric | Baseline | Variant 1 | Delta |
|--------|----------|-----------|-------|
| Faithfulness | ?/5 | ?/5 | +/- |
| Answer Relevance | ?/5 | ?/5 | +/- |
| Context Recall | ?/5 | ?/5 | +/- |
| Completeness | ?/5 | ?/5 | +/- |

**Nhận xét:**
> TODO: Variant 1 cải thiện ở câu nào? Tại sao?
> Có câu nào kém hơn không? Tại sao?

**Kết luận:**
> TODO: Variant 1 có tốt hơn baseline không?
> Bằng chứng là gì? (điểm số, câu hỏi cụ thể)

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