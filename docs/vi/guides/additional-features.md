# Tính năng nghiên cứu bổ sung

Phương pháp B và C bổ sung một tín hiệu landmark cho baseline PERCLOS của A. Giá trị trong `configs/config.yaml` là mặc định triển khai có thể chỉnh, chưa phải ngưỡng an toàn đã kiểm định. Phải chọn trên dữ liệu train/validation rồi cố định trước khi đánh giá held-out.

## Phương pháp B: PERCLOS và ngáp

Tỷ lệ hình dạng miệng (MAR) dùng cặp landmark MediaPipe 61/291 làm chiều rộng, 82/87 và 312/317 làm hai độ mở dọc. Quan sát miệng hợp lệ khi landmark có mặt, hữu hạn và chiều rộng không suy biến.

Ứng viên ngáp bắt đầu khi MAR hợp lệ đạt `yawn_threshold`; trở thành một sự kiện khi độ mở liên tục hợp lệ ít nhất `yawn_seconds`. Bằng ngưỡng được tính là đạt. Một lần mở liên tục không tạo sự kiện thứ hai cho đến khi quan sát hợp lệ xuống dưới ngưỡng. Quan sát thiếu/sai hoặc khoảng trống vượt `max_gap_seconds` đặt lại ứng viên mà không tạo sự kiện. Sự kiện hoàn tất được giữ trong cửa sổ trượt `window_seconds`; nhánh tín hiệu B cần ít nhất `yawn_count` sự kiện.

Bằng chứng lượt chạy phân biệt số đếm cửa sổ, MAR hiện tại, sự kiện vừa hoàn tất, thời lượng ứng viên, tính hợp lệ và lý do không khả dụng. A/C không tính hoặc dùng bằng chứng ngáp.

MAR có thể thay đổi do nói, nét mặt, góc camera hoặc lỗi landmark. Sự kiện ngáp chỉ là chỉ báo hình học theo cấu hình, không chứng minh buồn ngủ sinh lý; ngưỡng và thời lượng phải được chọn bằng validation.

## Phương pháp C: PERCLOS và tư thế đầu tương đối

Tư thế đầu dùng ước lượng perspective-n-point sáu điểm. Trong triển khai này, pitch tương đối dương nghĩa là cúi đầu. Bằng chứng lưu bộ pitch/yaw/roll tương đối, tính hợp lệ, thời lượng cúi liên tục, cờ Boolean duy trì, pitch tham chiếu và lý do không khả dụng.

`head_pose_reference_degrees` có thể đặt pitch tuyệt đối cố định. Thí nghiệm có kiểm soát phải dùng và ghi nhận tham chiếu được protocol validation duyệt. Nếu đặt `null`, tracker live/demo lấy pitch hợp lệ đầu tiên làm tham chiếu và ghi nhận lúc lấy. Chế độ tự động tiện cho demo nhưng không phải tư thế trung tính đã kiểm định và không được âm thầm dùng để tinh chỉnh trên test held-out.

Pitch tương đối đạt `head_down_degrees` bắt đầu ứng viên. Chỉ báo đúng sau ít nhất `head_down_seconds` bằng chứng liên tục hợp lệ; cả hai phép so sánh đều bao gồm bằng. Mẫu dưới ngưỡng, pose sai, mất mặt hoặc khoảng trống vượt `max_gap_seconds` đặt lại thời lượng. Tham chiếu giữ nguyên trong lượt chạy.

Pose từ landmark đơn camera phụ thuộc hình học camera, không phải phép đo mệt mỏi vật lý. Cần kiểm định ngưỡng và quy trình tham chiếu trước so sánh nghiên cứu.

## Ma trận phương pháp có kiểm soát

| ID | CLI | Bằng chứng chung | Bằng chứng bổ sung |
|---|---|---|---|
| A | `perclos` | Nguồn mắt, nhắm kéo dài, cửa sổ/sẵn sàng PERCLOS và ngưỡng chính | Không; bỏ qua tín hiệu phụ |
| B | `perclos-yawn` | Giữ nguyên thiết lập A | Số ngáp hợp lệ trong cửa sổ ở dải PERCLOS kết hợp |
| C | `perclos-head-pose` | Giữ nguyên thiết lập A | Bằng chứng cúi đầu tương đối liên tục hợp lệ trong dải PERCLOS kết hợp |

Cả ba cảnh báo theo cùng quy tắc nhắm kéo dài hoặc PERCLOS chính. Trong khoảng từ `combined_perclos_threshold` đến `perclos_threshold`, B/C cần tín hiệu hợp lệ tương ứng. Nếu tín hiệu cần thiết không khả dụng, kết quả là `UNKNOWN`, không phải `NORMAL`. Dưới ngưỡng kết hợp, thiếu tín hiệu phụ không ảnh hưởng quyết định nền bình thường. Kết quả mỗi lượt lưu ID phương pháp, nguồn mắt, thiết lập chung, tên tín hiệu phụ và thiết lập đã phân giải. CSV từng frame ghi phương pháp đang chạy cùng tính hợp lệ của cả hai tín hiệu để có thể kiểm tra dữ liệu thiếu.
