# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Nguyễn Đức Mạnh  
**Vai trò trong nhóm:** Tech Lead  
**Ngày nộp:** 13/04/2026  

---

## 1. Tôi đã làm gì trong lab này?

Với vai trò Tech Lead, tôi tập trung chủ yếu vào Sprint 1 (Khởi tạo hệ thống) và Sprint 3 (Thử nghiệm và vận hành Pipeline). Tôi chịu trách nhiệm thiết kế cấu trúc kỹ thuật ban đầu, triển khai module vector database (ChromaDB) để lưu trữ các document chunks. Tôi đảm bảo quá trình indexing và vectorization hoạt động chính xác, khắc phục triệt để lỗi "Collection does not exist" để Retrieval Owner có cơ sở dữ liệu để test query. 

Ở Sprint 3, tôi đã tích hợp trực tiếp Generator (LLM) với Retriever, tạo thành end-to-end RAG pipeline vận hành trơn tru. Ngoài ra, tôi hỗ trợ Eval Owner thiết lập hệ thống chấm điểm tự động. Quyết định kỹ thuật quan trọng nhất tôi đưa ra là cách tổ chức kiến trúc loose-coupling giữa Retriever và Generator, giúp mọi người trong team có thể thay đổi prompt hoặc thuật toán search mà không làm gãy pipeline chung.

---

## 2. Điều tôi hiểu rõ hơn sau lab này

Sau bài lab, tôi đã thực sự hiểu sâu sắc hơn về **Chunking Strategy và luồng hoạt động của vòng lặp Evaluation**. 

Trước đây, tôi nghĩ để tìm kiếm tốt chỉ cần vứt văn bản vào một vector database là xong. Tuy nhiên, qua thực hành tôi thấy rõ: nếu kích thước "chunk" quá lớn, LLM sẽ bị nhiễu bởi các thông tin không liên quan; nếu quá nhỏ, đoạn text sẽ thiếu ngữ cảnh semantic. Việc tinh chỉnh chunk_size/chunk_overlap quyết định trực tiếp đến chất lượng của Retriever. Thêm vào đó, việc dùng bộ test (Evaluation loop) liên tục đo lường `ndcg@10` hay completeness mới là cách duy nhất chứng minh pipeline đang tiến bộ chứ không phải "cảm tính".

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn

Khó khăn mất nhiều thời gian debug nhất với tôi chính là lỗi cấu hình môi trường khởi tạo ChromaDB ban đầu (vấn đề persistency). Database khi chạy in-memory thường bay mất data, khiến việc query bị lỗi "Collection does not exist", tôi đã phải tinh chỉnh cấu hình đường dẫn lưu trữ cố định.

Bên cạnh đó, tôi ngạc nhiên khi thấy LLM đôi khi vẫn bị "hallucination" cho dù context đưa vào là chính xác. Giả thuyết ban đầu của tôi là: cung cấp context đúng, mô hình tự nhiên sẽ trả lời đúng. Nhưng thực tế, nó vẫn có xu hướng tự biên dịch thêm bằng kiến thức nền (prior knowledge). Điều này buộc tôi phải bổ sung các cấu trúc prompt khắt khe (ví dụ: "Chỉ trả lời dựa trên context được cho"). 

---

## 4. Phân tích một câu hỏi trong scorecard

**Câu hỏi:** SLA xử lý ticket P1 đã thay đổi như thế nào so với phiên bản trước? (Câu hỏi gq01)

**Phân tích:**
- **Baseline trả lời:** Thường là **sai** hoặc thiếu so sánh rõ ràng. Baseline lấy lên được số 4 giờ, nhưng vì thiếu kĩ thuật trích xuất nhiều phiên bản tài liệu nên không thấy được sự thay đổi từ 6 giờ xuống 4 giờ. Điểm cho Baseline thường thấp.
- **Lỗi nằm ở đâu:** Lỗi chính nằm ở **Retrieval**. Vector search thông thường có xu hướng tìm các chunk có độ tương đồng nghĩa cao nhất nhưng không phân biệt được metadata về *phiên bản* thời gian (versioning/freshness). 
- **Variant có cải thiện không?** Chắc chắn **Có**. Khi áp dụng các variant có **Metadata Filtering** (lọc theo ngày/version mới nhất) hoặc **Hybrid Search / Reranking** ưu tiên freshness, Retriever trả về đúng chunk của phiên bản v2026.1 (SLA 4 giờ) kết hợp với tài liệu tham chiếu cũ. Từ đó Generation có đủ fact để tổng hợp cả hai mốc thời gian hoàn chỉnh.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì?

Nếu có thêm thời gian, tôi sẽ thử triển khai **Cross-Encoder Reranking**. Kết quả eval cho thấy Pipeline hiện tại làm rất tốt các câu fact-checking đơn giản, nhưng lại đuối ở những câu hỏi phải tổng hợp từ nhiều tài liệu (Cross-document). Khâu bi-encoder đôi lúc xếp các tài liệu bổ trợ ra ngoài khoảng top-K. Việc dùng thêm một bước Reranker tái đánh giá lại top 20 kết quả sẽ giúp đẩy những chunk thực sự liên quan lên đầu, tối ưu chất lượng context cho Generator.
