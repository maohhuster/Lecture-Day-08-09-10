# 🧪 Hướng Dẫn Chạy Test Questions & Grading Questions

## 1️⃣ Setup Trước Tiên

```bash
# Vào thư mục lab
cd Lecture-Day-08-09-10/day09/lab

# Tạo thư mục artifacts nếu chưa có
mkdir -p artifacts/traces

# Kiểm tra requirements
pip install -r requirements.txt
```

---

## 2️⃣ Chạy Test Questions (15 câu hỏi cơ bản)

### **Cách 1: Chạy tất cả test questions**

```bash
python eval_trace.py
```

**Output:** 
- ✅ Chạy 15 câu hỏi từ `data/test_questions.json`
- 📁 Lưu trace từng câu vào `artifacts/traces/`
- 📊 Hiển thị kết quả trực tiếp trên console

**Ví dụ output:**
```
📋 Running 15 test questions from lab/data/test_questions.json
============================================================
[01/15] q01: SLA xử lý ticket P1 là bao lâu?...
  ✓ route=retrieval_worker, conf=0.92, 1250ms

[02/15] q02: Khách hàng có thể yêu cầu hoàn tiền trong bao nhiêu ngày?...
  ✓ route=retrieval_worker, conf=0.88, 980ms

[03/15] q03: Ai phải phê duyệt để cấp quyền Level 3?...
  ✓ route=policy_tool_worker, conf=0.90, 1100ms

...

✅ Done. 15 / 15 succeeded.
```

---

### **Cách 2: Chạy từng câu hỏi riêng lẻ (debug mode)**

```bash
python -c "
import sys
sys.path.insert(0, '.')
from graph import run_graph
import json

# Mở file test_questions.json
with open('data/test_questions.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

# Chọn câu hỏi (ví dụ câu đầu tiên)
q = questions[0]
print(f\"🔍 Testing: {q['question']}\")
print(f\"📌 Expected answer: {q['expected_answer']}\")

# Chạy qua graph
result = run_graph(q['question'])

print(f\"\n✅ Result:\")
print(f\"   Route: {result.get('supervisor_route', '?')}\")
print(f\"   Answer: {result.get('final_answer', '?')[:150]}...\")
print(f\"   Sources: {result.get('sources', [])}\")
print(f\"   Confidence: {result.get('confidence', 0)}\")
print(f\"   Latency: {result.get('latency_ms', 0)}ms\")
"
```

---

## 3️⃣ Chạy Grading Questions (Câu hỏi chấm điểm)

### ⚠️ Lưu ý:
- Grading questions được **công khai lúc 17:00**
- Bạn chỉ được phép chạy **SAU khi 17:00** (quy định academic integrity)
- Mỗi người chỉ được chạy **1 lần duy nhất**

### **Cách chạy:**

```bash
# Nếu đã qua 17:00
python eval_trace.py --grading
```

**Output:**
- ✅ Chạy các câu hỏi từ `data/grading_questions.json`
- 📁 Lưu log vào `artifacts/grading_run.jsonl` (với timestamp)
- 🔐 Ghi lại thời gian chạy (để chứng minh chạy sau 17:00)

**Ví dụ output:**
```
🎯 Running grading questions (available after 17:00)
============================================================
[01/06] gq01: Ticket P1 được tạo lúc 22:47...
  ✓ route=retrieval_worker, conf=0.95, 1400ms

[02/06] gq02: Khách hàng đặt đơn ngày 31/01/2026...
  ✓ route=retrieval_worker, conf=0.82, 1150ms

...

✅ Done. Grading run saved to: artifacts/grading_run_2026-04-14_1730.jsonl
```

---

## 4️⃣ Xem Chi Tiết Trace từ Từng Câu Hỏi

### **Cách 1: Đọc file trace JSON**

```bash
# Xem danh sách trace đã lưu
ls artifacts/traces/

# Xem chi tiết 1 trace
python -c "
import json
with open('artifacts/traces/test_run_q01_20260414_143211.json') as f:
    trace = json.load(f)

print('=== FULL TRACE ===')
print(json.dumps(trace, indent=2, ensure_ascii=False))
"
```

### **Cách 2: Chạy analyze mode**

```bash
python eval_trace.py --analyze
```

**Output:**
- 📊 Tính toán metrics từ tất cả trace
  - Routing accuracy
  - Average confidence
  - Latency stats
