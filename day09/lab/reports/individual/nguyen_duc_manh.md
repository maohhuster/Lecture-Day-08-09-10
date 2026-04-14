# Báo Cáo Cá Nhân — Lab Day 09: Multi-Agent Orchestration

**Họ và tên:** Nguyễn Đức Mạnh
**Vai trò trong nhóm:** Trace & Docs Owner  
**Ngày nộp:** 14/04/2026  

---

> **Lưu ý quan trọng:**
> - Viết ở ngôi **"tôi"**, gắn với chi tiết thật của phần bạn làm
> - Phải có **bằng chứng cụ thể**: tên file, đoạn code, kết quả trace, hoặc commit
> - Nội dung phân tích phải khác hoàn toàn với các thành viên trong nhóm

---

## 1. Tôi phụ trách phần nào?

**Module/file tôi chịu trách nhiệm:**
- File chính: `eval_trace.py`, thư mục lưu trữ `artifacts/traces/`, và báo cáo `reports/group_report.md`
- Functions tôi implement: `analyze_traces()`, `compare_single_vs_multi()`, `run_grading_questions()`.

**Cách công việc của tôi kết nối với phần của thành viên khác:**
Vai trò của tôi là "người đánh giá". Khi Lê Hà An (Supervisor) và Lê Đức Hải / Nguyễn Anh Hào (Workers) hoàn tất phần core pipeline trong `graph.py` và `workers/`, tôi là người cung cấp các bộ công cụ chạy kiểm thử tự động, trích xuất metric và phân tích dữ liệu hiệu suất tổng hợp. Nhờ tool `eval_trace.py` của tôi thống kê tự động các fields như `routing_distribution` hay `avg_confidence`, nhóm mới có thể viết File Comparison (nhận ra confidence chỉ đạt `0.10` và thời gian chạy `~1ms`) để xác định được sự cố module synthesis bị fallback.

**Bằng chứng (commit hash, file có comment tên bạn, v.v.):**
Toàn bộ script `eval_trace.py` được tôi tinh chỉnh để hỗ trợ chế độ batch evaluation: `python eval_trace.py --grading` hay `--compare`. Trích file logic `eval_trace.py`:
```python
def analyze_traces(traces_dir: str = "artifacts/traces") -> dict:
# Load toàn bộ file trace JSON và trích xuất routing distribution
...
metrics = {
    "total_traces": total,
    "routing_distribution": {k: f"{v}/{total} ({100*v//total}%)" for k, v in routing_counts.items()},
    "avg_confidence": round(sum(confidences) / len(confidences), 3) if confidences else 0,
    ...
```

---

## 2. Tôi đã ra một quyết định kỹ thuật gì?

**Quyết định:** Tôi chọn lưu trữ mỗi trace dưới dạng một file JSON độc lập (`artifacts/traces/q01_<timestamp>.json`) thay vì thiết lập một database (SQLite) hay append vào một file log chung khổng lồ.

**Lý do:**
1. **Dễ đọc & Debug**: Cấu trúc JSON tĩnh được format đẹp giúp các bạn Worker Owner (Hải, Hào) mở thẳng bằng môi trường IDE xem `route_reason` và `workers_called` cho mỗi test case riêng rẽ ngay sau khi chạy lệnh test.
2. **Loại bỏ lock error**: Với pipeline có thể sau này scale chạy thread ngầm song song cho nhiều test questions cùng lúc, lưu JSON file sẽ tránh bị lock write I/O.
3. **Phù hợp scope lab**: Cực kỳ dễ parse lại bằng logic OS directory trong `analyze_traces()`.

**Trade-off đã chấp nhận:**
Khó truy vấn phức tạp nêú hệ thống test lớn hơn vài nghìn questions (phải load toàn bộ vào memory để scan thay vì chạy câu lệnh SELECT SQL). Tạo ra nhiều file nhỏ làm rác thư mục, phải tạo `.gitignore` riêng.

**Bằng chứng từ trace/code:**
Việc parse folder ở trong `eval_trace.py`:
```python
trace_files = [f for f in os.listdir(traces_dir) if f.endswith(".json")]
traces = []
for fname in trace_files:
    with open(os.path.join(traces_dir, fname), encoding='utf-8') as f:
        traces.append(json.load(f))
# Trace list sẽ độc lập để chạy aggregate mà không cần library ngoài
```

