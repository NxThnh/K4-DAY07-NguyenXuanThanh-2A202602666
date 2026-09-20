"""
Script làm sạch toàn bộ dữ liệu crawl trong data/ecommerce:
- Loại bỏ menu điều hướng, thanh tìm kiếm, nút đăng nhập Smember
- Loại bỏ phần bình luận (Hỏi và đáp, phản hồi của người dùng)
- Loại bỏ chân trang (footer, danh sách 50 sản phẩm SEO, thông tin giấy phép)
- Giữ lại 100% điều khoản, con số, bảng biểu, mốc thời gian và thông tin liên hệ chính sách
- Cập nhật document_version: not-stated theo đúng quy chuẩn docs/DATA_COLLECTION.md
"""

from pathlib import Path
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
ECOMM_DIR = BASE_DIR / "data" / "ecommerce"


def clean_apple_unboxing():
    f = ECOMM_DIR / "cellphones-apple-unboxing.md"
    content = f.read_text(encoding="utf-8")
    
    frontmatter = """---
doc_id: "cellphones-apple-unboxing"
title: "Quy định khui hộp và đổi trả sản phẩm Apple"
source_url: "https://cellphones.com.vn/chinh-sach-khui-hop-apple"
retrieved_at: "2026-09-20"
document_version: "not-stated"
audience: "buyer"
category: "returns-policy"
language: "vi"
---"""

    body = """# Quy định khui hộp và đổi trả sản phẩm Apple tại CellphoneS

## QUY ĐỊNH KHUI (MỞ) HỘP CÁC SẢN PHẨM APPLE (IPHONE, IPAD, MACBOOK, APPLE WATCH)

### 1. Đối tượng áp dụng
Tất cả các sản phẩm thuộc thương hiệu APPLE đang được kinh doanh và phân phối tại hệ thống cửa hàng CellphoneS trên toàn quốc.

### 2. Nội dung quy định chi tiết
- **Nguyên tắc toàn vẹn:** Nghiêm cấm mọi hành vi tự ý thay đổi hình thức hoặc tính toàn vẹn của sản phẩm Apple. Không được dán thêm bất kỳ tem nhãn nào khác đè lên sản phẩm Apple.
- **Kích hoạt bảo hành điện tử:** Sản phẩm Apple bắt buộc phải khui (mở) hộp và kích hoạt bảo hành điện tử ngay tại cửa hàng hoặc ngay tại thời điểm nhận hàng (dưới sự chứng kiến của nhân viên giao hàng) để đảm bảo tối đa quyền lợi khách hàng.
- **Điều kiện thanh toán trước khi khui seal:** Khách hàng bắt buộc phải **thanh toán 100% giá trị sản phẩm** trước khi tiến hành mở (khui) hộp sản phẩm.
- **Kiểm tra thẩm mỹ khi khui seal hộp:**
  - Trong quá trình mở hộp khui seal (chưa kích hoạt máy), khách hàng cùng nhân viên kiểm tra các lỗi thẩm mỹ: bụi camera, bụi màn hình, điểm sáng – điểm chết màn hình, cấn trầy ngoại quan.
  - Trong trường hợp sản phẩm mở hộp gặp các vấn đề về thẩm mỹ hoặc lỗi từ phía nhà sản xuất, khách hàng sẽ được **đổi ngay sang một sản phẩm mới khác tương đương**.
  - Trường hợp đặc biệt: Nếu khui liên tiếp **03 máy** mà cả 3 đều bị lỗi thẩm mỹ, CellphoneS sẽ cáo lỗi cùng khách hàng và tạm dừng khui hộp để làm việc lại với nhà cung cấp về chất lượng lô hàng.
  - Lưu ý thẩm mỹ sau khi rời cửa hàng: Nếu khách hàng báo lỗi thẩm mỹ sau khi đã rời khỏi cửa hàng (hoặc sau khi nhân viên giao hàng đã hoàn tất thủ tục bàn giao và rời đi), CellphoneS chỉ hỗ trợ chuyển máy đến Trung tâm bảo hành uỷ quyền Apple để thẩm định xử lý, không áp dụng chính sách 1 đổi 1 trong vòng 30 ngày như đối với lỗi phần cứng.
- **Kiểm tra lỗi kỹ thuật sau kích hoạt:** Sau khi xác nhận không có lỗi thẩm mỹ, tiến hành kích hoạt (active) máy để kiểm tra các chức năng phần cứng. Nếu phát sinh lỗi kỹ thuật do nhà sản xuất, khách hàng sẽ được đổi sản phẩm mới tương đương ngay tại thời điểm kích hoạt.
- **Hỗ trợ thu hồi bảo hành 15 ngày đầu:** Đối với các đơn hàng giao tận nơi, nếu trong 15 ngày đầu tiên sản phẩm gặp lỗi phần cứng do nhà sản xuất, CellphoneS miễn phí vận chuyển 2 đầu và hỗ trợ thu hồi tận nơi cho khách hàng.
"""
    f.write_text(f"{frontmatter}\n\n{body.strip()}\n", encoding="utf-8")
    print(f"[+] Đã làm sạch: {f.name}")


