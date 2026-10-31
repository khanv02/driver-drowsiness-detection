# Metric đánh giá theo thời gian

**Trạng thái:** Đã xác minh triển khai có tham số; Protocol `drowsyalert-video-eval-v1.1` được duyệt ngày 2026-10-26; chấm dữ liệu thật còn chờ.

`drowsyalert.experiments.metrics` cung cấp primitive độc lập dữ liệu cho Protocol Phase 6. Không có tolerance ghép mặc định: bên gọi phải truyền giới hạn sớm/muộn đã duyệt để provenance nêu rõ.

## Ghép sự kiện

Sự kiện tham chiếu và episode cảnh báo dự đoán có ID ổn định, clip ID và khoảng media-time hữu hạn. Trong mỗi clip, xử lý sự kiện tham chiếu theo thời gian và ghép với onset cảnh báo chưa dùng sớm nhất nằm trong cửa sổ sớm/muộn bao gồm biên. Mỗi tham chiếu và cảnh báo chỉ dùng một lần. Cảnh báo bắt đầu trước biên sớm vẫn là cảnh báo giả dù khoảng của nó chồng lên sự kiện sau đó.

Kết quả giữ ID đã ghép, ID tham chiếu/cảnh báo chưa ghép và độ trễ onset có dấu. Giá trị âm nghĩa là phát hiện sớm, không bị chặn về 0. Sự kiện bỏ lỡ không có độ trễ.

## Tổng hợp

- Metric sự kiện: TP, FP, FN, precision, recall, F1.
- Cảnh báo giả: cảnh báo không ghép chia cho số giờ quan sát hợp lệ.
- Độ trễ: giá trị thô đã ghép, số phát hiện/bỏ lỡ, trung bình, trung vị, độ lệch chuẩn tổng thể, khoảng biến thiên và phân vị 25/75 nội suy tuyến tính.
- Coverage: giây đủ điều kiện, hợp lệ, unknown; coverage; giờ đủ điều kiện/hợp lệ.

Phép chia không xác định trả `null`/`None`, không giả tạo số 0. Khi có tham chiếu và cảnh báo nhưng không ghép được, precision/recall/F1 hợp lệ bằng 0. Từ chối khoảng sai/trùng, tolerance âm/không hữu hạn, thời lượng âm và tổng coverage bất khả thi.

Các hàm không nạp video, chọn ngưỡng, định nghĩa ground truth hay đưa kết luận nghiên cứu. Tích hợp phải chứng minh A/B/C dùng cùng clip được duyệt, eligibility mask, nhãn, tolerance cố định -1/+2 giây và mẫu số.

## Episode cảnh báo và Accuracy hệ thống

Trạng thái frame chuyển thành khoảng media-time nửa mở theo trạng thái của mẫu trước. Chuyển `ALERT` sang `NORMAL` hoặc `UNKNOWN` kết thúc episode; các mẫu ALERT liên tiếp là một episode. Thời gian trước trạng thái đầu tiên là `UNKNOWN`. Mẫu phải hữu hạn, tăng nghiêm ngặt và nằm trong clip.

System Accuracy chia timeline mỗi clip thành bin cố định do bên gọi khai báo. Chồng lấp sự kiện tham chiếu và thời lượng trạng thái dự đoán dùng tham số tỷ lệ dương tường minh. Nếu ALERT và NORMAL cùng đạt tỷ lệ trong trường hợp hòa, bin là `UNKNOWN` để tránh tự chọn kết quả.

Accuracy chính là `correct_bins / all_bins`: UNKNOWN vẫn nằm trong mẫu số và không được tính đúng như bình thường. Accuracy chỉ trên quan sát và coverage là chẩn đoán riêng. TP/TN/FP/FN tính dự đoán quan sát được; `unknown_bins` giữ bằng chứng bị từ chối. Có thể nhóm theo điều kiện khai báo; thẻ thiếu tạo nhóm `unknown`.

Protocol v1 cố định bin 1 giây, stride 1 giây nên bin kề không chồng nhau. Tỷ lệ dương 0,50 thời lượng đủ điều kiện của bin áp dụng cho mức chiếm chỗ bởi sự kiện tham chiếu và thời lượng trạng thái dự đoán, không phải stride. Mã metric yêu cầu caller truyền kích thước bin và giữ tỷ lệ dương tường minh để hồ sơ chứng minh giá trị protocol.

## Bộ đánh giá hồ sơ chạy

`drowsyalert.experiments.evaluation` ghép chú thích nghiêm ngặt với hồ sơ chạy headless hoàn tất bằng clip ID. Clip trong run phải khớp chính xác corpus khai báo và method ID phải khớp yêu cầu. Báo cáo tách riêng ghép sự kiện, độ trễ có dấu, Accuracy bin cố định, coverage hợp lệ/unknown, lý do mất quan sát, số lượng thẻ điều kiện và thời gian xử lý. Từ chối run chưa hoàn tất, thiếu clip, không có bằng chứng frame, thời gian xử lý âm hoặc chú thích ngoài corpus.

Evaluator nhận protocol gồm nhãn tham chiếu, tolerance sớm/muộn, kích thước bin và tỷ lệ dương; không tự quyết định hành vi NITYMED nào là endpoint chính. Có thể xuất JSON nghiêm ngặt, từ chối giá trị không hữu hạn.
