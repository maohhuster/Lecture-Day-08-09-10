# Báo Cáo Cá Nhân — Lab Day 09: Multi-Agent Orchestration

**Họ và tên:** Nguyễn Anh Hào  
**Vai trò trong nhóm:** Worker Owner  
**Ngày nộp:** 14/04/2026  
**Độ dài yêu cầu:** 500–800 từ

---

> **Lưu ý quan trọng:**
> - Viết ở ngôi **"tôi"**, gắn với chi tiết thật của phần bạn làm
> - Phải có **bằng chứng cụ thể**: tên file, đoạn code, kết quả trace, hoặc commit
> - Nội dung phân tích phải khác hoàn toàn với các thành viên trong nhóm
> - Deadline: Được commit **sau 18:00** (xem SCORING.md)
> - Lưu file với tên: `reports/individual/[ten_ban].md` (VD: `nguyen_van_a.md`)

---

## 1. Tôi phụ trách phần nào? (100–150 từ)

> Mô tả cụ thể module, worker, contract, hoặc phần trace bạn trực tiếp làm.
> Không chỉ nói "tôi làm Sprint X" — nói rõ file nào, function nào, quyết định nào.

**Module/file tôi chịu trách nhiệm:**
- File chính: `workers/retrieval.py` và `workers/policy_tool.py`
- Functions tôi implement: `retrieve_dense`, `analyze_policy`, `run`

**Cách công việc của tôi kết nối với phần của thành viên khác:**

Tôi chịu trách nhiệm cung cấp dữ liệu đầu vào (Context) và kết quả phân tích nghiệp vụ (Policy) cho toàn bộ pipeline. Kết quả từ `retrieval_worker` được chuyển tiếp cho `policy_tool_worker` để kiểm tra ngoại lệ. Cuối cùng, `policy_result` của tôi là thành phần bắt buộc để Synthesis Worker có thể viết câu trả lời chính xác cho khách hàng. Nếu Retrieval của tôi lỗi, Supervisor sẽ không có cơ sở để ra quyết định.

**Bằng chứng (commit hash, file có comment tên bạn, v.v.):**

- File `workers/retrieval.py` và `workers/policy_tool.py` trong repo với logic xử lý ChromaDB và logic rule-based exceptions.
- Commit fd8fc0d8108c737f24359387b5d16fd9e4f4b56c. add worker policy and retrieval - nanhhao04



---

## 2. Tôi đã ra một quyết định kỹ thuật gì? (150–200 từ)

> Chọn **1 quyết định** bạn trực tiếp đề xuất hoặc implement trong phần mình phụ trách.
> Giải thích:
> - Quyết định là gì?
> - Các lựa chọn thay thế là gì?
> - Tại sao bạn chọn cách này?
> - Bằng chứng từ code/trace cho thấy quyết định này có effect gì?

**Quyết định:** Sử dụng **Rule-based Exception Detection** ưu tiên trước khi gọi LLM để xử lý các ngoại lệ chính sách như Flash Sale hay Sản phẩm số.

**Ví dụ:**
> "Tôi chọn dùng keyword-based routing trong supervisor_node thay vì gọi LLM để classify.
>  Lý do: keyword routing nhanh hơn (~5ms vs ~800ms) và đủ chính xác cho 5 categories.
>  Bằng chứng: trace gq01 route_reason='task contains P1 SLA keyword', latency=45ms."

**Lý do:**

Ban đầu tôi định để LLM tự quét chính sách, nhưng thực tế cho thấy LLM đôi khi bỏ sót các quy định cực ngắn nhưng quan trọng (như "Flash Sale không được hoàn tiền"). Việc dùng LLM cho mọi câu hỏi cũng làm tăng latency lên ~1 giây. Tôi quyết định dùng Regex/Keyword matching trong `analyze_policy` để bắt nhanh các case  này. Điều này đảm bảo tính deterministic (luôn đúng 100% với từ khóa) và giảm đáng kể chi phí/thời gian xử lý.

**Trade-off đã chấp nhận:**

Cách này đòi hỏi bộ từ khóa phải được cập nhật thủ công nếu chính sách công ty thay đổi, không linh hoạt hoàn toàn bằng LLM nhưng cực kỳ an toàn cho các nghiệp vụ liên quan đến tài chính/hoàn tiền.

**Bằng chứng từ trace/code:**

