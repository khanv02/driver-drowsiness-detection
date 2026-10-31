# Hướng dẫn đọc và thực hiện danh sách công việc

## Nguồn chuẩn

Danh sách task chi tiết và trạng thái chính thức được duy trì tại [`specs/001-drowsyalert/tasks.md`](../../specs/001-drowsyalert/tasks.md). Tài liệu tiếng Việt này chỉ giải thích cách sử dụng; không sao chép danh sách task, trạng thái checkbox, tiêu chí nghiệm thu hay quyết định nghiên cứu. Khi có khác biệt, luôn theo file `tasks.md`.

## Cách đọc task

- Task cha (`T-###`) là một gói công việc. Trước khi làm, chia thành các task con cụ thể trong đúng phase theo yêu cầu của danh sách chuẩn.
- Task con cần có phạm vi đủ nhỏ để triển khai, kiểm tra và review trong một lượt làm việc tập trung. Giữ nguyên ID để truy vết.
- Đọc các trường phase, priority, dependencies, requirements, objective, implementation steps, expected artifacts, verification và definition of done trước khi bắt đầu.
- Chỉ đánh dấu task cha hoàn tất khi mọi task con và tiêu chí nghiệm thu tương ứng đã được xác minh.
- Không đánh dấu hoàn tất chỉ vì file hoặc bộ khung đã tồn tại; cần kiểm chứng hành vi và bằng chứng được yêu cầu.

## Phê duyệt và nghiên cứu

- Các gate phê duyệt thuộc trách nhiệm của chủ dự án hoặc người hướng dẫn. Agent không được tự suy diễn rằng đã có phê duyệt.
- Task gắn nhãn Research/Data phải do người có thẩm quyền thực hiện khi cần đồng thuận, nguồn gốc dữ liệu hoặc hồ sơ đạo đức nghiên cứu.
- Không tự quyết định dữ liệu, giấy phép, nhãn chuẩn, ngưỡng đánh giá hoặc quy trình thu thập còn đang mở; ghi nhận người phụ trách và ảnh hưởng chặn tiến độ theo danh sách chuẩn.

## Thực hiện an toàn

- Theo dõi dependencies và critical path trước khi chọn task; làm song song chỉ khi danh sách chuẩn cho phép.
- Tạo nhánh ngắn hạn theo quy ước trong task list, kiểm tra thay đổi, chạy xác minh phù hợp và ghi lại bằng chứng.
- Không dùng `git reset --hard` hoặc viết lại lịch sử nhánh dùng chung để khôi phục. Tuân thủ quy trình phục hồi nêu trong task list.
- Không đưa dataset, video cá nhân, checkpoint, kết quả sinh tự động hoặc thông tin nhạy cảm vào Git.
- Không commit hoặc push nếu chưa được yêu cầu.

## Báo cáo hoàn tất

Khi xong, nêu task/đầu ra đã hoàn thành, file thay đổi, kiểm tra và kết quả, cùng hạn chế còn lại. Chỉ đánh dấu task hoàn tất khi có đủ bằng chứng theo tiêu chí nghiệm thu; phân biệt rõ kiểm tra tự động với nghiệm thu cần thiết bị thật.
