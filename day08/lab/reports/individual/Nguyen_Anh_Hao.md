# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Nguyễn Anh Hào  
**Vai trò trong nhóm:** Eval Owner / Documentation Owner  
**Ngày nộp:** 13/04/2026 
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

> Mô tả cụ thể phần bạn đóng góp vào pipeline:
> - Sprint nào bạn chủ yếu làm?
> - Cụ thể bạn implement hoặc quyết định điều gì?
> - Công việc của bạn kết nối với phần của người khác như thế nào?

Trong bài lab này, mình đảm nhận vai trò chính là Eval & Documentation Owner, tập trung chủ yếu vào Sprint 3 và 4. Ở Sprint 3, tiếp nối phần Hybrid Retrieval của Hải, mình đã cài đặt thêm cơ chế LLM Reranking vào `rag_answer.py` để làm "phễu lọc" cuối cùng cho các đoạn văn bản. Sang Sprint 4, mình dành phần lớn thời gian xây dựng module đánh giá tự động (LLM-as-Judge) trong `eval.py`. Mình đã setup để hệ thống tự động chấm điểm bộ câu hỏi thử nghiệm dựa trên 4 tiêu chí quan trọng: Faithfulness, Relevance, Recall và Completeness, từ đó xuất ra bảng Scorecard để cả nhóm cùng phân tích hiệu quả tuning.

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

> Chọn 1-2 concept từ bài học mà bạn thực sự hiểu rõ hơn sau khi làm lab.
> Ví dụ: chunking, hybrid retrieval, grounded prompt, evaluation loop.
> Giải thích bằng ngôn ngữ của bạn — không copy từ slide.

1. **Tư duy "lọc phễu" (Funnel Retrieval)**: Mình thực sự hiểu ra rằng không phải cứ nhồi thật nhiều context vào là tốt. Việc kết hợp Hybrid Retrieval để quét rộng (tăng Recall) rồi dùng Rerank để chốt lại những đoạn chất lượng nhất (tăng Precision) giúp câu trả lời của model "sạch" và chính xác hơn hẳn.
2. **Sức mạnh của Evaluation tự động**: Thay vì ngồi chấm tay từng câu rất tốn sức và cảm tính, việc dùng LLM làm Judge giúp quy trình đánh giá diễn ra cực nhanh và nhất quán. Nhìn vào bảng Scorecard, mình biết ngay Variant nào thực sự hiệu quả để tập trung cải thiện.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

> Điều gì xảy ra không đúng kỳ vọng?
> Lỗi nào mất nhiều thời gian debug nhất?
> Giả thuyết ban đầu của bạn là gì và thực tế ra sao?

Vấn đề mình gặp khó khăn nhất là việc xử lý format output của LLM khi chạy Rerank và Eval. Dù đã nhắc model chỉ trả về JSON, nhưng thi thoảng nó vẫn "khuyến mãi" thêm vài câu giải thích, làm code bị lỗi khi parse dữ liệu. Mình đã phải loay hoay thêm bước dùng Regex để trích xuất JSON mới chạy ổn định được. Ngoài ra, việc dùng LLM để Rerank kết quả tuy ngon thật nhưng lại bị đánh đổi bởi độ trễ (latency) khá cao, làm trải nghiệm dùng thử cảm giác chưa được mượt mà như mong đợi.

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

> Chọn 1 câu hỏi trong test_questions.json mà nhóm bạn thấy thú vị.
> Phân tích:
> - Baseline trả lời đúng hay sai? Điểm như thế nào?
> - Lỗi nằm ở đâu: indexing / retrieval / generation?
> - Variant có cải thiện không? Tại sao có/không?

**Câu hỏi:** q07 - "Approval Matrix để cấp quyền hệ thống là tài liệu nào?"

**Phân tích:**
- **Baseline**: Trả lời sai hoặc báo không tìm thấy thông tin vì từ khóa "Approval Matrix" không khớp chính xác với tiêu đề file (vốn đã được đổi tên). Đây là lỗi điển hình của việc thiếu Recall ở bước Retrieval.
- **Cải thiện ở Variant**: Kết quả tốt hơn hẳn nhờ **Hybrid Retrieval** (BM25 bắt được từ "Approval" trong nội dung văn bản) và **Rerank** (LLM nhận diện được "Access Control SOP" chính là tài liệu thay thế). Dù điểm Relevance đạt tối đa 5/5, nhưng điểm Completeness vẫn hơi thấp (2/5) vì model chưa giải thích kỹ về việc đổi tên tài liệu như mình kỳ vọng.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

> 1-2 cải tiến cụ thể bạn muốn thử.
> Không phải "làm tốt hơn chung chung" mà phải là:
> "Tôi sẽ thử X vì kết quả eval cho thấy Y."

Nếu còn thời gian, mình sẽ thử thay thế LLM Reranking bằng các model **Cross-Encoder** chuyên dụng (như ms-marco-MiniLM) để giải quyết triệt để vấn đề tốc độ. Bên cạnh đó, mình muốn thử thêm hướng **Metadata Filtering** theo phòng ban hoặc loại tài liệu. Nếu lọc được bớt "nhiễu" ngay từ đầu thì chắc chắn độ chính xác của hệ thống sẽ còn vượt ngưỡng 90% một cách dễ dàng.

---

*Lưu file này với tên: `reports/individual/[ten_ban].md`*
*Ví dụ: `reports/individual/nguyen_van_a.md`*
