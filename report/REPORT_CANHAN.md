# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Xuân Thành  
**Nhóm:** LaoGaKho
**Mã Sinh Viên:** 2A202602666  
**Ngày:** 20/09/2026  

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao (tiến gần đến 1.0) thể hiện hai vector embedding cùng chỉ về một hướng trong không gian đa chiều, phản ánh hai đoạn văn bản có mức độ tương đồng rất lớn về mặt ngữ nghĩa hoặc chủ đề, bất kể số lượng từ và độ dài giữa chúng.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Chính sách đổi trả sản phẩm áp dụng trong vòng 30 ngày kể từ khi mua."
- Câu B: "Khách hàng có quyền yêu cầu hoàn trả hoặc đổi mới hàng hóa trong thời hạn một tháng."
- Tại sao tương đồng: Cả hai câu đều truyền tải cùng một chính sách kinh doanh về quyền và thời hạn đổi trả hàng (30 ngày tương đương một tháng), dùng các từ ngữ đồng nghĩa ("đổi trả" - "hoàn trả hoặc đổi mới", "khi mua" - "kể từ ngày mua").

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Khách hàng cần thanh toán 100% giá trị máy trước khi khui hộp kiểm tra."
- Câu B: "Hướng dẫn cài đặt hệ điều hành Linux trên máy tính cá nhân."
- Tại sao khác: Hai câu thuộc hai lĩnh vực hoàn toàn tách biệt: Câu A là quy định nghiệp vụ bán hàng / khui hộp công nghệ, còn Câu B là hướng dẫn kỹ thuật công nghệ thông tin phần mềm.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Khoảng cách Euclid bị phụ thuộc mạnh vào độ dài vector (văn bản dài chứa nhiều từ sẽ có vector độ lớn lớn hơn văn bản ngắn dù cùng ý nghĩa). Ngược lại, Cosine similarity chuẩn hóa độ dài về đường tròn đơn vị và chỉ đo góc hợp giữa hai vector, giúp phản ánh chính xác sự tương đồng ngữ nghĩa mà không bị thiên vị bởi độ dài văn bản.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> - Bước nhảy giữa các chunk (step): $\text{step} = \text{chunk\_size} - \text{overlap} = 500 - 50 = 450$ ký tự.
> - Số lượng chunk: $\lceil \frac{10000 - 50}{450} \rceil = \lceil \frac{9950}{450} \rceil = \lceil 22.11 \rceil = 23$ chunks.  
> *(Các điểm bắt đầu chunk: 0, 450, 900, ..., 9900 tương ứng 23 chunks)*
> *Đáp án:* **23 chunks**.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap tăng lên 100, bước nhảy giảm còn $500 - 100 = 400$ ký tự. Số lượng chunk tăng lên $\lceil \frac{9900}{400} \rceil = 25$ chunks (tăng thêm 2 chunks). Tăng độ chồng chéo giúp hạn chế tình trạng mất ngữ cảnh tại điểm cắt ranh giới, đảm bảo các câu, cụm điều khoản hoặc thông tin then chốt không bị đứt đoạn giữa hai chunk kế tiếp.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi sử dụng biểu thức chính quy `(?<=[.!?])\s+` để tách câu dựa trên các dấu kết thúc câu (`.`, `!`, `?` hoặc `.\n`) theo sau bởi khoảng trắng. Xử lý các edge case như chuỗi rỗng/chỉ chứa khoảng trắng (trả về `[]`), văn bản không chứa dấu ngắt câu (giữ nguyên toàn bộ làm một câu), và gom nhóm các câu đã được làm sạch theo từng cụm `max_sentences_per_chunk`.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán hoạt động theo nguyên tắc chia nhỏ có phân cấp với danh sách dấu phân cách ưu tiên `["\n\n", "\n", ". ", " ", ""]`. Base case là khi đoạn văn bản có độ dài $\le$ `chunk_size` hoặc đã hết danh sách phân tách thì trả về ngay. Thuật toán tìm separator phù hợp đầu tiên, tách chuỗi, đệ quy xử lý các đoạn còn quá dài, và gom các đoạn hợp lệ liền kề sao cho tổng độ dài đạt tối đa trong giới hạn `chunk_size`.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Dữ liệu được lưu trữ in-memory dưới dạng danh sách `dict` chứa `id`, `content`, `metadata` và vector nhúng `embedding` (chuẩn bị sẵn hook tích hợp ChromaDB nếu thư viện có sẵn). Khi tìm kiếm `search`, query được nhúng thành vector, sau đó tính toán cosine similarity (`compute_similarity`) với từng bản ghi trong store, sắp xếp giảm dần theo điểm tương đồng và trả về top-k.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Với `search_with_filter`, tôi áp dụng chiến lược pre-filtering (lọc trước): duyệt qua toàn bộ kho để giữ lại các bản ghi thỏa mãn tất cả cặp key-value trong `metadata_filter`, rồi mới tính điểm similarity trên tập đã lọc. Với `delete_document`, tôi lọc loại bỏ các bản ghi có `id == doc_id` hoặc `metadata['doc_id'] == doc_id`, so sánh độ dài kho trước và sau thao tác để trả về `True` (nếu đã xóa) hoặc `False`.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Hàm `answer` thực hiện quy trình RAG chuẩn 3 bước: đầu tiên gọi `self.store.search(question, top_k=top_k)` để trích xuất các đoạn văn bản phù hợp nhất; tiếp theo gom các đoạn content thành khối ngữ cảnh `Context:\n...`; cuối cùng định dạng prompt kèm theo câu hỏi `Question: ...` và chuyển cho mô hình ngôn ngữ `llm_fn` để sinh câu trả lời dựa trên ngữ cảnh đã cung cấp.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```text
tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.08s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán (Ngữ nghĩa) | Điểm thực tế (Mock / Semantic) | Phân tích |
|:---:|:---|:---|:---:|:---:|:---|
| 1 | "Thời hạn bảo hành đổi mới sản phẩm là 30 ngày." | "Chính sách đổi trả trong vòng một tháng kể từ ngày mua." | Cao (đồng nghĩa) | -0.186 (Mock) / 0.892 (Semantic) | Ngữ nghĩa tương đương nhau, nhưng Mock Embedder băm MD5 chuỗi ký tự nên điểm thấp |
| 2 | "Khách hàng cần thanh toán 100% trước khi khui hộp iPhone." | "Mở seal và kích hoạt máy Apple yêu cầu thanh toán trước." | Cao (cùng chủ đề) | -0.120 (Mock) / 0.841 (Semantic) | Cùng mô tả quy định bóc seal điện thoại Apple |
| 3 | "Thay pin Macbook được bảo hành 12 tháng tại cửa hàng." | "Màn hình laptop Dell bị nứt vỡ do rơi rớt không được bảo hành." | Trung bình / Thấp | -0.065 (Mock) / 0.432 (Semantic) | Cùng về bảo hành máy tính nhưng dịch vụ và thương hiệu khác nhau |
| 4 | "Chính sách ưu đãi chiết khấu dành cho khách hàng doanh nghiệp mua sỉ." | "Quy trình đổi trả hàng bị lỗi kỹ thuật cho người tiêu dùng cá nhân." | Thấp (khác đối tượng) | -0.127 (Mock) / 0.285 (Semantic) | Một bên là đối tượng người bán/B2B, một bên là người mua cá nhân |
| 5 | "Hướng dẫn cài đặt hệ điều hành Linux trên máy tính cá nhân." | "Chính sách đổi trả hàng và hoàn tiền trên sàn thương mại điện tử." | Rất thấp (hoàn toàn khác) | -0.025 (Mock) / 0.091 (Semantic) | Hai chủ đề hoàn toàn không liên quan |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Điểm số từ `MockEmbedder` cho thấy dù hai câu có ngữ nghĩa tương đồng cao, điểm cosine similarity vẫn có thể mang giá trị âm hoặc gần 0 vì mock embedder chỉ băm MD5 chuỗi ký tự (lexical hash) thay vì phân tích ngữ nghĩa (semantic representation). Điều này làm nổi bật tầm quan trọng cốt lõi của các mô hình nhúng thực thụ (như multilingual Sentence Transformers hay OpenAI/Gemini Embeddings), vốn học được mối quan hệ từ vựng trong không gian vector dày đặc (dense vector space).

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score (Semantic) | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Khách hàng có được mở seal hộp iPhone kiểm tra trước khi thanh toán không? | Quy định khui hộp CellphoneS: Khách hàng phải thanh toán 100% giá trị sản phẩm trước khi mở (khui) hộp sản phẩm Apple. | 0.865 | Có (Chính xác 100%) | Khách hàng bắt buộc phải thanh toán 100% trước khi khui seal sản phẩm Apple; chỉ mở hộp kiểm tra sau khi đã thanh toán. |
| 2 | Thay pin Macbook tại Điện Thoại Vui được bảo hành bao lâu và bảo hành những lỗi gì? | Chính sách Điện Thoại Vui: Thay pin Macbook GENA bảo hành 1 đổi 1 trong 12 tháng, bảo hành lỗi pin chai, báo ảo, sạc không vào, sập nguồn và cả pin phồng. | 0.871 | Có (Chính xác 100%) | Được bảo hành 1 đổi 1 trong 12 tháng cho các lỗi pin chai, sạc không vào, sập nguồn và phồng pin. |
| 3 | Doanh nghiệp mua số lượng lớn có chính sách chiết khấu và xuất hóa đơn VAT như thế nào? *(Filter: audience='seller')* | Chính sách B2B CellphoneS: Mua từ 100-200 triệu giảm thêm 2-3%, trên 200 triệu đàm phán riêng, hỗ trợ xuất 100% hóa đơn điện tử VAT. | 0.736 | Có (Nhờ lọc metadata) | Doanh nghiệp mua sỉ được áp dụng chiết khấu theo bậc giá trị và được xuất hóa đơn VAT điện tử. |
| 4 | Điều kiện để linh kiện máy tính được đổi mới tại TNC Store là gì? | Chính sách TNC Store: CPU/RAM/SSD đổi mới 100% trong 3 năm; Nguồn/Tản nhiệt 1 năm; Main/VGA 6 tháng; tem còn nguyên, không biến dạng/cháy nổ. | 0.881 | Có (Chính xác 100%) | Sản phẩm phải còn nguyên tem bảo hành, lỗi phần cứng do nhà sản xuất và nằm trong thời hạn quy định. |
| 5 | Gói bảo hành mở rộng rơi vỡ vào nước tại CellphoneS có những quyền lợi gì? | Dịch vụ bảo hành mở rộng CellphoneS: Tặng bảo hành 1-1 VIP, hỗ trợ 90% chi phí sửa chữa rơi vỡ vào nước, đổi máy tương đương nếu không sửa được. | 0.890 | Có (Chính xác 100%) | Được hỗ trợ 90% chi phí sửa chữa khi rơi vỡ hoặc vào nước, hoặc đổi máy tương đương với 10% phí dịch vụ. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5 (Đạt 100% Top-1 chính xác tuyệt đối)

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Tôi học được rằng đối với các tài liệu có cấu trúc bảng biểu hoặc điều khoản dài, chiến lược `RecursiveChunker` hoặc `SectionChunker` vượt trội hơn hẳn `SentenceChunker` vì nó bảo toàn được toàn bộ ngữ cảnh của đề mục và các dòng tiêu đề quan trọng, giúp điểm số truy xuất top-1 chính xác vượt bậc.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
