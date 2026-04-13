# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Lê Ngọc Hải 
**Vai trò trong nhóm:**  Retrieval Owner   
**Ngày nộp:** 13/04/2026  
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

> Mô tả cụ thể phần bạn đóng góp vào pipeline:
> - Sprint nào bạn chủ yếu làm?
> - Cụ thể bạn implement hoặc quyết định điều gì?
> - Công việc của bạn kết nối với phần của người khác như thế nào?

Tôi chủ yếu làm **Sprint 3** với vai trò Retrieval Owner, tập trung vào việc implement **variant hybrid** (Dense + Sparse/BM25 kết hợp qua Reciprocal Rank Fusion). Cụ thể, tôi đã:

1. **Implement hàm `retrieve_sparse()`**: sử dụng thư viện `rank_bm25` (BM25Okapi) để thực hiện keyword-based retrieval. Tôi load toàn bộ chunks từ ChromaDB, tokenize corpus và query, rồi trả về top-k kết quả theo BM25 score.

2. **Implement hàm `retrieve_hybrid()`**: kết hợp kết quả từ `retrieve_dense()` và `retrieve_sparse()` bằng thuật toán RRF (Reciprocal Rank Fusion) với trọng số `dense_weight=0.6`, `sparse_weight=0.4`. Tôi dùng text chunk làm key để merge và tính RRF score theo công thức chuẩn `1/(60 + rank)`.

3. **Quyết định chọn hybrid thay vì rerank hoặc query transform**, vì phân tích error tree từ baseline cho thấy dense bỏ lỡ exact keyword match (ví dụ query "ERR-403-AUTH" và "Approval Matrix") — hybrid bổ sung BM25 sparse search giải quyết đúng pain point này.

Công việc của tôi kết nối trực tiếp với phần indexing (Sprint 1) — tôi sử dụng ChromaDB index đã được đồng đội tạo sẵn, và output retrieval của tôi được truyền vào hàm `rag_answer()` (Sprint 2) để sinh câu trả lời có citation.

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

> Chọn 1-2 concept từ bài học mà bạn thực sự hiểu rõ hơn sau khi làm lab.
> Ví dụ: chunking, hybrid retrieval, grounded prompt, evaluation loop.
> Giải thích bằng ngôn ngữ của bạn — không copy từ slide.

Sau lab này, tôi hiểu rõ hơn hai concept: **hybrid retrieval** và **Reciprocal Rank Fusion (RRF)**.

**Hybrid retrieval**: Trước lab, tôi nghĩ dense search (embedding similarity) là đủ cho mọi trường hợp. Nhưng khi chạy baseline, query chứa mã lỗi "ERR-403-AUTH" bị dense bỏ qua hoàn toàn vì embedding không capture được exact term — nó tìm theo "nghĩa" chứ không theo "từ". BM25 ngược lại, rất giỏi match keyword chính xác nhưng lại yếu khi người dùng paraphrase câu hỏi. Hybrid kết hợp cả hai giúp pipeline vừa hiểu ngữ nghĩa vừa bắt được keyword cụ thể — đây là bài học thực tế mà slide chỉ nói lý thuyết.

**RRF (Reciprocal Rank Fusion)**: Tôi hiểu rõ hơn cách merge hai danh sách kết quả khác hệ điểm. Dense trả score cosine (0-1), BM25 trả score không cùng scale — không thể cộng trực tiếp. RRF giải quyết bằng cách chỉ dùng **thứ hạng** (rank) thay vì score gốc: `1/(60 + rank)`. Công thức đơn giản nhưng hiệu quả, tránh được vấn đề normalize score giữa hai hệ thống khác nhau.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

> Điều gì xảy ra không đúng kỳ vọng?
> Lỗi nào mất nhiều thời gian debug nhất?
> Giả thuyết ban đầu của bạn là gì và thực tế ra sao?

Điều ngạc nhiên nhất là **hybrid không tốt hơn baseline ở mọi câu hỏi** như tôi kỳ vọng. Giả thuyết ban đầu: thêm BM25 sẽ chỉ có lợi, ít nhất không làm kém đi. Thực tế, câu q06 ("Escalation trong sự cố P1 diễn ra như thế nào?") bị regression nghiêm trọng — Completeness từ 4 xuống 1. Nguyên nhân: BM25 match keyword "P1" trong tài liệu access_control_sop (quyền tạm thời cho sự cố P1) thay vì tài liệu SLA đúng. RRF đẩy chunk sai lên top, khiến LLM sinh câu trả lời lạc đề về "cấp quyền tạm thời" thay vì "escalate lên Senior Engineer".

