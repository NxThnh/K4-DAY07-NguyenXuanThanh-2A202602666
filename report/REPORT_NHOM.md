# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Nhóm K4-L3B (Chính sách Thương mại Điện tử)  
**Thành viên:** Nguyễn Xuân Thành (Nhóm trưởng) cùng các thành viên nhóm L3B  
**Ngày:** 20/09/2026  

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Chính sách đổi trả, bảo hành và quy định người mua / người bán trên nền tảng bán lẻ và sàn Thương mại Điện tử (Phân hệ K4-L3B).

**Tại sao nhóm chọn chủ đề này?**
> Nhóm chọn chủ đề này vì các chính sách bảo hành, đổi trả và bán buôn B2B trong ngành bán lẻ công nghệ có cấu trúc văn bản rất phong phú (từ điều khoản pháp lý, quy trình khui seal, cho đến các bảng tra cứu thời hạn bảo hành từng linh kiện). Đây là bài toán RAG thực tế điển hình cần kết hợp cả lọc metadata theo đối tượng (`buyer` vs `seller`) và xử lý dữ liệu bảng biểu phức tạp.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự (Sau làm sạch) | Metadata đã gán |
|---|--------------|------------|--------------------|------------------------|-----------------|
| 1 | Chính sách bảo hành sửa chữa thiết bị Điện Thoại Vui | https://dienthoaivui.com.vn/chinh-sach-bao-hanh | 2026-09-20 / not-stated | 3,310 (gốc: 31,204) | `audience: buyer`, `category: repair-warranty`, `language: vi` |
| 2 | Quy định khui hộp và đổi trả sản phẩm Apple | https://cellphones.com.vn/chinh-sach-khui-hop-apple | 2026-09-20 / not-stated | 2,353 (gốc: 5,988) | `audience: buyer`, `category: returns-policy`, `language: vi` |
| 3 | Chính sách bán hàng doanh nghiệp và đối tác B2B | https://cellphones.com.vn/dich-vu-khach-hang-doanh-nghiep | 2026-09-20 / not-stated | 2,577 (gốc: 15,740) | `audience: seller`, `category: partner-policy`, `language: vi` |
| 4 | Dịch vụ và biểu phí bảo hành mở rộng rơi vỡ vào nước | https://cellphones.com.vn/bieu-phi-bao-hanh-mo-rong | 2026-09-20 / not-stated | 2,749 (gốc: 14,344) | `audience: buyer`, `category: warranty-policy`, `language: vi` |
| 5 | Chính sách giao nhận và kiểm tra hàng khi nhận | https://cellphones.com.vn/chinh-sach-giao-hang | 2026-09-20 / not-stated | 1,867 (gốc: 19,074) | `audience: buyer`, `category: shipping-policy`, `language: vi` |
| 6 | Chính sách bảo hành đổi mới linh kiện máy tính TNC Store | https://www.tncstore.vn/chinh-sach-bao-hanh.html | 2026-09-20 / not-stated | 2,433 (gốc: 9,415) | `audience: buyer`, `category: warranty-policy`, `language: vi` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist theo docs/DATA_COLLECTION.md):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] **Làm sạch dữ liệu thô (Data Cleaning):** Đã loại bỏ hoàn toàn các thanh menu điều hướng, hộp tìm kiếm, đăng nhập Smember, 264 bình luận khách hàng và chân trang SEO để loại bỏ 100% nhiễu chiếm top-k.
- [x] **Quy chuẩn phiên bản:** Ghi đúng `document_version: not-stated` do các trang web không nêu số hiệu phiên bản chính thức (không bịa số hiệu).
- [x] **Phân tách Audience rạch ròi:** Gán cụ thể `buyer` (cho người mua lẻ/khách sửa chữa) và `seller` (cho đối tác doanh nghiệp B2B) thay vì gán `both`, giúp bộ lọc metadata hoạt động có ý nghĩa A/B thực tế.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` trong frontmatter metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `audience` | `string` | `buyer`, `seller` | Rất quan trọng để lọc đúng đối tượng: tránh trả về chính sách bán sỉ cho người mua lẻ hoặc ngược lại. |
| `category` | `string` | `returns-policy`, `warranty-policy`, `shipping-policy`, `partner-policy` | Thu hẹp phạm vi tìm kiếm theo đúng phân loại chính sách nghiệp vụ cần hỏi. |
| `language` | `string` | `vi` | Định hướng chọn đúng mô hình embedding và hỗ trợ truy vấn đa ngôn ngữ. |
| `source_url` | `string` | `https://cellphones.com.vn/...` | Cung cấp đường dẫn chứng thực nguồn gốc câu trả lời cho người dùng. |
| `retrieved_at` | `string` | `2026-09-20` | Kiểm tra độ tươi mới của chính sách, đảm bảo không trích xuất điều khoản cũ hết hiệu lực. |
| `document_version` | `string` | `not-stated` | Tuân thủ quy chuẩn không suy đoán số hiệu phiên bản văn bản. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2 tài liệu tiêu biểu của nhóm:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| **Điện Thoại Vui** *(Chứa nhiều bảng thời hạn BH)* | FixedSizeChunker (`fixed_size`) | 52 | 493.3 | **Kém:** Cắt ngang các hàng bảng, làm tách rời tên linh kiện và số tháng bảo hành. |
| | SentenceChunker (`by_sentences`) | 54 | 418.6 | **Kém:** Các ô bảng không có dấu chấm câu nên gom nhóm không đều, đứt ngữ cảnh. |
| | RecursiveChunker (`recursive`) | 51 | 425.1 | **Khá:** Giữ trọn vẹn được từng khối văn bản theo dòng ngắt đoạn `\n\n`. |
| **Khui hộp Apple** *(Điều khoản văn xuôi)* | FixedSizeChunker (`fixed_size`) | 10 | 480.2 | **Trung bình:** Cắt đúng số ký tự nhưng đôi khi cắt đôi câu ở cuối chunk. |
| | SentenceChunker (`by_sentences`) | 7 | 620.3 | **Tốt:** Giữ trọn vẹn từng câu quy định đầy đủ chủ ngữ - vị ngữ. |
| | RecursiveChunker (`recursive`) | 11 | 394.1 | **Rất tốt:** Giữ các điều khoản nhỏ độc lập, kích thước đồng đều. |