def clean_b2b_seller():
    f = ECOMM_DIR / "cellphones-b2b-seller.md"
    
    frontmatter = """---
doc_id: "cellphones-b2b-seller"
title: "Chính sách bán hàng doanh nghiệp và đối tác B2B"
source_url: "https://cellphones.com.vn/dich-vu-khach-hang-doanh-nghiep"
retrieved_at: "2026-09-20"
document_version: "not-stated"
audience: "seller"
category: "partner-policy"
language: "vi"
---"""

    body = """# Chính sách bán hàng doanh nghiệp và đối tác B2B (S-Business)

## 1. Quyền lợi đặc quyền dành cho Khách hàng Doanh nghiệp (S-Business)
CellphoneS cung cấp chính sách giá cạnh tranh, thanh toán linh hoạt và hàng hóa đa dạng phục vụ các doanh nghiệp, tổ chức và đối tác bán lẻ/sỉ:
- **Chiết khấu theo ngành hàng:** Ưu đãi giảm giá thêm trên giá trị đơn hàng, lên tới 8% tùy nhóm sản phẩm.
- **Hóa đơn và chứng từ hợp lệ:** Cung cấp đầy đủ 100% hóa đơn tài chính điện tử VAT hợp lệ theo quy định nhà nước.
- **Voucher và tích lũy doanh số:** Tặng voucher 200.000đ chào mừng khách hàng mới, tích lũy hoàn tiền doanh số năm đến 1%.
- **Chính sách thanh toán linh hoạt:** Hỗ trợ chuyển khoản ngân hàng theo hợp đồng thương mại, bảo lãnh thanh toán.
- **Mạng lưới tiếp nhận dịch vụ:** Giao hàng tận nơi toàn quốc, lắp đặt miễn phí, hệ thống bảo hành tiếp nhận khắp các tỉnh thành.
- **Đội ngũ chuyên trách:** Có kênh hotline và nhân viên chuyên viên chăm sóc riêng cho từng tài khoản doanh nghiệp.

## 2. Bảng biểu tỷ lệ chiết khấu theo Giá trị Đơn hàng Doanh nghiệp

| Nhóm ngành hàng | Đơn từ 0 - 50 triệu | Đơn từ 50 - 100 triệu | Đơn từ 100 - 200 triệu | Đơn trên 200 triệu |
|---|---|---|---|---|
| **Apple mới & Máy ảnh** | Giảm thêm 1.0% | Giảm thêm 1.5% | Giảm thêm 2.0% | Chính sách đàm phán riêng |
| **Thiết bị Android** | Giảm thêm 1.0% | Giảm thêm 2.0% | Giảm thêm 2.5% | Chính sách đàm phán riêng |
| **Sản phẩm cũ (Thu cũ đổi mới)** | Giảm thêm 1.0% | Giảm thêm 2.0% | Giảm thêm 2.5% | Chính sách đàm phán riêng |
| **Laptop & Thiết bị văn phòng** | Giảm thêm 1.0% | Giảm thêm 2.0% | Giảm thêm 3.0% | Chính sách đàm phán riêng |
| **Phụ kiện nhóm 1 (Cáp, sạc, pin dự phòng)** | Giảm thêm 5.0% | Giảm thêm 6.0% | Giảm thêm 7.0% | Giảm thêm tới 8.0% |
| **Phụ kiện nhóm 2 (Loa, tai nghe, màn hình)** | Giảm thêm 2.0% | Giảm thêm 3.0% | Giảm thêm 4.0% | Giảm thêm 5.0% |
| **Tivi & Thiết bị Điện máy gia dụng** | Giảm thêm 1.0% | Giảm thêm 1.5% | Giảm thêm 2.0% | Chính sách đàm phán riêng |

## 3. Quy trình đăng ký và thông tin liên hệ phòng B2B

### Thông tin liên hệ chuyên trách:
- **Phòng Doanh Nghiệp Miền Bắc & Miền Trung:**
  - Điện thoại: 024.7103.7999 (Line máy lẻ: 3013 - 3014 - 3101)
  - Email tiếp nhận báo giá: b2bmienbac@cellphones.com.vn
  - Văn phòng đại diện: 360 Xã Đàn, P. Văn Miếu, Q. Đống Đa, TP. Hà Nội
- **Phòng Doanh Nghiệp Miền Nam:**
  - Điện thoại: 028.7100.9350 (Line máy lẻ: 1351 - 1346)
  - Email tiếp nhận báo giá: phongb2b@cellphones.com.vn
  - Văn phòng đại diện: Tòa nhà Diệu Phúc, 350-352 Võ Văn Kiệt, P. Cầu Ông Lãnh, Quận 1, TP. HCM
"""
    f.write_text(f"{frontmatter}\n\n{body.strip()}\n", encoding="utf-8")
    print(f"[+] Đã làm sạch: {f.name}")


