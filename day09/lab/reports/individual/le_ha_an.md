## Báo Cáo Cá Nhân — Lab Day 09: Multi-Agent Orchestration
Họ và tên: Lê Hà An

Vai trò trong nhóm: Supervisor Owner / Prototype Lead

Ngày nộp: 14/04/2026

Độ dài yêu cầu: 500–800 từ

## 1. Tôi phụ trách phần nào? (100–150 từ)
Tôi trực tiếp chịu trách nhiệm thiết kế và cài đặt "bộ não" điều phối của toàn bộ hệ thống. Nhiệm vụ của tôi là chuyển đổi từ một pipeline RAG tuyến tính sang kiến trúc Graph linh hoạt nhằm xử lý các yêu cầu phức tạp từ phụ huynh và nhân viên hỗ trợ.

Module/file tôi chịu trách nhiệm:

File chính: graph.py

Functions tôi implement: supervisor_node, route_decision, human_review_node, make_initial_state.

Cách công việc của tôi kết nối với phần của thành viên khác:
Tôi định nghĩa Shared State (AgentState), đóng vai trò là "bộ nhớ chung" xuyên suốt graph. Supervisor của tôi phân tích ý định (intent) để quyết định gửi tác vụ đến đúng Worker chuyên biệt (Retrieval hoặc Policy) và nhận lại kết quả để tổng hợp.

Bằng chứng: File graph.py với logic phân loại intent đa tầng đã được hoàn thiện trong Sprint 1.

## 2. Tôi đã ra một quyết định kỹ thuật gì? (150–200 từ)
Quyết định: Tôi chọn triển khai Logic định tuyến ưu tiên theo tầng (Tiered Priority Routing) dựa trên từ khóa và mức độ rủi ro, thay vì chỉ sử dụng LLM để phân loại intent đơn thuần.

Lý do: Việc gọi LLM chỉ để phân loại (Classification) tốn kém tài nguyên và độ trễ cao (~800ms). Tôi thiết lập một bộ lọc từ khóa chuyên biệt (policy, risk, error) để xử lý các tác vụ nghiệp vụ nhanh chóng. Đặc biệt, tôi ưu tiên kiểm tra rủi ro (risk_high) trước khi quyết định các bước tiếp theo để đảm bảo tính an toàn hệ thống.

Trade-off đã chấp nhận: Chấp nhận sự cứng nhắc của từ khóa (Keyword-based) so với sự linh hoạt của Semantic search. Tuy nhiên, với dữ liệu nội bộ Teki có thuật ngữ ổn định, cách này hiệu quả hơn.

Bằng chứng từ trace/code:

Python
# Logic ưu tiên Risk trước Policy
if any(kw in task for kw in risk_keywords):
    risk_high = True
    route_reason = "Phát hiện rủi ro cao/SLA P1."

if any(kw in task for kw in policy_keywords):
    route = "policy_tool_worker"
## 3. Tôi đã sửa một lỗi gì? (150–200 từ)
Lỗi: TypeError: AgentMessage.__init__() got an unexpected keyword argument 'sender'.

Symptom: Pipeline bị crash ngay lập tức khi Supervisor cố gắng khởi tạo một tin nhắn để gửi cho Worker.

Root cause: Lỗi nằm ở việc định nghĩa dataclass cho AgentMessage. Tôi đã sử dụng pass mà không khai báo Type Hints cho các trường dữ liệu, dẫn đến việc Decorator @dataclass không tự động tạo hàm __init__ với các tham số tương ứng.

Cách sửa: Tôi đã loại bỏ pass và khai báo rõ ràng kiểu dữ liệu cho 5 trường: sender: str, receiver: str, task: str, context: dict, và expected_output_format: str.

Bằng chứng trước/sau:

Trước: class AgentMessage: pass -> Gây lỗi unexpected keyword argument.

Sau: Khai báo đầy đủ thuộc tính giúp Supervisor có thể gọi AgentMessage(sender="Supervisor", ...) thành công mà không gây crash hệ thống.

## 4. Tôi tự đánh giá đóng góp của mình (100–150 từ)
Tôi làm tốt nhất ở điểm nào?
Tôi đã xây dựng được một hệ thống Traceability (Truy vết) minh bạch. Mọi bước đi của AI từ việc tại sao chọn route đó đến việc con người can thiệp khi nào đều được ghi lại trong history.

Tôi làm chưa tốt hoặc còn yếu ở điểm nào?
Phần xử lý ngoại lệ khi tất cả các Worker đều trả về kết quả rỗng (Null response) vẫn còn đơn giản, chủ yếu dựa vào synthesis để báo lỗi.

Nhóm phụ thuộc vào tôi ở đâu?
Nếu supervisor_node không hoạt động, toàn bộ hệ thống sẽ bị block vì không có Agent nào nhận được tác vụ để thực hiện.

Phần tôi phụ thuộc vào thành viên khác:
Tôi cần các Worker Owner cung cấp định dạng Output chuẩn (Contract) để Supervisor có thể tổng hợp dữ liệu vào AgentState chính xác.

## 5. Nếu có thêm 2 giờ, tôi sẽ làm gì? (50–100 từ)
Tôi sẽ triển khai Sub-query Decomposition trong supervisor_node. Trace của các câu hỏi phức tạp (như gq06) cho thấy một Agent đơn lẻ gặp khó khăn khi tổng hợp dữ liệu từ hai tài liệu chính sách khác nhau. Tôi muốn Supervisor có khả năng xé nhỏ task thành 2 sub-tasks chạy song song để tối ưu Context Recall.