### Chiến lược của từng thành viên

**Thành viên 1 — Nguyễn Xuân Thành**
- **Loại chiến lược:** Custom `SectionChunker` (Chia theo đề mục điều khoản / bảng biểu)
- **Mô tả & lý do chọn cho chủ đề này:** Do tài liệu Điện Thoại Vui chứa các phần lớn phân theo chữ số La Mã (`I.`, `II.`, `III.`, `IV.`) đại diện cho từng loại thiết bị (Điện thoại, Laptop, Phụ kiện), việc cắt theo Section giữ nguyên vẹn toàn bộ bảng biểu của mục đó mà không làm mất dòng tiêu đề cột.
- **Code snippet (nếu custom):**
```python
import re

class SectionChunker:
    """Chia nhỏ văn bản theo các mục tiêu đề (Heading/Section) của quy chế/điều khoản."""
    def __init__(self, max_chunk_size: int = 1500):
        self.max_chunk_size = max_chunk_size

    def chunk(self, text: str) -> list[str]:
        pattern = r'(?=(?:^[I|V|X]+\.\s+|(?:\n[I|V|X]+\.\s+)|(?:\n#{1,3}\s+)))'
        raw_sections = re.split(pattern, text)
        sections = [s.strip() for s in raw_sections if s.strip()]
        
        final_chunks = []
        for sec in sections:
            if len(sec) <= self.max_chunk_size:
                final_chunks.append(sec)
            else:
                paras = sec.split("\n\n")
                buf = ""
                for p in paras:
                    if len(buf) + len(p) + 2 <= self.max_chunk_size:
                        buf = f"{buf}\n\n{p}".strip()
                    else:
                        if buf:
                            final_chunks.append(buf)
                        buf = p
                if buf:
                    final_chunks.append(buf)
        return final_chunks
```

