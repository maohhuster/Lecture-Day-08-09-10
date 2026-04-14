# Báo Cáo Cá Nhân — Lab Day 09: Multi-Agent Orchestration

**Họ và tên:** Nguyễn Ngọc Cường 
**Vai trò trong nhóm:** MCP Owner   
**Ngày nộp:** 14/4/2026
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
- File chính: `mcp_server.py, policy_tool.py và graph.py
- Functions tôi implement: `Implement mock MCP Server với 4 tools: search_kb: Tìm kiếm Knowledge Base nội bộ bằng semantic search, get_ticket_info: Tra cứu thông tin ticket từ hệ thống Jira nội bộ, check_access_permission: Kiểm tra điều kiện cấp quyền truy cập theo Access Control SO và create_ticket: Tạo ticket mới trong hệ thống Jira
mcp_server.py: tool_search_kb() Kết nối với ChromaDB thực
policy_tool.py: gọi MCP client để lấy kết quả thay vì truy cập ChromaDB trực tiếp ở hàm _call_mcp_tool()
Ghi lại mcp_tool_called và mcp_result vào trace ở trong file graph.py, supervisor_node(state: AgentState) để Supervisor ghi log "chọn MCP vs không chọn MCP" vào route_reason
chạy thử cả 3 file mcp_server.py, policy_tool.py và graph.py để kiểm tra thỏa mãn 4 điều kiện Spirit 3 và lưu log vào artifacts/traces/

**Cách công việc của tôi kết nối với phần của thành viên khác:**
Công việc của tôi kết nối với các phần khác: Cải tiến graph.py để mcp_tool_called và mcp_result được ghi vào trace
lưu log vào artifacts/traces/ để cho lưu thông tin vào Spirit 4
policy_tool.py từ bước 2 tận dụng và chỉnh sửa thêm để gọi MCP client để lấy kết quả ở hàm _call_mcp_tool()

**Bằng chứng (commit hash, file có comment tên bạn, v.v.):**

mcp_server.py, policy_tool.py và graph.py
username: 21020285-art

---

## 2. Tôi đã ra một quyết định kỹ thuật gì? (150–200 từ)
Quyết định: Xây dựng Mock MCP Server với kiến trúc tập trung (qua hàm dispatch_tool và TOOL_REGISTRY) để chuẩn hóa giao tiếp giữa Policy Worker và các external tools, thay vì hard-code trực tiếp logic truy vấn vào bên trong Worker.

Lý do: Lựa chọn thay thế ban đầu là nhúng thẳng logic gọi ChromaDB và tra cứu Jira (mock dict) vào file workers/policy_tool.py. Tuy nhiên, tôi chọn cách tách riêng ra mcp_server.py vì nó đảm bảo tính Separation of Concerns (chia để trị). Policy Worker giờ đây chỉ đóng vai trò là một "Client" gọi công cụ. Cách này giúp hệ thống cực kỳ dễ mở rộng; sau này muốn thêm tool mới (như create_ticket), tôi chỉ cần đăng ký vào TOOL_REGISTRY ở Server mà không cần chạm vào code cốt lõi của Worker.

Trade-off đã chấp nhận: Chấp nhận việc tăng độ phức tạp của code base ở giai đoạn đầu (phải thiết kế schema cho từng tool, xử lý try/catch khi gọi hàm gián tiếp) đổi lấy khả năng bảo trì và scale dễ dàng về sau.

Bằng chứng từ trace/code:

# Trong workers/policy_tool.py: Worker không gọi DB trực tiếp mà gọi qua _call_mcp_tool
def _call_mcp_tool(tool_name: str, tool_input: dict) -> dict:
    from mcp_server import dispatch_tool
    result = dispatch_tool(tool_name, tool_input)
    return {
        "tool": tool_name,
        "input": tool_input,
        "output": result,
        "timestamp": datetime.now().isoformat(),
    }

## 3. Tôi đã sửa một lỗi gì? (150–200 từ)

> Mô tả 1 bug thực tế bạn gặp và sửa được trong lab hôm nay.
> Phải có: mô tả lỗi, symptom, root cause, cách sửa, và bằng chứng trước/sau.