---

## 3. Tôi đã sửa một lỗi gì?

**Lỗi:** Trong lúc chạy `eval_trace.py` với `--grading`, nếu pipeline graph gặp lỗi unhandled exception (VD: node không tồn tại hoặc type error trong `AgentState`), hàm `run_grading_questions()` sẽ chêt luôn giữa vòng lặp, khiến `artifacts/grading_run.jsonl` không ghi lại được những câu chạy sau đó.

**Symptom (pipeline làm gì sai?):**
Chạy test báo `Exception...` xong tắt ngang terminal. Output report `.jsonl` để thầy cô chấm không có đủ các dòng grading questions dẫn tới việc "không có đáp án" cho script chấm điểm tự động. Console thường in thiếu kí tự do sai encoding.

**Root cause (lỗi nằm ở đâu — indexing, routing, contract, worker logic?):**
Lỗi nằm ở logic try-catch của module loop chạy test, thiếu một fallback write-fail safety. Đồng thời do stdout trên Windows mặc định encode không in được list icon emoji tick `✓` sẽ gây văng.

**Cách sửa:**
- Bổ sung cấu hình reconfigure encoding hệ điều hành ngay phần setup của sys module.
- Ở vòng catch, tôi ép việc khởi tạo một dummy `record` để báo lại `PIPELINE_ERROR` kèm theo message báo lỗi rồi ghi tiếp log thay vì dừng hẳn.

**Bằng chứng trước/sau:**
```python
            # Cách sửa ở eval_trace.py
            except Exception as e:
                # Vẫn cố catch lại trace
                result = {"question_id": q_id}
                ...
                record = {
                    "id": q_id,
                    "answer": f"PIPELINE_ERROR: {e}",
                    "supervisor_route": "error",
                    "route_reason": str(e),
                    "confidence": 0.0,
                    ...
                }
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
```

---

## 4. Tôi tự đánh giá đóng góp của mình

**Tôi làm tốt nhất ở điểm nào?**
Khả năng tổng hợp metric (`analyze_traces()` + `compare_single_vs_multi()`), cung cấp góc nhìn toàn cảnh về project day 09 để tạo Report Nhóm (`group_report.md` đạt hơn 1k từ khá chi tiết và sâu) rất rõ ràng, cụ thể với minh chứng đầy đủ về routing distribution (16/30 retrieval, 14/30 policy).

**Tôi làm chưa tốt hoặc còn yếu ở điểm nào?**
Vì mải lo thiết kế CLI evaluation tools, tôi không có thời gian soi vào file trace thực tế để kịp thắc mắc tại sao avg confidence luôn chỉ bằng `0.10`. Tôi cứ nghĩ là kết quả thực của prompt chứ không nhận ra ChromaDB chưa index đủ ở module `synthesis_worker` (như nhắc dưới Group Report). Nếu tôi cảnh báo anh em sớm hơn, nhóm đã kịp fix ChromaDB.

**Nhóm phụ thuộc vào tôi ở đâu?**
Tính toán metric tự động để so sánh Baseline Day 08 và Multi-Agent day 09, chạy batch sinh Grading output phục vụ nộp bài theo score card vào điểm. 

**Phần tôi phụ thuộc vào thành viên khác:**
Tôi cần supervisor của An và MCP tools của Cường ổn định, pipeline return type của graph.py chuẩn định dạng trả về để tôi bóc log, bắt data (confidence, latency) không bị key errors.

---

## 5. Nếu có thêm 2 giờ, tôi sẽ làm gì?

Tôi sẽ bổ sung module **cảnh báo metric bất thường** (Anomaly Alert) ngay sau hàm test run. Thay vì chờ in thông số "avg_confidence = 0.1", nếu trace trả về `len(retrieved_chunks) == 0` > 3 test case trở lên liên tiếp, tôi sẽ throw WARNING trên CLI báo `"Source data may be missing in Workers"`. Việc này bắt lỗi sớm để team tránh cảnh "pipeline không nổ nhưng đáp án lại trả giá trị mock/fallback do null context".
