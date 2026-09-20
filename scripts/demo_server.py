"""
Lab 07 — Demo Presentation Server
Chạy máy chủ web đa luồng phục vụ giao diện thuyết trình của sinh viên Nguyễn Xuân Thành:
- Phục vụ file tĩnh (HTML, CSS, JS) trong thư mục web/
- API RAG thời gian thực với Google Gemini và Vector Store
- API trực quan hóa và so sánh 4 chiến lược chunking
- API minh chứng lọc Metadata
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any

# Reconfigure stdout for Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from dotenv import load_dotenv
load_dotenv(BASE_DIR / ".env")

from src import (
    Document,
    FixedSizeChunker,
    SentenceChunker,
    RecursiveChunker,
    EmbeddingStore,
)
from scripts.bench import (
    load_and_chunk_corpus,
    make_embedder_fn,
    make_llm_fn,
)


class SectionChunker:
    """Chia nhỏ văn bản theo các mục tiêu đề (Heading/Section) của quy chế/điều khoản."""

    def __init__(self, max_chunk_size: int = 1200):
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

# Global instances
CHUNKS: list[Document] = []
STORE: EmbeddingStore | None = None
EMBED_DESC = ""
LLM_FN = None
LLM_DESC = ""


def init_rag_system():
    global CHUNKS, STORE, EMBED_DESC, LLM_FN, LLM_DESC
    print("[*] Đang khởi tạo hệ thống RAG và Vector Store cho Demo Web...")
    data_dir = BASE_DIR / "data" / "ecommerce"
    CHUNKS = load_and_chunk_corpus(data_dir, chunk_size=1200)

    embed_fn, EMBED_DESC = make_embedder_fn(CHUNKS)
    LLM_FN, LLM_DESC = make_llm_fn()

    STORE = EmbeddingStore(collection_name="demo_ecommerce", embedding_fn=embed_fn)
    STORE.add_documents(CHUNKS)
    print(f"[+] Hệ thống RAG đã sẵn sàng ({len(CHUNKS)} clean chunks | {EMBED_DESC})")


class DemoRequestHandler(SimpleHTTPRequestHandler):
    """Xử lý HTTP requests cho file tĩnh và các REST API."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR / "web"), **kwargs)

    def do_GET(self):
        if self.path == "/api/inventory":
            self.handle_get_inventory()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/chat":
            self.handle_post_chat()
        elif self.path == "/api/compare-ab":
            self.handle_post_compare_ab()
        elif self.path == "/api/compare-chunking":
            self.handle_post_compare_chunking()
        else:
            self.send_error(404, "Endpoint not found")

    def handle_get_inventory(self):
        """Trả về thống kê và số liệu làm sạch của kho tài liệu."""
        data_dir = BASE_DIR / "data" / "ecommerce"
        inventory = [
            {
                "doc_id": "dienthoaivui-repair-warranty",
                "title": "Chính sách bảo hành sửa chữa thiết bị Điện Thoại Vui",
                "audience": "buyer",
                "category": "repair-warranty",
                "raw_chars": 31204,
                "clean_chars": 3310,
                "reduction_percent": 89.4,
                "document_version": "not-stated",
                "source_url": "https://dienthoaivui.com.vn/chinh-sach-bao-hanh"
            },
            {
                "doc_id": "cellphones-apple-unboxing",
                "title": "Quy định khui hộp và đổi trả sản phẩm Apple",
                "audience": "buyer",
                "category": "returns-policy",
                "raw_chars": 5988,
                "clean_chars": 2353,
                "reduction_percent": 60.7,
                "document_version": "not-stated",
                "source_url": "https://cellphones.com.vn/chinh-sach-khui-hop-apple"
            },
            {
                "doc_id": "cellphones-b2b-seller",
                "title": "Chính sách bán hàng doanh nghiệp và đối tác B2B",
                "audience": "seller",
                "category": "partner-policy",
                "raw_chars": 15740,
                "clean_chars": 2577,
                "reduction_percent": 83.6,
                "document_version": "not-stated",
                "source_url": "https://cellphones.com.vn/dich-vu-khach-hang-doanh-nghiep"
            },
            {
                "doc_id": "cellphones-extended-warranty",
                "title": "Dịch vụ và biểu phí bảo hành mở rộng rơi vỡ vào nước",
                "audience": "buyer",
                "category": "warranty-policy",
                "raw_chars": 14344,
                "clean_chars": 2749,
                "reduction_percent": 80.8,
                "document_version": "not-stated",
                "source_url": "https://cellphones.com.vn/bieu-phi-bao-hanh-mo-rong"
            },
            {
                "doc_id": "cellphones-shipping-policy",
                "title": "Chính sách giao nhận và kiểm tra hàng khi nhận",
                "audience": "buyer",
                "category": "shipping-policy",
                "raw_chars": 19074,
                "clean_chars": 1867,
                "reduction_percent": 90.2,
                "document_version": "not-stated",
                "source_url": "https://cellphones.com.vn/chinh-sach-giao-hang"
            },
            {
                "doc_id": "tnc-store-warranty",
                "title": "Chính sách bảo hành đổi mới linh kiện máy tính TNC Store",
                "audience": "buyer",
                "category": "warranty-policy",
                "raw_chars": 9415,
                "clean_chars": 2433,
                "reduction_percent": 74.2,
                "document_version": "not-stated",
                "source_url": "https://www.tncstore.vn/chinh-sach-bao-hanh.html"
            }
        ]
        self._send_json(inventory)

    def handle_post_chat(self):
        """Xử lý hỏi đáp RAG với Vector Store và Gemini LLM."""
        payload = self._read_json_body()
        question = payload.get("question", "").strip()
        filter_audience = payload.get("filter_audience", "").strip()
        top_k = int(payload.get("top_k", 3))

        if not question:
            self.send_error(400, "Missing question")
            return

        # 1. Retrieval
        if filter_audience:
            results = STORE.search_with_filter(question, top_k=top_k, metadata_filter={"audience": filter_audience})
        else:
            results = STORE.search(question, top_k=top_k)

        # 2. Context Formulation
        context_parts = []
        for r in results:
            context_parts.append(r["content"])
        context_str = "\n\n---\n\n".join(context_parts)

        # 3. Generation via LLM
        prompt = f"Context:\n{context_str}\n\nQuestion: {question}"
        answer = LLM_FN(prompt)

        self._send_json({
            "answer": answer,
            "results": results,
            "engine": LLM_DESC
        })

    def handle_post_compare_ab(self):
        """So sánh A/B cho Câu hỏi 3: Không lọc vs Có lọc audience='seller'."""
        q3 = "Doanh nghiệp mua số lượng lớn có chính sách chiết khấu và xuất hóa đơn VAT như thế nào?"
        res_no = STORE.search(q3, top_k=3)
        res_with = STORE.search_with_filter(q3, top_k=3, metadata_filter={"audience": "seller"})
        self._send_json({
            "no_filter": res_no,
            "with_filter": res_with
        })

    def handle_post_compare_chunking(self):
        """Chạy so sánh 4 chiến lược chunking trên tài liệu mẫu."""
        payload = self._read_json_body()
        sample_key = payload.get("sample", "dienthoaivui")

        if sample_key == "apple":
            sample_file = BASE_DIR / "data" / "ecommerce" / "cellphones-apple-unboxing.md"
        else:
            sample_file = BASE_DIR / "data" / "ecommerce" / "dienthoaivui-repair-warranty.md"

        raw_text = sample_file.read_text(encoding="utf-8")
        # Bỏ frontmatter
        if raw_text.startswith("---"):
            parts = raw_text.split("---", 2)
            if len(parts) >= 3:
                raw_text = parts[2].strip()

        # 1. FixedSize
        c_fixed = FixedSizeChunker(chunk_size=500, overlap=50).chunk(raw_text)
        # 2. Sentence
        c_sent = SentenceChunker(max_sentences_per_chunk=3).chunk(raw_text)
        # 3. Recursive
        c_recur = RecursiveChunker(chunk_size=1200).chunk(raw_text)
        # 4. Custom Section
        c_sec = SectionChunker(max_chunk_size=1200).chunk(raw_text)

        def make_stats(chunks: list[str]):
            lens = [len(c) for c in chunks] if chunks else [0]
            return {
                "count": len(chunks),
                "avg_length": sum(lens) / max(1, len(lens)),
                "chunks": chunks[:10]  # Giới hạn 10 chunks hiển thị
            }

        self._send_json({
            "fixed_size": make_stats(c_fixed),
            "by_sentences": make_stats(c_sent),
            "recursive": make_stats(c_recur),
            "section": make_stats(c_sec)
        })

    def _read_json_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0:
            return {}
        body = self.rfile.read(length).decode("utf-8")
        try:
            return json.loads(body)
        except Exception:
            return {}

    def _send_json(self, data: Any):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)


def main():
    init_rag_system()
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(("127.0.0.1", port), DemoRequestHandler)
    print("=" * 80)
    print(f"🚀 DEMO PRESENTATION SERVER ĐANG CHẠY TẠI: http://localhost:{port}")
    print("   Mở trình duyệt để trải nghiệm và thuyết trình bài Lab 07!")
    print("=" * 80)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Đang dừng máy chủ...")
        server.server_close()


if __name__ == "__main__":
    main()
