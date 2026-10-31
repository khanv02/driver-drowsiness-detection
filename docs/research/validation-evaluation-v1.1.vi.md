# Kết quả đánh giá validation v1.1

## Trạng thái

Baseline A/B/C đã được chạy trên validation nhưng coverage thấp; cấu hình chưa được đóng băng và chưa công bố kết quả held-out. Kết quả này phục vụ rà soát quy trình và chọn cấu hình, không phải kết luận hiệu suất cuối.

## Cách diễn giải

Chỉ so sánh phương pháp trên cùng clip, nhãn, điều kiện đủ tư cách và protocol. Báo riêng thời lượng hợp lệ, coverage, UNKNOWN và lý do mất quan sát; coverage thấp có thể khiến metric trên phần quan sát không đại diện cho toàn bộ clip. Không gán UNKNOWN thành NORMAL.

Validation có thể được dùng để chọn ngưỡng/cấu hình theo protocol đã duyệt. Sau khi lựa chọn và đóng băng, không điều chỉnh dựa trên test held-out. Kết quả CEW chỉ đo phân loại ảnh mắt, không phải hiệu suất video.

## Công việc còn lại

Rà soát manifest và chú thích, hoàn tất lựa chọn cấu hình validation, review độc lập test, pilot quy trình cuối và chỉ sau đó mới chạy đánh giá A/B/C held-out theo protocol.