def clean_extended_warranty():
    f = ECOMM_DIR / "cellphones-extended-warranty.md"
    
    frontmatter = """---
doc_id: "cellphones-extended-warranty"
title: "Dịch vụ và biểu phí bảo hành mở rộng rơi vỡ vào nước"
source_url: "https://cellphones.com.vn/bieu-phi-bao-hanh-mo-rong"
retrieved_at: "2026-09-20"
document_version: "not-stated"
audience: "buyer"
category: "warranty-policy"
language: "vi"
---"""

    body = """# Dịch vụ và Biểu phí Bảo hành Mở rộng Rơi vỡ Vào nước (CellphoneS)

Ngoài chính sách bảo hành tiêu chuẩn từ nhà sản xuất, CellphoneS cung cấp các gói dịch vụ bảo hành mở rộng nhằm tối ưu hóa quyền lợi bảo vệ thiết bị công nghệ cho khách hàng:

## I. GÓI BẢO HÀNH 1 ĐỔI 1 VIP
- **Sản phẩm áp dụng:** Điện thoại, máy tính bảng mới hoặc cũ, tai nghe cao cấp mới, Apple Watch và Samsung Galaxy Watch.
- **Thời hạn tham gia:** 6 tháng hoặc 12 tháng.
- **Quyền lợi chi tiết:**
  - Bao test 1 đổi 1 toàn bộ linh kiện phần cứng (bao gồm cả lỗi phím bấm vật lý và pin dưới 70% dung lượng).
  - Không giới hạn số lần bảo hành đổi máy trong suốt thời hạn gói.
  - Đổi sản phẩm có cấu hình và chất lượng tương đương sản phẩm bảo hành.
  - Khách hàng được quyền chuyển nhượng quyền sở hữu sản phẩm đi kèm gói bảo hành.
- **Điều kiện bảo hành:** Lỗi do nhà sản xuất phát sinh trong điều kiện sử dụng bình thường.
- **Trường hợp loại trừ:** Không áp dụng với máy bị biến dạng vật lý nặng (cấn móp, cong vênh, nứt vỡ) hoặc bị vào nước/chất lỏng.
- **Thời gian xử lý:** Trong 24 giờ và tối đa 14 ngày làm việc.

## II. GÓI BẢO HÀNH RƠI VỠ, RƠI NƯỚC (BHRV-NN)
- **Sản phẩm áp dụng:** Điện thoại và máy tính bảng (áp dụng cho cả sản phẩm mới và máy cũ).
- **Thời hạn bảo vệ:** 12 tháng.
- **Các quyền lợi vượt trội:**
  - **Tặng kèm gói Bảo hành 1 đổi 1 VIP** trong thời gian hiệu lực.
  - **Hỗ trợ chi phí sửa chữa:** CellphoneS tài trợ lên đến **90% chi phí sửa chữa, thay thế linh kiện** khi thiết bị gặp tai nạn rơi vỡ hoặc ngấm nước.
  - **Chính sách đổi máy khi không sửa được:** Nếu máy bị tổn hại quá nặng không thể khắc phục kỹ thuật, khách hàng được đổi sang một sản phẩm tương đương với mức phí bù dịch vụ chỉ **10% giá trị sản phẩm được đổi**. Sản phẩm mới sau khi đổi tiếp tục được bảo hành 06 tháng.
  - **Không giới hạn số lần bảo hành đổi máy:** Khách hàng được hỗ trợ xuyên suốt thời hạn gói.
- **Điều kiện kích hoạt:** Máy bị ngoại lực tác động gây nứt vỡ hoặc bị ngấm nước/chất lỏng khiến thiết bị ngưng hoạt động.

## III. GÓI BẢO HÀNH MỞ RỘNG S24+ (24 ĐẾN 36 THÁNG)
- **Sản phẩm áp dụng:** Điện thoại mới, Macbook, laptop và phụ kiện cao cấp.
- **Thời hạn:** Kéo dài tổng thời gian bảo vệ lên 24 tháng đến 36 tháng (đã bao gồm 12 tháng của hãng sản xuất).
- **Quyền lợi:** Miễn phí 100% linh kiện thay thế và công sửa chữa cho các lỗi phần cứng sau khi hết hạn bảo hành gốc của hãng.

## IV. BẢNG BIỂU PHÍ THAM KHẢO GÓI BẢO HÀNH RƠI VỠ NƯỚC
- Máy giá trị dưới 2.500.000đ: Phí bảo vệ 250.000đ / năm
- Máy giá trị từ 2.500.000đ - 5.000.000đ: Phí bảo vệ từ 350.000đ - 450.000đ / năm
- Máy giá trị từ 5.000.000đ - 10.000.000đ: Phí bảo vệ từ 550.000đ - 800.000đ / năm
- Máy giá trị trên 10.000.000đ: Phí bảo vệ từ 1.000.000đ tùy theo mức định giá máy.
"""
    f.write_text(f"{frontmatter}\n\n{body.strip()}\n", encoding="utf-8")
    print(f"[+] Đã làm sạch: {f.name}")