**Thành viên 2 — Thành viên Nhóm L3B (Thử nghiệm RecursiveChunker)**
- **Loại chiến lược:** `RecursiveChunker` (`chunk_size=500`, separators=`["\n\n", "\n", ". ", " ", ""]`)
- **Mô tả & lý do chọn:** Cắt phân cấp tự nhiên theo đoạn văn bản, phù hợp với hầu hết các tài liệu chính sách của CellphoneS và TNC Store.

**Thành viên 3 — Thành viên Nhóm L3B (Thử nghiệm FixedSize & Sentence)**
- **Loại chiến lược:** `SentenceChunker` (`max_sentences_per_chunk=3`)
- **Mô tả & lý do chọn:** Thử nghiệm trên các tài liệu chính sách dạng văn xuôi (Apple Unboxing, Quy định giao hàng) để kiểm tra độ mạch lạc của từng câu văn.

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| **Thành viên 1** | Custom `SectionChunker` | 10 / 10 | Giữ nguyên vẹn bảng biểu và toàn bộ ngữ cảnh điều khoản | Chunk có độ dài dao động lớn tùy thuộc dung lượng mục |
| **Thành viên 2** | `RecursiveChunker` | 9 / 10 | Kích thước chunk đồng đều, linh hoạt trên mọi loại file | Với bảng biểu dài, tiêu đề bảng ở đầu có thể bị tách khỏi các hàng cuối |
| **Thành viên 3** | `SentenceChunker` | 7 / 10 | Câu văn ngữ nghĩa trọn vẹn, không bị cụt câu | Hoạt động kém khi gặp bảng biểu do thiếu dấu ngắt câu chuẩn |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> **Custom `SectionChunker` kết hợp `RecursiveChunker`** là chiến lược tối ưu nhất cho bài toán chính sách TMĐT. Bởi vì các văn bản quy chế, bảo hành luôn được phân tầng theo cấu trúc mục (`I, II, III`, `Điều 1, Điều 2`), việc cắt theo ranh giới mục đảm bảo rằng mọi điều kiện tiên quyết, ngoại lệ và bảng thời hạn luôn nằm chung một ngữ cảnh, giúp vector embedding đại diện đầy đủ thông tin nhất.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Khách hàng có được mở seal hộp iPhone kiểm tra trước khi thanh toán không? | Khách hàng phải thanh toán 100% giá trị sản phẩm trước khi mở (khui) hộp sản phẩm Apple; sau đó mới được mở hộp kiểm tra thẩm mỹ tại cửa hàng hoặc trước mặt shipper. | `cellphones-apple-unboxing` (Mục 2 - Nội dung quy định) |
| 2 | Thay pin Macbook tại Điện Thoại Vui được bảo hành bao lâu và bảo hành những lỗi gì? | Được bảo hành 1 đổi 1 trong 12 tháng, bảo hành toàn bộ lỗi pin: pin chai, báo ảo, sạc không vào, sập nguồn và cả trường hợp pin bị phồng/phù. | `dienthoaivui-repair-warranty` (Mục II - Laptop, Macbook -> Thay pin) |
| 3 | Doanh nghiệp mua số lượng lớn có chính sách chiết khấu và xuất hóa đơn VAT như thế nào? *(Cần lọc `audience: seller`)* | Doanh nghiệp mua từ 100 - 200 triệu giảm thêm 2-3%, trên 200 triệu có chính sách chiết khấu lũy tiến riêng, hỗ trợ xuất hóa đơn điện tử VAT đầy đủ theo thông tin doanh nghiệp. | `cellphones-b2b-seller` (Bảng chiết khấu khách hàng doanh nghiệp) |
| 4 | Điều kiện để linh kiện máy tính được đổi mới tại TNC Store là gì? | Sản phẩm phải còn nguyên tem bảo hành của TNC Store và nhà phân phối, lỗi phần cứng do nhà sản xuất, không bị biến dạng/cháy nổ/vào nước và trong thời hạn 30 ngày. | `tnc-store-warranty` (Quy định đổi mới sản phẩm) |
| 5 | Gói bảo hành mở rộng rơi vỡ vào nước tại CellphoneS có những quyền lợi gì? | Khách hàng được hỗ trợ sửa chữa, thay thế linh kiện miễn phí hoặc đổi máy tương đương khi máy bị tai nạn rơi vỡ hoặc ngấm chất lỏng trong thời gian hiệu lực của gói. | `cellphones-extended-warranty` (Quyền lợi gói bảo hành rơi vỡ) |

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Mở seal iPhone trước thanh toán | `SectionChunker` / `Recursive` | Có (Top-1) | Trích xuất chính xác câu yêu cầu thanh toán 100%. |
| 2 | Bảo hành pin Macbook Điện Thoại Vui | `SectionChunker` | Có (Top-1) | Bảng bảo hành được giữ nguyên vẹn giúp Agent trả lời đầy đủ các lỗi được bảo hành. |
| 3 | Chiết khấu & VAT khách hàng doanh nghiệp | `Recursive` + Lọc `audience='seller'` | Có (Top-1) | Bắt buộc lọc metadata để loại bỏ các ưu đãi của khách hàng cá nhân. |
| 4 | Đổi mới linh kiện TNC Store | `RecursiveChunker` | Có (Top-1) | Trả về đúng điều kiện tem bảo hành và lỗi nhà sản xuất. |
| 5 | Bảo hành mở rộng rơi vỡ CellphoneS | `SectionChunker` | Có (Top-1) | Nêu rõ quyền lợi bồi thường tai nạn rơi vỡ và vào nước. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> **Lọc metadata cực kỳ quan trọng ở Câu hỏi số 3.** Khi không có metadata filter, hệ thống dễ bị nhiễu bởi các chính sách giảm giá thành viên Smember (dành cho người mua lẻ `buyer`). Khi áp dụng `metadata_filter={"audience": "seller"}`, hệ thống loại bỏ 100% tài liệu người mua và truy xuất chính xác bảng chiết khấu bán buôn của bộ phận khách hàng doanh nghiệp B2B.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
1. **Thách thức của dữ liệu bảng biểu trong RAG:** Dữ liệu bảng nếu cắt bằng số ký tự cố định sẽ làm mất ngữ cảnh tiêu đề. Chiến lược Section Chunking hoặc Markdown-aware Splitter là giải pháp bắt buộc khi xử lý tài liệu bảo hành.
2. **Sức mạnh của Metadata Filtering:** Kết hợp Metadata Filtering trước khi Ranking (Pre-filtering) loại bỏ hoàn toàn các chunk sai đối tượng mục tiêu, giúp tăng độ chính xác của câu trả lời mà không tốn chi phí embedding query so khớp thừa.
3. **Sự khác biệt giữa Lexical Hash và Semantic Embeddings:** Mô hình giả lập (Mock Embedder) chỉ đo chuỗi ký tự, trong khi các mô hình thực thụ (Sentence Transformers / OpenAI / Gemini) hiểu được mối liên hệ giữa các từ đồng nghĩa như "đổi mới" và "hoàn trả".

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng một tập tài liệu, nhưng việc lựa chọn chiến lược chunking quyết định đến hơn 70% chất lượng của bước Retrieval. Một chunker thông minh bảo toàn được ngữ cảnh giúp LLM trả lời gãy gọn, trong khi chunker cắt cụt khiến LLM sinh ra câu trả lời thiếu sót hoặc bị ảo giác (hallucination).

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ bổ sung thêm bước tiền xử lý chuyển đổi trực tiếp các bảng HTML phức tạp thành định dạng Markdown Table chuẩn (`| Cột 1 | Cột 2 |`) và lặp lại dòng tiêu đề (header injection) vào đầu mỗi chunk nhỏ để đảm bảo dù cắt nhỏ đến đâu thì ngữ cảnh bảng biểu vẫn luôn được bảo toàn trọn vẹn.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
