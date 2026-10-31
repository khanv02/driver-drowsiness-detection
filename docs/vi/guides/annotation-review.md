# Review chú thích độc lập NITYMED

Quy trình này ghi khoảng thời gian sự kiện quan sát được theo thời gian media. Không dùng dự đoán DrowsyAlert, EAR, PERCLOS, MAR hay kết quả head-pose làm nhãn tham chiếu. Worklist, bản nháp, chú thích cuối và video phải nằm dưới `data/` bị Git bỏ qua.

## 1. Khởi tạo worklist

```powershell
uv run python scripts/annotate_video_events.py init `
  --manifest data/processed/nitymed/video-manifest.csv `
  --worklist data/processed/nitymed/annotation-worklist.csv
```

Các dòng mới bắt đầu với `subject_group=unknown`, `session_group=unknown`, `split=unassigned`, điều kiện `unknown` và `review_status=pending`. Không suy đoán danh tính người tham gia từ tên tệp, thư mục giới tính hoặc ghép mặt tự động. Dùng ánh xạ do nhà cung cấp cấp hoặc ánh xạ dự án được review độc lập. Gán validation/test ở cấp nhóm người tham gia trước khi xuất cuối; một người/phiên không được xuất hiện ở cả hai split.

## 2. Review clip

```powershell
uv run python scripts/annotate_video_events.py review `
  --root data/raw/nitymed/DSM_Dataset-HDTV720 `
  --worklist data/processed/nitymed/annotation-worklist.csv `
  --draft data/processed/nitymed/annotation-draft.csv `
  --clip-id P1042748_720
```

Cửa sổ review mở ở trạng thái tạm dừng; nhấn `Space` để chạy theo FPS thực của video. `Space` tạm dừng/tiếp tục; `A`/`D` tua một giây; phím `1`–`5` bắt đầu loại sự kiện đang chọn, nhấn lại để kết thúc, đổi phím để bắt đầu loại mới tại thời điểm hiện tại; `U` xóa sự kiện gần nhất của clip; `Q` lưu và thoát. Khoảng sự kiện chưa kết thúc không được lưu.

Thư mục nhóm chỉ gợi ý hành vi cần xem, không phải nhãn onset/offset. Tuân theo hướng dẫn nhãn sự kiện đã khóa. Nên có reviewer thứ hai và phân xử; nếu chỉ có một người, dùng `single_reviewer` và công khai giới hạn.

Có thể thêm khoảng thời gian đã xác định từ player được phép:

```powershell
uv run python scripts/annotate_video_events.py add `
  --worklist data/processed/nitymed/annotation-worklist.csv `
  --draft data/processed/nitymed/annotation-draft.csv `
  --clip-id P1042748_720 --start 4.2 --end 6.1 --label yawn
```

## 3. Hoàn thiện metadata và xuất

Chỉ sửa bản worklist bị ignore. Trước khi đặt `review_status=reviewed`, xác nhận nhóm người/phiên, split và thẻ điều kiện. Xuất cuối từ chối review đang chờ, split chưa gán, sự kiện ngoài thời lượng, nguồn nhãn vòng tròn và rò rỉ split.

```powershell
uv run python scripts/annotate_video_events.py export `
  --worklist data/processed/nitymed/annotation-worklist.csv `
  --draft data/processed/nitymed/annotation-draft.csv `
  --output data/processed/nitymed/annotations.csv `
  --annotator-id reviewer-1 `
  --adjudication single_reviewer `
  --confidence not_provided
```

Không chấm held-out cuối chỉ vì xuất thành công. Phê duyệt protocol, kiểm toán split, review nhãn và hash manifest cũng phải được khóa theo T-126/T-139.