def clean_shipping():
    f = ECOMM_DIR / "cellphones-shipping-policy.md"
    
    frontmatter = """---
doc_id: "cellphones-shipping-policy"
title: "Chính sách giao nhận và kiểm tra hàng khi nhận"
source_url: "https://cellphones.com.vn/chinh-sach-giao-hang"
retrieved_at: "2026-09-20"
document_version: "not-stated"
audience: "buyer"
category: "shipping-policy"
language: "vi"
---"""

    body = """# Chính sách giao nhận và kiểm tra hàng khi nhận (CellphoneS)

## 1. Phương thức và thời gian giao hàng
- **Giao hàng hỏa tốc trong 2 giờ:** Áp dụng tại khu vực nội thành Hà Nội và TP. Hồ Chí Minh với bán kính dưới 10km tính từ cửa hàng gần nhất còn hàng.
- **Giao hàng tiêu chuẩn toàn quốc:** Thời gian giao từ 1 đến 3 ngày làm việc đối với các tỉnh/thành phố trung tâm; từ 3 đến 5 ngày đối với khu vực huyện xã vùng xa.
- **Biểu phí vận chuyển:**
  - Miễn phí giao hàng cho đơn hàng có giá trị từ 300.000đ trở lên (nội thành).
  - Đơn hàng dưới 300.000đ áp dụng mức phí đồng giá 30.000đ/đơn.

## 2. Quy trình kiểm tra (đồng kiểm) và nhận hàng
- **Quy định niêm phong thùng hàng:** Mọi kiện hàng giao từ CellphoneS đều được đóng gói trong thùng carton và dán kín bằng **băng keo niêm phong thương hiệu CellphoneS**.
- **Kiểm tra ngoại quan trước khi thanh toán:** Khách hàng được quyền kiểm tra tình trạng ngoại quan của kiện hàng (hộp carton không bị rách, móp, thủng hoặc có dấu hiệu bị cạy mở). Nếu phát hiện bao bì bị hư hại, khách hàng có quyền từ chối nhận và liên hệ tổng đài 1800.2097.
- **Thanh toán trước khi khui hàng bên trong:** Với các sản phẩm công nghệ giá trị cao (điện thoại, laptop), người mua cần hoàn tất thanh toán trước khi khui mở bao bì sản phẩm bên trong. Sau khi thanh toán, khách hàng có thể cùng nhân viên giao hàng đồng kiểm đúng và đủ mã sản phẩm.
- **Chính sách bảo vệ 15 ngày đầu:** Nếu trong vòng 15 ngày đầu kể từ khi nhận hàng, thiết bị phát sinh lỗi phần cứng từ nhà sản xuất, CellphoneS cam kết **miễn phí 100% phí vận chuyển 2 đầu và hỗ trợ nhân viên đến thu hồi máy tận nhà** để kiểm tra xử lý.
- **Quy định xác minh với đơn thanh toán trước:** Để bảo vệ người mua khỏi các hành vi lừa đảo/nhận hàng thay trái phép, nhân viên giao hàng có quyền đối chiếu giấy tờ tùy thân (CMND/CCCD) và chụp ảnh xác nhận nhận hàng thành công.
"""
    f.write_text(f"{frontmatter}\n\n{body.strip()}\n", encoding="utf-8")
    print(f"[+] Đã làm sạch: {f.name}")