- 📈 Tổng hợp thống kê

---

## 5️⃣ So Sánh Single-Worker vs Multi-Worker (Day 08 vs Day 09)

```bash
python eval_trace.py --compare
```

**Output:**
- 📊 So sánh Day 08 (RAG monolith) vs Day 09 (Supervisor-Worker)
- 📈 Metrics:
  - Accuracy
  - Latency
  - Traceability
  - Error handling

---

## 6️⃣ Xem Kết Quả Chi Tiết Từng Câu

### **Script để in kết quả dạng dễ đọc:**

```bash
python -c "
import json

# Mở file test_questions.json
with open('data/test_questions.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

# Mở file trace gần nhất
import os
from pathlib import Path

traces_dir = Path('artifacts/traces')
if traces_dir.exists():
    traces = sorted(traces_dir.glob('*.json'), key=os.path.getmtime, reverse=True)[:15]
    
    for trace_file in traces:
        with open(trace_file) as f:
            trace = json.load(f)
        
        q_id = trace.get('question_id')
        q = next((q for q in questions if q['id'] == q_id), None)
        
        if q:
            print(f\"\\n{'='*70}\")
            print(f\"📌 {q_id}: {q['question']}\")
            print(f\"{'='*70}\")
            print(f\"✅ Expected: {q['expected_answer']}\")
            print(f\"\\n💬 Got: {trace.get('final_answer', 'N/A')}\")
            print(f\"\\n📊 Stats:\")
            print(f\"   Route: {trace.get('supervisor_route', 'N/A')}\")
            print(f\"   Sources: {trace.get('retrieved_sources', [])}\")
            print(f\"   Confidence: {trace.get('confidence', 0):.2f}\")
            print(f\"   Latency: {trace.get('latency_ms', 0)}ms\")
else:
    print('⚠️  No traces found. Run: python eval_trace.py')
"
```

---

## 7️⃣ Chạy Full Workflow (Tất Cả Lúc Một)

```bash
# Step 1: Chạy 15 test questions
python eval_trace.py

# Step 2: Phân tích kết quả
python eval_trace.py --analyze

# Step 3: (Sau 17:00) Chạy grading questions
# python eval_trace.py --grading

# Step 4: Chạy so sánh với Day 08
python eval_trace.py --compare

# Step 5: Xem báo cáo tổng kết
python -c "
import json
with open('artifacts/eval_report.json') as f:
    report = json.load(f)
print(json.dumps(report, indent=2, ensure_ascii=False))
"
```

---

## 8️⃣ Troubleshooting

### **Error: "graph module not found"**
```bash
# Đảm bảo bạn ở thư mục lab
cd Lecture-Day-08-09-10/day09/lab
python eval_trace.py
```

### **Error: "data/test_questions.json not found"**
```bash
# Kiểm tra file tồn tại
ls data/test_questions.json
ls data/grading_questions.json
```

### **Error: "import chromadb failed"**
```bash
# Cài đặt dependencies
pip install chromadb sentence-transformers openai
```

### **Chạy quá lâu?**
```bash
# Chạy chỉ 3 câu đầu để test nhanh
python -c "
import sys
sys.path.insert(0, '.')
from eval_trace import run_test_questions
import json

with open('data/test_questions.json') as f:
    questions = json.load(f)[:3]  # Chỉ 3 câu

for q in questions:
    from graph import run_graph
    result = run_graph(q['question'])
    print(f\"✓ {q['id']}: {result.get('confidence', 0):.2f}\")
"
```

---

## 9️⃣ Lưu Ý Quan Trọng

| What | Command | When |
|------|---------|------|
| **Test Questions** | `python eval_trace.py` | Bất kỳ lúc nào |
| **Analyze Results** | `python eval_trace.py --analyze` | Sau khi chạy test |
| **Grading Questions** | `python eval_trace.py --grading` | **CHỈ AFTER 17:00** |
| **Compare with Day 08** | `python eval_trace.py --compare` | Sau khi có traces |

---

## 🎯 Expected Results

Khi chạy thành công, bạn sẽ thấy:
- ✅ 15/15 test questions pass
- 📊 Confidence scores: 0.75 - 0.95
- ⏱️ Latency: 800ms - 2000ms per question
- 🗂️ Traces lưu trong `artifacts/traces/`

Hãy chạy và kiểm tra kết quả! 🚀