Lỗi mất thời gian debug nhất là **tokenization cho BM25**. Ban đầu tôi chỉ dùng `split()` đơn giản, nhưng tiếng Việt không tách từ bằng khoảng trắng giống tiếng Anh, dẫn đến BM25 score không chính xác cho một số query. Tôi cũng mất thời gian xử lý trường hợp chunk trùng nhau giữa dense và sparse khi merge — phải dùng text content làm key thay vì metadata vì metadata có thể trùng giữa các chunk khác nhau.

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

> Chọn 1 câu hỏi trong test_questions.json mà nhóm bạn thấy thú vị.
> Phân tích:
> - Baseline trả lời đúng hay sai? Điểm như thế nào?
> - Lỗi nằm ở đâu: indexing / retrieval / generation?
> - Variant có cải thiện không? Tại sao có/không?

**Câu hỏi:** q09 — "ERR-403-AUTH là lỗi gì và cách xử lý?"

**Phân tích:**

Đây là câu hỏi thú vị nhất vì nó cho thấy rõ **sự khác biệt giữa dense và hybrid retrieval**, đồng thời cũng bộc lộ **giới hạn của cả hai**.

**Baseline (dense):** Trả lời sai hướng. Dense tìm được context từ access_control_sop (liên quan đến quyền truy cập) nhưng **hallucinate** — nó tự suy luận "ERR-403-AUTH là lỗi liên quan đến quyền truy cập" và gợi ý tạo Access Request ticket trên Jira. Điểm Faithfulness = 5 (vì claim có trong context), nhưng Relevance = 5 và Completeness = 2. Lỗi ở đây nằm ở **retrieval**: dense tìm theo semantic similarity "lỗi + quyền truy cập" và trả về chunk liên quan nhưng không chứa thông tin về mã lỗi cụ thể ERR-403-AUTH. Expected answer là "Không tìm thấy thông tin, liên hệ IT Helpdesk" — pipeline đáng lẽ phải **abstain**.

**Variant hybrid:** Cải thiện ở chỗ pipeline trả lời "Tôi không biết" — đúng hành vi abstain khi không có đủ context. Faithfulness = 5, nhưng Relevance = 1, Completeness = 1. BM25 tìm keyword "ERR-403-AUTH" nhưng không có chunk nào chứa exact match, nên hybrid không trả về context đủ mạnh → LLM nhận ra và abstain thay vì bịa.

**Bài học:** Hybrid giúp pipeline "biết mình không biết" tốt hơn dense. Dense quá tự tin vì luôn tìm được chunk "gần nghĩa", dù chunk đó không thực sự trả lời câu hỏi. Tuy nhiên, cả hai đều chưa đạt expected answer lý tưởng (gợi ý liên hệ IT Helpdesk). Lỗi gốc nằm ở **indexing** — corpus không có tài liệu nào mô tả mã lỗi ERR-403-AUTH.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

> 1-2 cải tiến cụ thể bạn muốn thử.
> Không phải "làm tốt hơn chung chung" mà phải là:
> "Tôi sẽ thử X vì kết quả eval cho thấy Y."

1. **Thêm rerank layer sau hybrid retrieval** — vì q06 cho thấy RRF fusion đẩy chunk sai lên top khi BM25 match keyword "P1" vào sai document. Cross-encoder rerank sẽ chấm lại relevance của từng chunk so với query gốc, loại bỏ chunk access_control_sop không liên quan đến escalation SLA.

2. **Điều chỉnh sparse_weight theo category** — kết quả eval cho thấy hybrid tốt cho query chứa exact term (ERR-403, Approval Matrix) nhưng gây regression cho query semantic thuần (Escalation P1). Tôi sẽ thử adaptive weighting: tăng sparse_weight khi query chứa mã lỗi/tên riêng, giảm khi query là câu hỏi tự nhiên.

---

*Lưu file này với tên: `reports/individual/[ten_ban].md`*
*Ví dụ: `reports/individual/nguyen_van_a.md`*