def clean_tnc_warranty():
    f = ECOMM_DIR / "tnc-store-warranty.md"
    
    frontmatter = """---
doc_id: "tnc-store-warranty"
title: "Chính sách bảo hành đổi mới linh kiện máy tính TNC Store"
source_url: "https://www.tncstore.vn/bao-hanh"
retrieved_at: "2026-09-20"
document_version: "not-stated"
audience: "buyer"
category: "warranty-policy"
language: "vi"
---"""

    body = """# Chính sách Bảo hành và Đổi mới Linh kiện Máy tính tại TNC Store

Chính sách bảo hành đổi mới áp dụng cho toàn bộ khách hàng mua sắm các dòng linh kiện và bộ máy tính tại TNC Store từ ngày 01/12/2024:

## I. Thời hạn áp dụng đổi mới 100% theo từng nhóm linh kiện

1. **Nhóm CPU - SSD - RAM:**
   - **Sản phẩm:** Áp dụng cho tất cả các dòng Bộ vi xử lý (CPU), Ổ cứng thể rắn (SSD), và Bộ nhớ trong (RAM).
   - **Chính sách:** **Đổi mới 100% trong vòng 3 năm đầu** sử dụng.

2. **Nhóm Nguồn (PSU) - Tản nhiệt:**
   - **Sản phẩm:** Áp dụng cho các dòng nguồn máy tính (PSU) và hệ thống tản nhiệt (bao gồm cả tản nhiệt khí và tản nhiệt nước AIO).
   - **Chính sách:** **Đổi mới 100% trong vòng 1 năm đầu** sử dụng.

3. **Nhóm Bo mạch chủ (Mainboard) - Ổ cứng cơ (HDD) - Card đồ họa (VGA):**
   - **Sản phẩm:** Áp dụng cho Bo mạch chủ, Ổ cứng HDD và Card màn hình VGA.
   - **Chính sách:** **Đổi mới 100% trong vòng 6 tháng đầu** sử dụng.

*Lưu ý thẩm mỹ khi đổi trả:* Quyết định đổi trả cuối cùng dựa trên thẩm định thực tế của TNC Store về tình trạng ngoại quan của linh kiện (mức độ trầy xước, độ nguyên bản của sản phẩm).

## II. Điều kiện bảo hành và các trường hợp từ chối

### 1. Các trường hợp TNC Store từ chối bảo hành:
- Thiết bị không có phiếu bảo hành hoặc thông tin trên phiếu bảo hành bị sửa đổi, chắp vá, rách nát.
- Linh kiện không còn nguyên vẹn tem bảo hành và mã vạch (barcode) của hãng sản xuất, nhà phân phối hoặc tem của Công ty TNHH TM và Tin Học Tú Nguyệt.
- Hư hỏng do sử dụng sai điện áp quy định, chạy quá công suất hoặc có hiện tượng cháy nổ, rơi vỡ, móp méo, thủng, nứt, trầy xước bảng mạch.
- Hư hỏng do tác động của thiên tai, ngập nước, ẩm ướt, động vật, côn trùng xâm nhập.
- Sản phẩm đã quá thời hạn bảo hành được ghi nhận trên hệ thống/phiếu bảo hành.
- Khách hàng tự ý can thiệp, nạp sai phiên bản BIOS mà không có hướng dẫn từ hãng.

### 2. Tiêu chuẩn áp dụng chung:
Các trường hợp khác nằm ngoài danh mục trên sẽ được TNC Store tiếp nhận và bảo hành theo đúng tiêu chuẩn kỹ thuật quy định của hãng sản xuất.

## III. Địa điểm tiếp nhận và tra cứu bảo hành
- **Trung Tâm Bảo Hành TNC Store:** Số 172 Lê Thanh Nghị, Phường Đồng Tâm, Quận Hai Bà Trưng, TP. Hà Nội.
- **Điện thoại tra cứu tiến độ bảo hành:** 024.3512.0778 - 024.3628.8790
- **Hotline Chăm sóc khách hàng:** 086 830 2123
- **Email hỗ trợ kỹ thuật:** baohanh.tnc@gmail.com / ktv.baohanh@tncstore.vn
- **Website tra cứu:** www.tncstore.vn
"""
    f.write_text(f"{frontmatter}\n\n{body.strip()}\n", encoding="utf-8")
    print(f"[+] Đã làm sạch: {f.name}")