```python
# Rule-based check cho Flash Sale trong workers/policy_tool.py
if "flash sale" in task_lower or "flash sale" in context_text:
    exceptions_found.append({
        "type": "flash_sale_exception",
        "rule": "Đơn hàng Flash Sale không được hoàn tiền (Điều 3, chính sách v4).",
        "source": "policy_refund_v4.txt",
    })
```

---

## 3. Tôi đã sửa một lỗi gì? (150–200 từ)

> Mô tả 1 bug thực tế bạn gặp và sửa được trong lab hôm nay.
> Phải có: mô tả lỗi, symptom, root cause, cách sửa, và bằng chứng trước/sau.

**Lỗi:** Lỗi không nhận diện được ngoại lệ do phân biệt chữ hoa/chữ thường (Case-sensitivity).

**Symptom (pipeline làm gì sai?):**

Khi người dùng hỏi "Tôi mua FLASH SALE có được hoàn tiền không?", hệ thống bỏ qua rule-based check và đi thẳng vào LLM hoặc trả về "Không có ngoại lệ", dẫn đến kết quả sai lệch so với quy định cứng.

**Root cause (lỗi nằm ở đâu — indexing, routing, contract, worker logic?):**

Lỗi nằm ở logic so khớp chuỗi trong `analyze_policy`. Tôi sử dụng `if "flash sale" in task`, nhưng biến `task` chứa chuỗi "FLASH SALE", dẫn đến kết quả trả về `False`.

**Cách sửa:**

Tôi đã thực hiện chuẩn hóa toàn bộ input đầu vào (cả `task` và `context`) sang chữ thường bằng hàm `.lower()` trước khi thực hiện bất kỳ so khớp nào.

**Bằng chứng trước/sau:**

Trước khi sửa: Task "FLASH SALE" -> không tìm thấy exception.
Sau khi sửa: Task "FLASH SALE" -> `.lower()` thành "flash sale" -> khớp đúng rule và trả về từ chối hoàn tiền chính xác.

---

## 4. Tôi tự đánh giá đóng góp của mình (100–150 từ)

> Trả lời trung thực — không phải để khen ngợi bản thân.

**Tôi làm tốt nhất ở điểm nào?**

Tôi đã đóng gói được các Worker một cách độc lập. Việc có hàm `if __name__ == "__main__":` giúp tôi test Retrieval và Policy Tool cực nhanh mà không cần chờ khởi động toàn bộ Graph.

**Tôi làm chưa tốt hoặc còn yếu ở điểm nào?**

Phần tích hợp MCP thực thụ (thông qua server/client) của tôi còn sơ sài, hiện tại vẫn đang dùng file import trực tiếp thay vì giao tiếp qua protocol chuẩn.

**Nhóm phụ thuộc vào tôi ở đâu?** _(Phần nào của hệ thống bị block nếu tôi chưa xong?)_

Nếu `policy_tool_worker` của tôi không trả về đúng format `policy_result`, bạn Synthesis sẽ không có "nguyên liệu" để giải thích cho khách hàng lý do tại sao họ bị từ chối hoàn tiền.

**Phần tôi phụ thuộc vào thành viên khác:** _(Tôi cần gì từ ai để tiếp tục được?)_

Tôi cần Supervisor Owner xác định đúng lúc nào cần gọi tool (`needs_tool`) để tôi thực hiện truy vấn thêm thông tin từ hệ thống bên ngoài.

---

## 5. Nếu có thêm 2 giờ, tôi sẽ làm gì? (50–100 từ)

> Nêu **đúng 1 cải tiến** với lý do có bằng chứng từ trace hoặc scorecard.
> Không phải "làm tốt hơn chung chung" — phải là:
> *"Tôi sẽ thử X vì trace của câu gq___ cho thấy Y."*

Tôi sẽ bổ sung **Hybrid Search** cho Retrieval Worker. Hiện tại tôi chỉ dùng vector search nên với các mã đơn hàng hoặc tên sản phẩm đặc thù (như "SUBS-2026"), ChromaDB đôi khi trả về kết quả mờ nhạt. Tôi sẽ thêm lớp BM25 keyword search để đảm bảo các thực thể định danh luôn được tìm thấy chính xác như yêu cầu của khách hàng.

---

*Lưu file này với tên: `reports/individual/Nguyen_Anh_Hao.md`*  
*Ví dụ: `reports/individual/nguyen_van_a.md`*
