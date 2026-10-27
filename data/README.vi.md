# Dữ liệu cục bộ

<p><a href="README.md">English</a> | <strong>Tiếng Việt</strong></p>

Mọi tệp trong `data/` là dữ liệu cục bộ, riêng tư và bị Git bỏ qua, ngoại trừ các file `.gitkeep` và hai README.

## Tải CEW cho Phase 3

1. Đọc điều khoản nghiên cứu, phi thương mại, trích dẫn và không phân phối lại trên [trang CEW chính thức](https://parnec.nuaa.edu.cn/_upload/tpl/02/db/731/template731/pages/xtan/ClosedEyeDatabases.html).
2. Tải thủ công archive **eye-patch** từ trang chính thức; không dùng mirror.
3. Trước khi giải nén, ghi nhận định danh archive cục bộ:

   ```powershell
   uv run python scripts/download_dataset.py --archive C:\path\to\CEW-eye-patches.rar
   ```

4. Giải nén archive vào `data/raw/cew/`. Không commit archive hoặc dữ liệu đã giải nén.
5. Thông báo cho nhóm triển khai khi dữ liệu sẵn sàng. T-075 sẽ kiểm tra cấu trúc thực tế trước khi chọn lệnh chuẩn bị; không đổi tên thư mục chỉ để khớp parser nhãn hiện tại.

Nhãn logic dự kiến là `open` (class 0) và `closed` (class 1). Sau khi kiểm tra, ghi lại ánh xạ thư mục đã giải nén trong `docs/research/dataset-card.md`.

## Quy ước thư mục

- `raw/`: archive/bản giải nén nguồn chưa chỉnh sửa; ghi provenance riêng.
- `processed/`: ảnh mắt, manifest và báo cáo chuẩn bị được sinh ra.
- `volunteer/`: dữ liệu người tham gia có quản lý đồng ý, chỉ dành cho các phase sau.

Không bao giờ commit dataset đã tải, video người tham gia, checkpoint hoặc kết quả sinh tự động. Không phân phối lại CEW qua repository này.

## Yêu cầu video theo thời gian Phase 6

NITYMED HDTV720 nằm trong `data/raw/nitymed/DSM_Dataset-HDTV720/`. Inventory được tạo tại `data/processed/nitymed/video-manifest.csv`; cả hai vị trí đều bị Git bỏ qua. Xem `docs/research/nitymed-dataset-card.md` để biết nguồn gốc, số lượng, phát hiện toàn vẹn và các cổng chú thích/nhóm còn mở. Thư mục phân loại không phải nhãn thời điểm bắt đầu/kết thúc.

Không ghi hình tình nguyện viên trước khi được phê duyệt quy trình của người hướng dẫn/đạo đức và đồng thuận. Archive nguồn bổ sung phải nằm trong `data/raw/<dataset-id>/`, kèm provenance và SHA-256 được ghi trước khi giải nén khi có archive.