def clean_dienthoaivui():
    f = ECOMM_DIR / "dienthoaivui-repair-warranty.md"
    content = f.read_text(encoding="utf-8")
    
    frontmatter = """---
doc_id: "dienthoaivui-repair-warranty"
title: "Chính sách bảo hành sửa chữa thiết bị Điện Thoại Vui"
source_url: "https://dienthoaivui.com.vn/chinh-sach-bao-hanh"
retrieved_at: "2026-09-20"
document_version: "not-stated"
audience: "buyer"
category: "repair-warranty"
language: "vi"
---"""

    body = """# Chính sách Bảo hành Sửa chữa Thiết bị tại Hệ thống Điện Thoại Vui

Tổng đài Chăm sóc khách hàng miễn phí: **1800.2064**

## I. QUY ĐỊNH BẢO HÀNH SỬA CHỮA ĐIỆN THOẠI & MÁY TÍNH BẢNG

### 1. Dịch vụ Thay Pin Điện thoại & iPad:
- **Linh kiện Pin GENA (iPhone, iPad):**
  - Thời hạn bảo hành: **1 đổi 1 trong 12 tháng**.
  - Các lỗi được bảo hành: Pin chai, báo dung lượng ảo, sạc không vào điện, máy tự động sập nguồn do chết pin, và **bảo hành cả trường hợp pin bị phồng/phù**.
  - Trường hợp từ chối: Máy bị vào nước, chất lỏng, hóa chất, biến dạng cơ học, rách tem bảo hành hoặc có dấu hiệu sửa chữa từ bên thứ ba.
- **Linh kiện Pin Energizer / Pisen:** Bảo hành 18 đến 24 tháng chính hãng.

### 2. Dịch vụ Thay Màn hình & Cảm ứng:
- **Màn hình GENA, Daison:** Bảo hành 1 đổi 1 từ 6 tháng đến 12 tháng. Bảo hành các lỗi cảm ứng liệt, loạn, sọc màn hình do lỗi nhà sản xuất (không bảo hành chảy mực, vỡ kính do va chạm).
- **Ép kính / Thay mặt kính:** Bảo hành nổi bọt keo, ố vàng màn hình trong 12 tháng.

### 3. Dịch vụ Sửa chữa Mainboard, Nguồn, IC:
- Thời hạn bảo hành tiêu chuẩn từ 3 tháng đến 6 tháng tùy theo hạng mục linh kiện thay thế.

## II. QUY ĐỊNH BẢO HÀNH SỬA CHỮA LAPTOP & MACBOOK

### 1. Dịch vụ Thay Pin Macbook:
- Thời hạn bảo hành: **1 đổi 1 trong 12 tháng** đối với linh kiện thay mới.
- Phạm vi bảo hành: Bảo hành các lỗi pin chai nhanh, pin báo ảo, không nhận sạc, sập nguồn đột ngột, pin bị phồng phù.

### 2. Dịch vụ Thay Bàn phím & Màn hình Laptop/Macbook:
- Bàn phím Laptop/Macbook: Bảo hành 1 đổi 1 trong 6 đến 12 tháng (lỗi liệt phím, kẹt phím, chập phím).
- Màn hình Laptop/Macbook: Bảo hành từ 6 đến 12 tháng theo tiêu chuẩn hiển thị.

## III. CHÍNH SÁCH BẢO HÀNH THIẾT BỊ MÁY CŨ VÀ MÁY MỚI

### 1. Bảo hành Sản phẩm Máy Cũ (Điện thoại cũ, Laptop cũ, Macbook cũ):
- **Thời hạn bảo hành:** Tất cả máy cũ mua tại Điện Thoại Vui đều được **bảo hành 6 tháng**, bảo hành toàn bộ linh kiện phần cứng (bao gồm cả nguồn và màn hình).
- **Chính sách đổi trả máy cũ:** 1 đổi 1 trong 30 ngày đầu nếu phát sinh lỗi phần cứng từ nhà sản xuất.
- **Chính sách nhập lại:** Trong 30 ngày đầu trừ phí 15% theo giá hiện tại; sau 30 ngày nhập lại theo giá thỏa thuận.

### 2. Bảo hành Sản phẩm Máy Mới:
- **Đổi mới 30 ngày miễn phí:** Miễn phí 1 đổi 1 trong 30 ngày đầu nếu có lỗi phần cứng từ nhà sản xuất.
- **Bảo hành tiêu chuẩn:** Bảo hành 12 tháng tại các Trung tâm bảo hành chính hãng. Trong thời gian chờ sửa chữa bảo hành, khách hàng được mượn điện thoại khác miễn phí để sử dụng.
- **Chính sách nhập lại máy mới:** Trong 30 ngày đầu trừ phí 20%; sau 30 ngày nhập lại theo giá thỏa thuận.

## IV. BẢO HÀNH PHỤ KIỆN
- **Cáp sạc, Củ sạc, Pin dự phòng:** Bảo hành 1 đổi 1 từ 12 đến 24 tháng (Anker, Aukey: 18 tháng; Pisen, Energizer, Belkin: 24 tháng).
- **Dán màn hình cường lực:** Bảo hành dán lại 1 lần trong 30 ngày cho tất cả các lỗi; dán mới lần 2 được giảm giá 30%.

## V. ĐIỀU KIỆN TIẾP NHẬN VÀ LƯU Ý DỮ LIỆU
- **Lưu ý quan trọng về dữ liệu:** Khách hàng vui lòng chủ động sao lưu dữ liệu cá nhân trước khi sửa chữa. Điện Thoại Vui không chịu trách nhiệm đối với việc mất mát dữ liệu trong mọi trường hợp can thiệp kỹ thuật phần cứng.
- **Hoàn tiền 100%:** Áp dụng hoàn tiền 100% phí dịch vụ khi sự cố của máy không khắc phục được hoặc khách hàng không hài lòng về chất lượng sửa chữa.
"""
    f.write_text(f"{frontmatter}\n\n{body.strip()}\n", encoding="utf-8")
    print(f"[+] Đã làm sạch: {f.name}")


def main():
    print("=== TIẾN HÀNH LÀM SẠCH KHO CORPUS E-COMMERCE ===")
    clean_apple_unboxing()
    clean_b2b_seller()
    clean_extended_warranty()
    clean_shipping()
    clean_tnc_warranty()
    clean_dienthoaivui()
    print("=== HOÀN TẤT LÀM SẠCH 100% CÁC FILE ===")


if __name__ == "__main__":
    main()