Lỗi: ModuleNotFoundError khi Policy Worker gọi MCP Server. TÔi đã chạy ngay trước khi sửa code ở policy_tools.py do tôi nghĩ chỉ cần sửa mcp_server.py là xong

Symptom (pipeline làm gì sai?): Khi luồng câu hỏi định tuyến vào Policy Worker, worker không thể kích hoạt các external tools (như search_kb). Thay vì trả về kết quả policy, trạng thái policy_result báo lỗi MCP_CALL_FAILED. Do không có context, Synthesis Worker tổng hợp câu trả lời sai hoặc từ chối trả lời.

Root cause (lỗi nằm ở đâu): Lỗi nằm ở Worker logic (Import Path). Trong file workers/policy_tool.py, hàm gọi MCP đang hard-code đường dẫn tĩnh: from day09.lab.mcp_server import dispatch_tool. Khi chạy file graph.py (entry point) từ thư mục gốc lab/, Python Context không nhận diện được package theo đường dẫn này, gây crash module.

Cách sửa: Tôi đã refactor lại hàm _call_mcp_tool(). Thay vì import tĩnh, tôi dùng module os và sys để tự động nối chuỗi thư mục hiện tại với thư mục cha, sau đó đưa vào biến môi trường hệ thống trước khi gọi file.

Bằng chứng trước/sau:

Trước khi sửa (State Error Log):

JSON
"mcp_tools_used": [],
"policy_result": {
  "error": {"code": "MCP_CALL_FAILED", "reason": "No module named 'day09'"}
}
Sau khi sửa (Trace Success):

JSON
"mcp_tools_used": [
  {
    "tool": "search_kb",
    "input": {"query": "quyền admin P1", "top_k": 3},
    "output": {"chunks": [{"text": "...", "source": "access_control_sop.txt"}]},
    "timestamp": "2026-04-14T15:30:11"
  }
]

## 4. Tôi tự đánh giá đóng góp của mình (100–150 từ)

> Trả lời trung thực — không phải để khen ngợi bản thân.

**Tôi làm tốt nhất ở điểm nào?**
CÓ thể xử lý tốt phần việc mình được đưa ra mà không ảnh hưởng nhiều đến tiến trình của nhóm

**Tôi làm chưa tốt hoặc còn yếu ở điểm nào?**

Một số kỹ thuật cơ bản tôi đôi lúc bất cẩn chưa kiểm tra. ví dụ tôi lỡ đẩy code mà chưa tạo .gitignore và bỏ thư mục /venv hay việc chạy để kiểm tra đạt đủ điều kiện chưa tôi cần hỏi bạ ncungf nhóm để biết làm gì để kiểm tra tôi đã hoàn thành mục tiêu cảu Spirit 3

**Nhóm phụ thuộc vào tôi ở đâu?** _(Phần nào của hệ thống bị block nếu tôi chưa xong?)_

tool_search_kb() Kết nối với ChromaDB thực

**Phần tôi phụ thuộc vào thành viên khác:** _(Tôi cần gì từ ai để tiếp tục được?)_

Tôi phụ thuộc ban Hải để có thể hiểu rõ điều kiện tôi kiểm tra trong Spirit 3 có đạt đủ ddiefu kiện như yêu cầu không

---

## 5. Nếu có thêm 2 giờ, tôi sẽ làm gì? (50–100 từ)

> Nêu **đúng 1 cải tiến** với lý do có bằng chứng từ trace hoặc scorecard.
> Không phải "làm tốt hơn chung chung" — phải là:
> *"Tôi sẽ thử X vì trace của câu gq___ cho thấy Y."*

Hiện tại tôi chưa cần cải thiện vì lấy các câu test và có kết quả các câu đều khá chính xác. TUy nhiên, do buổi tối sẽ có 1 tập test khác nên câu trả lời này là chwua chắc chắn và câu kiểm tra lại sau. 
Tôi sẽ thử gq13 câu buổi chiều vì có chỉ số high_risk là cao nhưng độ confidence cũng là tận 0.9

---

*Lưu file này với tên: `reports/individual/[ten_ban].md`*  
*Ví dụ: `reports/individual/nguyen_van_a.md`*
