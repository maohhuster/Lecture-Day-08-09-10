# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Nguyễn Ngọc Cường  
**Vai trò trong nhóm:** Baseline Retrieval + Answer  
**Ngày nộp:** 13/4/2026 
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

> Mô tả cụ thể phần bạn đóng góp vào pipeline:
> - Sprint nào bạn chủ yếu làm?
> - Cụ thể bạn implement hoặc quyết định điều gì?
> - Công việc của bạn kết nối với phần của người khác như thế nào?

Tôi đã chủ yếu làm Sprint 2 trong bài tập lab nhóm này là Baseline Retrieval + Answer. Tôi đã retrieve_dense() — query ChromaDB với embedding , sau đó tinh chỉnh lại hàm call_llm() — gọi OpenAI hoặc Gemini để có thể sử dụng được cả 2 Model trên bằng if-else. TÔi cũng đã tinh chỉnh build_context_block để prompt trả về câu trả lời theo 4 quy tắc Evidence-only, Abstain, Citation và Short, clear, stable. TUy vậy cả nhóm đã kiểm tra và thống nhất lựa chọn prompt đơn giản hơn cảu tôi làm

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

> Chọn 1-2 concept từ bài học mà bạn thực sự hiểu rõ hơn sau khi làm lab.
> Ví dụ: chunking, hybrid retrieval, grounded prompt, evaluation loop.
> Giải thích bằng ngôn ngữ của bạn — không copy từ slide.

chunking là thứ tôi cần học, bởi vì với tập dât khác nhau, việc chunking sẽ cần 1 chiến thuật khác nhau.
Evaluation Loop mình quan sát các bạn cùng nhóm và họ dùng LLM như GPT, Gemini bản cao hơn để tạo ra các metric, rồi check lại để có hiểu đúng ý với mục đích ban đầu, baseline chấm không
Việc truy vấn ranking top-k sẽ cần khaongr top 3 đến top 5, top 6 để không bị quá ít để bị overfitting ,hay quá nhiều như top 30 để dữ liệu không bị nhiễu bởi các thông tin không liên quan.
---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

> Điều gì xảy ra không đúng kỳ vọng?
> Lỗi nào mất nhiều thời gian debug nhất?
> Giả thuyết ban đầu của bạn là gì và thực tế ra sao?

Tôi đã cố gắng sử dụng Open AI key và Gemini key để chạy, tuy vậy đều không sử dụng được do chi phí của tôi không cho phép và đã đạt giới hạn prompt của gói free quá nhanh. Lỗi mất nhiều thời gian debug nhất là truy tìm LLM để Rerank với test rag_answer mãu 3 câu thì đều có score rất thấp ở 1 số câu hỏi, thậm chí dười 0.5 ở câu "SLA xử lý ticket P1 là bao lâu?".
GIả thiết ban đầu của mình là những câu hỏi mà có thể trả lợi dược trực tiếp trong file tài liệu, data mà caau hỏi không quá lắt léo thì có thể tìm ngay và có score cao. THực tế thì thời gian tìm kiếm là lâu hơn mình dự kiến khoảng 2 - 3 lần, score thì khá thấp khoảng 0.35

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

> Chọn 1 câu hỏi trong test_questions.json mà nhóm bạn thấy thú vị.
> Phân tích:
> - Baseline trả lời đúng hay sai? Điểm như thế nào?
> - Lỗi nằm ở đâu: indexing / retrieval / generation?
> - Variant có cải thiện không? Tại sao có/không?

**Câu hỏi:** ERR-403-AUTH là lỗi gì và cách xử lý? : q09

**Phân tích:**
Baseline trả lời đúng : Câu tả lời của Baseline và đáp án thực tế là Tôi không biết. ĐIểm top 3 lần lượt là 0.371, 0.349 và 0.345
Câu hỏi này thú vị vì kiểm tra cách prompt với trường hợp không cung cấp đủ thông tin hoặc thông tin không liên quan. Prompt có giới hạn LLM các trường hợp này có khiến LLM trả lời tôi không biết, hay là bịa ra các cau trả lời sai.
Điều thú vị nữa là quan trọng nhất nhưng dễ mắc phải nhất là AI?LLM dễ bị hiện tương ảo giác, tự bịa ra câu trả lời trông có vẻ hợp lý nhưng sai hoàn toàn, nó nguy hiểm khi người dùng không thể kiểm chứng 100% là chính xác không
Variant không cải thiện lắm bởi vì prompt đã khiến cho LLM giới hạn những câu trả lời không thuộc trong tệp data và câu hỏi mà thiếu thông tin đó. Lý do nữa là việc ngăn chặn các LLM bịa ra các câu trả lời với câu hỏi thiếu dữ kiện, không thuộc thông tin trong nguồn data cung cấp có thẻ tác động bằng prompt
_

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

> 1-2 cải tiến cụ thể bạn muốn thử.
> Không phải "làm tốt hơn chung chung" mà phải là:
> "Tôi sẽ thử X vì kết quả eval cho thấy Y."

Tôi sẽ cải tiến bằng cách áp dụng thêm LLM có thể dùng local khác như phi3 thay vì sử dụng Gemini, OpanAI có rủi ro là không phải ai cũng có API key trả phí để phục vụ cho bài tập này
Tôi sẽ thử thêm RETRIEVAL — DENSE (Vector Search) kết hợp với MMR. Lý do là trong các lần chạy test, các kết quả của top 3 có vẻ khá giống nhua 80 đến 90%, thiếu đi độ bao quát toàn diện

---Note: Phan mình lam va dong gop o tren nhanh Cuong

*Lưu file này với tên: `reports/individual/[ten_ban].md`*
*Ví dụ: `reports/individual/nguyen_van_a.md`*
