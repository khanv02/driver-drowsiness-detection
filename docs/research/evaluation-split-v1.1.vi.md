# Phân chia tập đánh giá NITYMED v1.1

**Protocol:** `drowsyalert-video-eval-v1.1`  
**Seed chọn mẫu:** 42  
**Cách tách:** không trùng clip; chưa có ánh xạ người tham gia  
**Định danh split chuẩn:** `2e4e0ea7eb2e529ea2db2f692444768a4de91023d9ce29829bcbdab911cbd047`

Các artifact cục bộ bị Git bỏ qua:

| Artifact | SHA-256 tệp |
|---|---|
| `evaluation-split-v1.1.csv` | `13f0133e0b729a1b45fb480dab32cccea64aabe37154f130005e5ed15ddcf65e` |
| `evaluation-worklist-v1.1.csv` | `5ca1246e5361ec4075acc86d4253c7e2a346f4fb7ce3aa0ff4d3ac4b2a5ff67b` |
| `review-schedule-v1.1.csv` | `1a24bfb7d71aca9a4802372725ccf46be7344c86136be71a7b005f66429fc3a9` |

Tập gồm toàn bộ 19 clip microsleep và 19 clip ngáp được chọn theo cách xác định. Không có clip ID hoặc hash nội dung trùng giữa các phân vùng. Bốn clip pilot đã xem được khóa vào validation. Thành viên split được cố định trước khi chú thích thêm hoặc chấm held-out.

## Số lượng

| Phân vùng/nhóm | Nữ | Nam | Tổng |
|---|---:|---:|---:|
| Validation microsleep | 3 | 3 | 6 |
| Validation ngáp | 3 | 3 | 6 |
| Test microsleep | 5 | 8 | 13 |
| Test ngáp | 7 | 6 | 13 |

- Validation dài 939,72 giây trên 12 clip.
- Test dài 2.011,64 giây trên 26 clip.
- Tổng thời lượng 2.951,36 giây (khoảng 49 phút 11 giây).
- Cả 12 clip validation đã review. 26 clip test held-out còn trong bảy đợt review.

## Clip validation

- `P1042751_720`, `P1042760_720`, `P1042762_720`, `P1042776_720`
- `P1042797_720`, `P1043081_720`, `P1043084_720`, `P1043089_720`
- `P1043090_720`, `P1043106_720`, `P1043112_720`, `P1043115_720`

## Clip test held-out

- `P1042748_720`, `P1042756_720`, `P1042757_720`, `P1042764_720`
- `P1042767_720`, `P1042769_720`, `P1042772_720`, `P1042786_720`
- `P1042787_720`, `P1042793_720`, `P1042795_720`, `P1042796_720`
- `P1042799_720`, `P1043067_720`, `P1043068_720`, `P1043075_720`
- `P1043083_720`, `P1043085_720`, `P1043094_720`, `P1043100_720`
- `P1043101_720`, `P1043114_720`, `P1043119_720`, `P1043122_720`
- `P1043129_720`, `P1043134_720`

Có thể chú thích độc lập clip test khi reviewer không thấy đầu ra mô hình, nhưng không dùng nhãn/kết quả test để chọn ngưỡng. Chỉ phát lại test một lần sau khi cấu hình validation đã khóa.

## Giới hạn

NITYMED cho biết có 21 người tham gia, nhưng cấu trúc tệp thu thập không ánh xạ clip với người. Phân tầng theo thư mục giới tính giảm mất cân bằng quan sát được nhưng không ngăn một người xuất hiện ở cả hai phân vùng. Mọi kết luận phải ghi rõ split không trùng clip và khả năng rò rỉ người tham gia; không được tuyên bố khái quát hóa độc lập theo người.
