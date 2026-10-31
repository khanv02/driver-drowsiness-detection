# Tasks: DrowsyAlert — Bản dịch tiếng Việt

**Tính năng:** `specs/001-drowsyalert`
**Căn cứ:** SRS `spec.md`, repository hiện tại và bảy luồng công việc được yêu cầu.
**Trạng thái kế hoạch:** Chủ dự án đã duyệt `spec.md`, `plan.md`, Constitution v1.0.0 và nguồn Project 12 hiện có vào 2026-10-26. CEW và NITYMED là các nguồn dữ liệu được chọn; Protocol v1.1 đã duyệt. Chú thích thời gian cuối, khóa ngưỡng chỉ bằng validation, review/chấm held-out và nghiệm thu webcam/âm thanh thủ công vẫn còn mở. Phải rà soát trạng thái Git có thay đổi trước khi thao tác nhánh hoặc commit.

> Đây là bản diễn giải tiếng Việt theo phase, không phải bản dịch từng dòng: một số task con được gom nhóm và các trường acceptance/verification không được lặp lại đầy đủ. Dùng [checklist chuẩn](../../specs/001-drowsyalert/tasks.md) cho nội dung đầy đủ, trạng thái và tiêu chí nghiệm thu; khi có khác biệt, checklist chuẩn được ưu tiên.

## Cách thực hiện danh sách task

Mỗi T-task dưới đây là một gói công việc cha. Trước khi bắt đầu, hãy chia thành task con, mỗi task thay đổi một hành vi hoặc artifact. Chọn phạm vi có thể triển khai, xác minh và review trong một phiên Codex tập trung. Thêm task con vào phase đang làm với ID ổn định trước khi triển khai; chỉ đánh dấu task cha sau khi mọi task con đạt kiểm tra nghiệm thu. Không tự chia nhỏ trước các quyết định nghiên cứu tương lai bằng chi tiết phỏng đoán. “Test” nghĩa là kiểm thử hoặc kiểm tra quan sát được thuộc chính task đó, không phải hoạt động dồn vào cuối. Task thu thập dữ liệu và protocol nghiên cứu mang nhãn **Research/Data** phải do người có thẩm quyền thực hiện, có đồng ý và hồ sơ nguồn gốc. Không đánh dấu hoàn tất chỉ vì file hoặc scaffold tồn tại; phải kiểm tra hành vi theo bằng chứng nghiệm thu.

### Quy trình nhánh và phục hồi

Migration bố cục root được lưu tại commit `3f717de` trên `checkpoint/root-layout`; nhánh `master` gốc không đổi. `feature/001-drowsyalert` bắt đầu từ checkpoint đó. Dùng một nhánh ngắn hạn `task/T-###-slug` cho mỗi task con. Giữ nhánh tập trung, chạy kiểm tra của task, review diff, commit rồi merge vào nhánh feature. Không dùng `git reset --hard` hoặc viết lại lịch sử nhánh dùng chung để phục hồi. Có thể bỏ nhánh task chưa merge hoặc revert commit task; nhánh feature và commit đã duyệt vẫn khôi phục được.

### Gate G0 — Phê duyệt trước triển khai

Chủ dự án/người hướng dẫn phải ghi nhận phê duyệt SRS Draft, ngày thông qua constitution, phê duyệt plan đã hoàn tất và đúng phiên bản tài liệu nguồn Project 12 như ghi tại OQ-002 trong `spec.md`. Các quyết định dataset/giấy phép, ground truth thời gian, ngưỡng quyết định và consent/đạo đức phải được giải quyết hoặc giao chủ sở hữu cụ thể, nêu ảnh hưởng chặn. Trước G0, danh sách task này không cho phép sửa code ứng dụng. Đây là gate phê duyệt, không phải quyền để coding agent tự đặt ra quyết định còn thiếu.

## Phase 1 — Nền tảng dự án

**Kết quả mốc:** Môi trường được xác minh, quy ước dự án, tiền đề thiết kế/protocol được duyệt và nền tảng dữ liệu/tài liệu an toàn.

- [X] **T-001 — Xác minh tiền đề triển khai và gate phê duyệt** (Research/Planning)
  - **Phase/Priority:** Phase 1, Gate G0 / P0.
  - **Phụ thuộc:** Không.
  - **Yêu cầu:** NFR-005–NFR-007; DR-001, DR-004–DR-007; RA-005; SRS OQ-001, OQ-002, OQ-005–OQ-009.
  - **Mục tiêu:** Ghi dữ kiện môi trường và nhận các phê duyệt của con người cần thiết trước khi sửa code hoặc xử lý dữ liệu người tham gia.
  - **Các bước:** Rà `specs/001-drowsyalert/spec.md`, `.specify/memory/constitution.md`, `specs/001-drowsyalert/plan.md`, `docs/reference/PhieuMoTaDeTai_30DeTai_ThiGiacMayTinh_NCKH.docx` và ứng dụng hiện tại. Xác nhận phê duyệt SRS, ngày thông qua constitution, phiên bản DOCX chính thức, phê duyệt plan đã hoàn tất, dataset/giấy phép, protocol ground-truth thời gian và hướng dẫn người tham gia/đạo đức. Ghi mục chưa giải quyết; không tự chọn ngầm.
  - **Artifact:** Hồ sơ phê duyệt/quyết định tại `specs/001-drowsyalert/decisions.md` hoặc hồ sơ review được duyệt; ngày thông qua constitution; `plan.md` được chủ dự án duyệt.
  - **Xác minh/hoàn tất:** Reviewer xác nhận từng mục G0 đã được duyệt kèm bằng chứng hoặc hoãn rõ người phụ trách và tác động chặn; plan chi tiết được duyệt và quyết định protocol được ghi nhận. Trước khi hoàn tất, task triển khai bị chặn; chỉ được kiểm tra môi trường ở chế độ chỉ đọc.

#### Task con T-001 — Thẩm quyền G0 và hồ sơ quyết định

Chỉ hoàn tất T-001 khi mọi task con dưới đây được đánh dấu. Phê duyệt phải do chủ dự án/người hướng dẫn được nêu thực hiện; agent không được suy luận rồi tự đánh dấu.

- [X] **T-036 [T-001]:** Kiểm kê SRS, constitution, plan, nguồn chính thức dự kiến và quyết định nghiên cứu còn mở trong `decisions.md`.
- [X] **T-037 [T-001]:** Ghi người phụ trách, ảnh hưởng chặn, định danh file nguồn và quyết định baseline Git an toàn trong `decisions.md` (phụ thuộc T-036).
- [X] **T-038 [T-001]:** Ghi phê duyệt của chủ dự án/người hướng dẫn cho SRS Draft và plan chi tiết (phụ thuộc T-037; cần con người).
- [X] **T-039 [T-001]:** Ghi thông qua Constitution v1.0.0 và ngày phê chuẩn trong constitution và `decisions.md` (phụ thuộc T-037; cần con người).
- [X] **T-040 [T-001]:** Xác nhận DOCX Project 12 hiện có, không hậu tố, có phải phiên bản chuẩn không và ghi kết quả (phụ thuộc T-037; cần con người).
- [X] **T-041 [T-001]:** Review/duyệt người phụ trách và ảnh hưởng chặn của các quyết định dataset, ground truth thời gian, metric, ngưỡng, consent và baseline Git (phụ thuộc T-038–T-040; cần con người).
- [X] **T-051 [T-001]:** Giữ migration root đã review tại `3f717de`, không đổi `master`, tạo `feature/001-drowsyalert` từ checkpoint (phụ thuộc T-041; chủ dự án duyệt).

- [X] **T-002 — Kiểm toán và ghi nhận môi trường hiện tại** (Coding/Environment; P0; không đổi source/dependency trước G0).
  - **Yêu cầu:** NFR-002–NFR-003, NFR-005; RA-006.
  - **Mục tiêu/các bước:** Tạo baseline tái lập cho môi trường runtime/phát triển. Từ root, ghi phiên bản Python/`uv`, OS/platform, trạng thái lock dependency, hỗ trợ CNN tùy chọn đã cài, tài nguyên webcam/video test và sự hiện diện của model/data cần thiết. Phân biệt dữ kiện quan sát được với khả năng dự kiến.
  - **Artifact:** `docs/project/environment-audit.md` hoặc vị trí được plan duyệt.
  - **Xác minh/hoàn tất:** Reviewer tái lập được kiểm tra phiên bản/asset; không ghi credential, video cá nhân hay định danh máy không cần thiết; ghi tiền đề còn thiếu/giới hạn mà không đổi hành vi app.

#### Task con T-002 — Kiểm toán môi trường

Thực hiện theo thứ tự; hoàn tất khi đủ bốn task con.

- [X] **T-032 [T-002]:** Ghi Python, `uv`, hệ điều hành và platform vào `docs/project/environment-audit.md`.
- [X] **T-033 [T-002]:** Ghi trạng thái lock/dependency và môi trường PyTorch tùy chọn (phụ thuộc T-032).
- [X] **T-034 [T-002]:** Kiểm kê model/data và fixture video không cá nhân; ghi asset thiếu, không tải dữ liệu hoặc quay webcam (phụ thuộc T-033).
- [X] **T-035 [T-002]:** Rà tính tái lập, bỏ chi tiết định danh máy không cần thiết và xác minh mỗi dữ kiện có lệnh/nguồn tái lập (phụ thuộc T-034).

- [X] **T-003 — Rà dependency và bố cục dự án theo thiết kế đã duyệt** (Coding/Environment; P1).
  - **Phụ thuộc:** T-001 để đối chiếu thiết kế; T-002 để có dữ kiện môi trường.
  - **Yêu cầu:** NFR-005, NFR-006; RA-006.
  - **Mục tiêu/các bước:** Chỉ tìm khoảng trống dependency/bố cục cần cho yêu cầu đã duyệt; tránh nhân đôi module. So plan với `pyproject.toml`, `src/drowsyalert/`, `tests/`, `README.md`; phân biệt cái đã có với cái đã xác minh. Chỉ đề xuất dependency khi có yêu cầu cụ thể và căn cứ trong plan.
  - **Artifact:** Ghi chú rà dependency/bố cục trong audit hoặc vị trí plan duyệt; chỉ đổi dependency hẹp nếu plan yêu cầu.
  - **Xác minh/hoàn tất:** Mỗi đề xuất gắn SPEC ID và lý do nền tảng/cài đặt; reviewer duyệt danh sách khoảng trống/quyết định trước triển khai.

#### Task con T-003 — Rà dependency và bố cục

- [X] **T-042 [T-003]:** So bố cục root đã duyệt với `pyproject.toml`, `src/drowsyalert/`, `scripts/`, `tests/`, README và ghi audit.
- [X] **T-043 [T-003]:** Ánh xạ dependency runtime, CNN, huấn luyện, phát triển với import quan sát được và trách nhiệm trong plan (phụ thuộc T-042).
- [X] **T-044 [T-003]:** Ghi asset/module experiment-test/tài liệu lệch ngôn ngữ/cấu hình tạm còn thiếu mà không đổi dependency (phụ thuộc T-043).
- [X] **T-045 [T-003]:** Rà khoảng trống Phase 1 và ghi nhận hiện chưa có căn cứ đổi dependency/bố cục (phụ thuộc T-044).

- [X] **T-004 — Thiết lập quy ước cấu hình, test và xử lý dữ liệu** (P0; phụ thuộc T-001, T-003).
  - **Yêu cầu:** FR-018–FR-020; NFR-005–NFR-007; DR-004–DR-007.
  - **Mục tiêu/các bước:** Làm rõ cấu hình, tổ chức test, provenance lượt chạy và ranh giới dữ liệu riêng tư. Đối chiếu config/test với plan; quy định nơi đặt test, cách ghi ngưỡng/cấu hình theo lượt chạy, đường dẫn dữ liệu/model/output riêng tư và lưu hồ sơ consent/provenance mà không commit video người tham gia.
  - **Artifact:** Cập nhật architecture hoặc tài liệu quy ước; chỉ sửa `.gitignore` nếu chính sách dữ liệu duyệt yêu cầu; sơ đồ test.
  - **Xác minh/hoàn tất:** Đường dẫn/chính sách rõ, kiểm tra trạng thái repo với đường dẫn dữ liệu giả xác nhận bị loại; reviewer duyệt quy ước; không tạo/đưa dữ liệu người thật vào task này.

#### Task con T-004 — Quy ước dự án

- [X] **T-046 [T-004]:** Ghi yêu cầu config được theo dõi, validation, path và cấu hình đã phân giải vào `development-conventions.md`.
- [X] **T-047 [T-004]:** Ánh xạ hành vi chính tới module test hiện có/dự kiến (phụ thuộc T-046).
- [X] **T-048 [T-004]:** Ghi ranh giới dữ liệu, model, output, consent và provenance (phụ thuộc T-046).
- [X] **T-049 [T-004]:** Ghi quy trình nhánh task và phục hồi không phá hủy (phụ thuộc T-046).
- [X] **T-050 [T-004]:** Dùng `git check-ignore` xác minh đường dẫn dữ liệu riêng tư, checkpoint, kết quả sinh bị loại và ghi nhận kết quả (phụ thuộc T-048).

### Gate nghiệm thu Phase 1

G1 đạt khi T-001–T-004 hoàn tất; có kiến trúc/protocol được duyệt; hiểu dependency, quy ước test và ranh giới dữ liệu/quyền riêng tư. Không huấn luyện model hoặc thu tình nguyện viên trước phê duyệt/kiểm tra giấy phép, consent tương ứng.

**G1 (2026-10-26): Đạt.** T-001–T-004 và task con Phase 1 hoàn tất. Điều kiện dataset, huấn luyện, dữ liệu tình nguyện viên và đánh giá vẫn là blocker tường minh cho task sau.

## Phase 2 — Landmark và PERCLOS baseline

**Kết quả mốc:** Luồng quan sát webcam/video cục bộ xác định, bằng chứng mắt từ landmark hợp lệ, PERCLOS theo timestamp và xử lý mất quan sát đã kiểm thử.

- [X] **T-052 [Phase 2]:** Chia T-005–T-009 thành task con review độc lập cho source, validity, EAR, temporal và integration.

- [X] **T-005 — Xác minh/hoàn thiện đầu vào webcam/video** (P0; phụ thuộc G1, T-004).
  - **Yêu cầu:** FR-001, FR-002, FR-017; NFR-004. Làm rõ nguồn trực tiếp/ghi sẵn cục bộ, timestamp, dừng và xử lý lỗi.
  - **Các bước:** Rà `source.py` và tests; giữ hành vi hợp lệ, xử lý lỗi mở, EOF, ngắt camera, thời gian capture live tăng đơn điệu, timestamp media, cleanup và dừng. Thêm test tập trung với source giả và fixture không cá nhân được duyệt nếu có.
  - **Artifact/xác minh:** `source.py`, `test_source.py`; test bao phủ camera/video, input không khả dụng, EOF/ngắt, timestamp và cleanup mà CI không cần webcam thật. Hai mode có ngữ nghĩa thời gian được ghi rõ; lỗi không tái dùng frame cũ.

#### Task con T-005 — Input và timestamp

- [X] **T-053 [T-005]:** Thêm test capture giả cho lỗi mở, EOF video, lỗi camera, cleanup, loại source và fallback timestamp.
- [X] **T-054 [T-005]:** Triển khai source kind/timebase tường minh và timestamp live/media tăng đơn điệu đã xác minh (phụ thuộc T-053).
- [X] **T-055 [T-005]:** Chạy test source/Ruff tập trung, ghi hoàn tất T-005 trong checklist chuẩn (phụ thuộc T-054).

- [X] **T-006 — Xác minh tính hợp lệ khuôn mặt/landmark/vùng mắt** (P0; phụ thuộc T-005, G1).
  - **Yêu cầu:** FR-003, FR-004, FR-015–FR-017. Bảo đảm quan sát landmark một người và crop mắt được xác định hợp lệ hoặc unknown.
  - **Các bước:** Rà `face.py`, `types.py`, `test_detection.py`; thêm test không có mặt, landmark sai/nằm ngoài frame, vùng mắt thiếu, che khuất/không chắc và nhiều mặt mơ hồ. Không trộn tín hiệu của người khác; tuân theo plan về chọn hay từ chối quan sát.
  - **Artifact/xác minh:** file detection/type hiện hữu và `test_detection.py`; fixture tổng hợp bao phủ ranh giới đúng/sai; không mặt/nhiều mặt không thể trở thành quan sát mắt mở.

#### Task con T-006 — Khuôn mặt và validity từng mắt

- [X] **T-056 [T-006]:** Test không mặt, mơ hồ nhiều mặt, landmark sai, mắt ngoài frame/suy biến và validity độc lập từng mắt.
- [X] **T-057 [T-006]:** Bổ sung validity từng mắt tường minh và crop/box/EAR nullable trong `FaceObservation` (phụ thuộc T-056).
- [X] **T-058 [T-006]:** Triển khai chọn không mặt/nhiều mặt và xác thực riêng từng mắt; điều chỉnh consumer trình bày/log nếu cần (phụ thuộc T-057).
- [X] **T-059 [T-006]:** Chạy test detection/Ruff tập trung và ghi hoàn tất T-006 (phụ thuộc T-058).

- [X] **T-007 — Định nghĩa và test ước lượng trạng thái mắt từ landmark** (P0; phụ thuộc T-006 và định nghĩa nhắm mắt được duyệt G0).
  - **Yêu cầu:** FR-006, FR-015; NFR-001; RA-002, RA-004. Tạo trạng thái landmark-only mở/nhắm/unknown cho câu hỏi PERCLOS chính.
  - **Các bước:** Trong `ear.py`/module feature được duyệt, triển khai hoặc đối chiếu phép đo landmark mắt 2D và luật quyết định mở/nhắm; tách biệt CNN. Test hai mắt, một mắt/nháy nếu quy định, biên ngưỡng, hình học sai và bằng chứng unknown.
  - **Artifact/xác minh:** module EAR và test tập trung; fixture xác định kiểm tra mở/nhắm/biên/sai; ghi luật/ngưỡng trong config; nguồn EAR landmark kiểm thử độc lập và có định danh riêng.

#### Task con T-007 — Trạng thái mắt landmark

- [X] **T-060 [T-007]:** Test bằng ngưỡng, nhắm hai mắt, một mắt mở hợp lệ, một mắt nhắm còn mắt kia sai và EAR sai.
- [X] **T-061 [T-007]:** Triển khai chính sách `OPEN`/`CLOSED`/`UNKNOWN` bilateral landmark-EAR đã duyệt và định danh nguồn (phụ thuộc T-060).
- [X] **T-062 [T-007]:** Chạy test trạng thái mắt/Ruff và ghi hoàn tất T-007 (phụ thuộc T-061).

- [X] **T-008 — Xác minh PERCLOS theo timestamp và ngữ nghĩa mất tracking** (P0; phụ thuộc T-005, T-007, temporal policy G0).
  - **Yêu cầu:** FR-007, FR-015; NFR-004, NFR-006; RA-002. Tính PERCLOS trên thời lượng quan sát hợp lệ, báo coverage/readiness; không tính khoảng trống là mở hoặc nhắm.
  - **Các bước:** Rà `temporal.py` và test; khớp cửa sổ, coverage, gap, closure, timestamp và unknown với protocol; giữ trọng số timestamp và test lấy mẫu lệch, cắt biên, khoảng unknown, coverage thiếu và timestamp sai/không tăng.
  - **Artifact/xác minh:** `temporal.py`, test và tài liệu protocol/config; chuỗi timestamp tính tay khớp closed/valid duration; gap giảm coverage hợp lệ, không thành quan sát mắt mở.

#### Task con T-008 — Hành vi thời gian theo timestamp

- [X] **T-063 [T-008]:** Test xác định khoảng lệch, cắt cửa sổ, loại unknown/gap, reset nhắm mắt, timestamp sai, readiness, source và metadata cửa sổ.
- [X] **T-064 [T-008]:** Hoàn thiện metadata source/window và hành vi interval trong `temporal.py`/`types.py` (phụ thuộc T-063).
- [X] **T-065 [T-008]:** Chạy test temporal/Ruff tập trung, ghi hoàn tất T-008 (phụ thuộc T-064).

- [X] **T-009 — Gate tích hợp baseline landmark/PERCLOS** (P0; phụ thuộc T-005–T-008).
  - **Yêu cầu:** FR-001–FR-004, FR-006–FR-007, FR-015–FR-017; NFR-004; RA-002. Xác minh baseline đầu-cuối trên input lặp lại được trước CNN/tính năng thêm.
  - **Các bước:** Chỉ nối source, quan sát mặt, trạng thái mắt landmark, PERCLOS thời gian và status trong `realtime.py` khi cần. Thêm integration test xác định; ghi riêng webcam thủ công.
  - **Artifact/xác minh:** `realtime.py`, `test_pipeline.py`, `verification.md`; replay tự động xác nhận state/PERCLOS/unknown và timestamp; kiểm tra webcam thủ công ghi môi trường/kết quả, không tuyên bố hiệu năng tổng quát.

#### Task con T-009 — Gate tích hợp baseline

- [X] **T-066 [T-009]:** Thêm integration test source/detector giả xác định bao phủ valid, unknown và replay có timestamp.
- [X] **T-067 [T-009]:** Hoàn thiện metadata nguồn landmark/timebase/window/coverage; giữ replay offline im lặng (phụ thuộc T-066).
- [X] **T-068 [T-009]:** Ghi bằng chứng replay tự động và kiểm tra webcam/model/thủ công chưa khả dụng; không tuyên bố test phần cứng bị bỏ qua là đạt (phụ thuộc T-067).
- [X] **T-069 [T-009]:** Chạy test/lint Phase 2, cập nhật requirement evidence và G2, đánh dấu T-009 (phụ thuộc T-068).
- [X] **T-070 [Phase 2]:** Chạy suite/Ruff cuối Phase 2, xác nhận task con T-005–T-009 hoàn tất, sửa lỗi format/diff trước merge.

### Gate nghiệm thu Phase 2

G2 đạt khi T-005–T-009 xong; input ghi lại tái lập được; trạng thái mắt landmark và PERCLOS truy vết riêng; gap/input sai vẫn unknown; unit/integration test đạt. Gate này không đưa ra tuyên bố Accuracy CNN.

**G2 (2026-10-26): Đạt cho tiến độ code tự động.** Suite có 41 passed, 1 optional-CNN skip; Ruff đạt. Webcam vật lý, asset Face Landmarker thật, codec video thật và âm thanh vẫn chưa xác minh, được ghi rõ trong `verification.md`.

## Phase 3 — Phân loại mắt bằng CNN

**Kết quả mốc:** Pipeline dữ liệu ảnh mắt hợp pháp, hạn chế leakage; classifier được huấn luyện; metric held-out độc lập; tích hợp suy luận CNN tường minh.

- [X] **T-071 [Phase 3]:** Chia T-010–T-014 thành task dataset, preparation, training, evaluation và inference có thể review riêng.
- [X] **T-010 — Chọn và ghi tài liệu dataset/split trạng thái mắt** (Research/Data)
  - **Phase/Priority/Phụ thuộc:** Phase 3 / P0 / G1, T-004.
  - **Yêu cầu:** DR-001–DR-003, DR-005–DR-007; NFR-006–NFR-007; RA-004–RA-005.
  - **Mục tiêu/các bước:** Thiết lập dataset được phép và nhãn open/closed tái lập được, không giả định một dataset cụ thể có thể truy cập. Nghiên cứu nguồn ảnh mắt công khai gồm nguồn Kaggle do giảng viên nêu; xác minh access, license/terms, version, provenance, định nghĩa nhãn, ID subject/session và suitability. Chỉ chọn sau review; thiết kế train/validation/test theo subject/session khi có thể và ghi giới hạn leakage. Không tải/commit dữ liệu hạn chế/cá nhân.
  - **Artifact/xác minh/hoàn tất:** `data/README.md`, dataset card, manifest split hoặc quy trình tạo tại nơi private/derived-data được duyệt. Reviewer kiểm tra nguồn/version/ngày lấy/license/nhãn/split và held-out không chung subject/session/frame gần trùng khi metadata cho phép. Dataset phải được duyệt; nếu không có dataset hợp pháp phù hợp thì ghi blocker/alternative, không bịa availability.

#### Task con T-010 — Thẩm quyền dataset và protocol split

- [X] **T-072 [T-010]:** Audit dataset ứng viên, terms access, provenance, nhãn, metadata identity và leakage risk trong dataset card; loại nguồn không có bằng chứng quyền dùng.
- [X] **T-073 [T-010]:** Thay automatic Kaggle downloader không rõ license bằng acquisition verifier an toàn, không tải/phân phối lại dữ liệu ngầm (phụ thuộc T-072).
- [X] **T-074 [T-010]:** Ghi nhận CEW được chọn: acquisition, bố cục local, nhãn, split, provenance và quy trình không phân phối lại trong `data/README.md`/dataset card (phụ thuộc T-072).
- [X] **T-075 [T-010]:** Kiểm tra CEW extraction do owner cung cấp, ghi hash source/version/file/count thật và duyệt manifest dữ liệu thật trước huấn luyện (phụ thuộc T-074; owner phải cung cấp dataset).

- [X] **T-011 — Chuẩn bị nhãn ảnh mắt và dataset loader**
  - **Priority/Phụ thuộc/Yêu cầu:** P1; T-010, G1; FR-005, DR-001–DR-003, DR-005–DR-007, NFR-006.
  - **Mục tiêu/các bước:** Tạo sample train/validation/test có nhãn open/closed rõ. Rà `dataset.py`, `prepare_dataset.py`, `test_cnn_dataset.py`; mở rộng loading/label mapping/validation với sample thiếu, mơ hồ, không dùng được; giữ dữ liệu thô riêng tư ngoài Git; ghi transformation/split identity.
  - **Artifact/xác minh/hoàn tất:** code loader/preparation, test và tài liệu dataset. Fixture tổng hợp chứng minh nhãn, loại trừ/split xác định/audit được; không assert statistic dữ liệu thật trước khi có dữ liệu. Sample chuẩn bị phải khớp mapping/split manifest và còn provenance.

#### Task con T-011 — Pipeline chuẩn bị có xác thực

- [X] **T-076 [T-011]:** Thêm test tổng hợp mapping label, sample bị loại, manifest schema, duplicate, group-disjoint split và output xác định trong `test_cnn_dataset.py` (phụ thuộc T-074).
- [X] **T-077 [T-011]:** Triển khai validation label/group/manifest nghiêm ngặt và preparation xác định chống leakage trong `dataset.py` (phụ thuộc T-076).
- [X] **T-078 [T-011]:** Cập nhật preparation CLI/provenance report với source identity, transformation, hash, split count, warning (phụ thuộc T-077).
- [X] **T-079 [T-011]:** Chạy suite preparation tổng hợp/Ruff, ghi assertion dữ liệu thật còn chờ T-075 (phụ thuộc T-078).

- [X] **T-012 — Huấn luyện và validation CNN trạng thái mắt**
  - **Priority/Phụ thuộc/Yêu cầu:** P1; T-011 và model/training choice plan đã duyệt; FR-005, NFR-001, NFR-005–NFR-006, RA-004–RA-005.
  - **Mục tiêu/các bước:** Huấn luyện classifier và chọn setting chỉ bằng train/validation. Rà `eye_cnn.py`, `train.py`, `train_model.py`; triển khai/đối chiếu training, validation, checkpoint metadata, seed xác định, class mapping. Không dùng test held-out để chọn model/ngưỡng.
  - **Artifact/xác minh/hoàn tất:** training code/script, checkpoint ở artifact location ignore, training guide, run metadata. Một run tổng hợp/mẫu được phép xác minh training/checkpoint; ghi identity train/validation, seed, setting, metric. Checkpoint tương thích sinh tái lập từ dữ liệu được duyệt và validation selection được ghi.

#### Task con T-012 — Huấn luyện/chọn model tái lập

- [X] **T-080 [T-012]:** Test config training xác định, chọn checkpoint validation-only, class mapping, checkpoint metadata (phụ thuộc T-079).
- [X] **T-081 [T-012]:** Triển khai loader/training xác định, chọn validation-only và metadata checkpoint/run đầy đủ (phụ thuộc T-080).
- [X] **T-082 [T-012]:** Chạy smoke test training/checkpoint tổng hợp nhỏ, không claim performance (phụ thuộc T-081).
- [X] **T-083 [T-012]:** Tài liệu command/config/artifact/selection rule/prerequisite dữ liệu thật tái lập trong training guide (phụ thuộc T-082).

- [X] **T-013 — Đánh giá phân loại mắt trên split test held-out**
  - **Priority/Phụ thuộc/Yêu cầu:** P0; T-012, split/model/decision rule đã khóa; NFR-001, NFR-006, RA-002, RA-004–RA-005.
  - **Mục tiêu/các bước:** Báo cáo performance phân loại ảnh open/closed không bias. Bổ sung evaluator; tính count test, Accuracy, confusion matrix, Precision/Recall/F1 từng lớp với định nghĩa averaging; ghi model/checkpoint identity và confidence/threshold policy. Chỉ đánh giá một chiều sau khi khóa selection.
  - **Artifact/xác minh/hoàn tất:** evaluator, `test_cnn_metrics.py`, kết quả machine-readable ở output ignore và summary docs. Metric qua test confusion-matrix đã biết; báo việc đạt Accuracy >=0.90 không ngụ ý bắt buộc phải đạt. Held-out/protocol phải audit được, không có data/result không sẵn có hoặc bịa.

#### Task con T-013 — Đánh giá held-out đã khóa

- [X] **T-084 [T-013]:** Test confusion matrix đã biết cho count, Accuracy, Precision/Recall/F1 từng lớp, macro F1, input empty/invalid (phụ thuộc T-081).
- [X] **T-085 [T-013]:** Triển khai evaluator held-out một chiều với checkpoint/manifest identity, threshold policy, output máy đọc được (phụ thuộc T-084).
- [X] **T-086 [T-013]:** Chấm checkpoint khóa một lần trên CEW test thật owner duyệt và ghi trạng thái Accuracy >=0.90 (phụ thuộc T-075, T-083, T-085; dataset/model đã xác minh).

- [X] **T-014 — Tích hợp suy luận CNN thành nguồn trạng thái mắt riêng**
  - **Priority/Phụ thuộc/Yêu cầu:** P1; T-007, T-009, T-012; T-013 cho performance claim; FR-004–FR-007, FR-015, FR-018, NFR-004, NFR-006.
  - **Mục tiêu/các bước:** Có suy luận CNN trong pipeline mà không lẫn với landmark. Rà `eye_cnn.py`/`realtime.py`; tích hợp confidence/uncertainty, output từng mắt, lỗi checkpoint thiếu, nguồn PERCLOS chọn được nếu duyệt và source label rõ trong log/config.
  - **Artifact/xác minh/hoàn tất:** model/pipeline change, `test_cnn_inference.py`, run schema/tài liệu cập nhật. Test valid/uncertain/invalid crop/checkpoint incompatible/missing/source identity; source chọn khớp nguồn PERCLOS ghi. CNN chọn độc lập, không ghi đè identity baseline landmark.

#### Task con T-014 — Bằng chứng CNN runtime riêng biệt

- [X] **T-087 [T-014]:** Test probability từng mắt, uncertainty config, bilateral policy, crop sai, checkpoint thiếu/không tương thích và source identity (phụ thuộc T-081).
- [X] **T-088 [T-014]:** Triển khai uncertainty CNN tường minh và hành vi trạng thái hai mắt (phụ thuộc T-087).
- [X] **T-089 [T-014]:** Tích hợp identity checkpoint/source/threshold CNN vào runtime/CSV, không đổi landmark baseline (phụ thuộc T-088).
- [X] **T-090 [Phase 3]:** Chạy suite/Ruff Phase 3; ghi code path hoàn tất, dataset blocker, G3 status không bịa result (code verification phụ thuộc T-085/T-089; G3 cuối phụ thuộc T-075/T-086).

### Gate Phase 3

G3 yêu cầu dataset có license/split được ghi, loader/huấn luyện được test, model tương thích, metric held-out và tích hợp CNN là bằng chứng riêng. Nếu quyền truy cập chặn thì không tuyên bố Accuracy. **G3 (2026-10-26): Đạt.** CEW có 3.392 train, 726 validation, 728 test; chọn epoch 34 từ validation; test một lần cho Accuracy 0.907967, macro F1 0.907904. Chỉ là phân loại ảnh, không phải hiệu năng video.

## Phase 4 — Cảnh báo buồn ngủ thời gian thực

**Kết quả mốc:** Quyết định nhắm mắt/PERCLOS cấu hình được, trạng thái hiển thị, cảnh báo âm thanh có kiểm soát và luồng trực tiếp được kiểm thử.

- [X] **T-091 [Phase 4]:** Chia T-015–T-018 thành task decision, presentation, audio, integration, asset và manual verification độc lập.
- [X] **T-015 — Hoàn thiện/test luật quyết định cấu hình được** (P0; G2, T-008, ngưỡng/cửa sổ G0; FR-007–FR-008, FR-012, FR-015). Triển khai/xác minh baseline Method A PERCLOS/nhắm kéo dài, normal/alert/unknown; đối chiếu threshold, warm-up/coverage, reason, unknown và parameter validation với protocol. Artifact decision/config/test; test dưới/tại/trên ngưỡng, closure ngắn/dài, coverage thiếu/unknown; unknown không thành normal mặc định, B/C để T-021.
- [X] **T-092 [T-015]:** Test mắt unknown, warm-up/coverage, PERCLOS thiếu, ngưỡng, closure và evidence không hữu hạn. **T-093:** triển khai priority/reason `NORMAL`/`ALERT`/`UNKNOWN`. **T-094:** xác thực config threshold/window và serialize resolved run. **T-095:** chạy test decision/config/Ruff, ghi Method A; B/C còn deferred T-021.
- [X] **T-016 — Xác minh trạng thái/trình bày cảnh báo** (P1; T-015; FR-012–FR-013, FR-015). Hiển thị rõ availability, status/reason/advisory; phân biệt normal, warning, unknown, input/camera lỗi, warm-up/unavailable; warning không được mô tả là đảm bảo an toàn. **T-096:** test presentation. **T-097:** refactor summary/overlay status-reason-advisory. **T-098:** cập nhật README trạng thái, stop/mute, privacy, limit. **T-099:** test overlay/Ruff và ghi xác minh.
- [X] **T-017 — Xác minh âm thanh và điều khiển phát lặp** (P1; T-015; FR-014, FR-020). Phát cảnh báo live, giới hạn repeat; kiểm tra async/nonblocking, cooldown/repeat, recovery/stop, file thiếu, mute, metadata. **T-100:** test injected audio cho alert/re-alert/mute/lỗi/close. **T-101:** state availability/enabled/active/result, cooldown nonblocking. **T-102:** metadata enabled/available/play/failure và policy. **T-103:** test/Ruff; loa thật là hardware check.
- [ ] **T-018 — Xác minh toàn bộ luồng webcam live** (P0; T-005–T-009, T-015–T-017, T-014 nếu CNN). Demo local đầu-cuối/failure handling; test integration/replay, demo webcam phần cứng, ghi model/asset/config/unknown/reason/stop-mute/camera loss. Artifact: test, verification, evidence không cá nhân. Không gọi kết quả giả/simulated là webcam thật. **T-104:** test live/replay giả. **T-105:** xác minh CLI/config/source/checkpoint/audio metadata. **T-106:** checklist/evidence webcam-audio thật. **T-107:** xác minh Face Model/provenance/hash không commit. **T-108:** suite/Ruff, privacy boundary, G4/blocker phần cứng.

## Phase 5 — Tính năng nghiên cứu bổ sung

**Kết quả mốc:** Tín hiệu phụ có validity/unknown; A/B/C dùng chung baseline và identity truy vết được.

- [X] **T-109 [Phase 5]:** Chia T-019–T-022 thành task yawn, pose, method isolation, experiment record, documentation và verification.
- [X] **T-019 — Triển khai/test trích xuất ngáp** (P1; G2, T-006, T-008, định nghĩa ngáp G0; FR-009, FR-011–FR-012, FR-015). Phát hiện event ngáp theo thời gian cho B từ quan sát miệng hợp lệ; kiểm tra mouth geometry, duration/reset, dedup, rolling count, unknown. **T-110:** test MAR/boundary/dedup/close-gap-expiry. **T-111:** triển khai yawn valid/unknown và temporal state. **T-112:** ghi rule ngáp provisional, test/Ruff, hoàn tất.
- [X] **T-020 — Triển khai/test head pose** (P1; G2, T-006, T-008, pose reference G0; FR-010–FR-012, FR-015). Ước lượng pose cho C; xử lý validity/reference/sign/sustained duration/gap-reset/unknown; không giả định neutral/calibration chưa duyệt. **T-113:** test pose. **T-114:** triển khai validity/reference/relative pitch/reset. **T-115:** ghi rule provisional, test/Ruff.
- [X] **T-021 — Chuẩn hóa config/provenance A/B/C** (P0; T-015, T-019, T-020, protocol PERCLOS G0; FR-011–FR-012, FR-018–FR-019). A/B/C chỉ khác auxiliary feature/rule đã duyệt; ghi method ID/common/feature setting/eye source/evidence; test A bỏ cue, B chỉ yawn, C chỉ pose. **T-116:** decision/integration test isolation. **T-117:** chuẩn hóa ID/validity/reason/config snapshot/provenance. **T-118:** matrix config, test/Ruff.
- [X] **T-022 — Hợp đồng thực thi/ghi kết quả experiment** (P0; T-013, T-021; FR-018–FR-020). Ghi input/output đủ tái lập/audit: run ID, dataset/split, timestamp, method/eye source, setting/threshold, seed/model/audio, evidence/unknown, output/environment; path private ignored. **T-119:** schema/validation/ID/JSON/CSV/no raw-frame test. **T-120:** metadata/frame export có version. **T-121:** provenance headless runtime/export/schema. **T-122:** suite/Ruff/privacy audit/G5, không claim webcam/audio physical đạt.

## Phase 6 — Đánh giá thực nghiệm

**Kết quả mốc:** Dữ liệu đánh giá hợp pháp, có consent khi cần và nhãn theo thời gian; protocol được khóa; kết quả A/B/C tái lập được, phân tích độ trễ/lỗi và giới hạn minh bạch.

- [X] **T-123 [Phase 6]:** Kiểm toán mức sẵn sàng Phase 6, chỉ chia task protocol T-023 trước công việc dataset/chấm điểm; giữ phụ thuộc phần cứng T-018/T-022 và thiếu corpus video thời gian làm blocker tường minh.
- [X] **T-133 [Phase 6]:** Chạy toàn bộ suite/Ruff sau nền tảng annotation/metric độc lập dữ liệu; ghi 176 test đạt, trong khi phê duyệt protocol, thu video và chấm thật còn chờ.
- [X] **T-134 [Phase 6]:** Kiểm toán corpus NITYMED HDTV720 đã thu nhận, chia T-024–T-027 thành task dữ liệu, metric, evaluator và controlled run có thể phục hồi; không coi thư mục category là ground truth thời gian.

- [X] **T-023 — Duyệt ground truth thời gian và protocol đánh giá** (Research)
  - **Priority/Phụ thuộc:** P0; G0, T-021, T-022.
  - **Yêu cầu:** DR-003, DR-005–DR-008; NFR-006–NFR-007; RA-001–RA-005.
  - **Mục tiêu:** Khóa nhãn sự kiện, ghép sự kiện, onset, mẫu số báo giả và protocol split trước khi chấm test.
  - **Các bước:** Ghi đơn vị nhãn tham chiếu, quy tắc onset/offset, quy trình annotation/adjudication độc lập, tolerance ghép, mẫu số mỗi video/thời gian, xử lý coverage/overlap unknown và split người/phiên. Xin duyệt người hướng dẫn và hướng dẫn ethics cho volunteer.
  - **Artifact/xác minh/hoàn tất:** `evaluation-protocol.md` và hồ sơ duyệt có phiên bản; reviewer xác nhận A/B/C dùng cùng video/nhãn/timestamp đủ điều kiện và ngưỡng chỉ chọn trên train/validation. Protocol phải được khóa/ngày hóa trước test; annotation/ethics chưa giải quyết chặn claim bị ảnh hưởng.

#### Task con T-023 — Protocol đánh giá đã khóa

- [X] **T-124 [T-023]:** Audit nguồn video thời gian công khai và dữ liệu cục bộ cho license, access, identity người/phiên, thời điểm sự kiện và nhãn điều kiện; không tải hay tuyên bố có dataset.
- [X] **T-125 [T-023]:** Soạn protocol với đơn vị annotation, onset/offset, validation/test, ghép alert một-một, latency, mẫu số false alarm, coverage unknown, phân tích điều kiện, kiểm soát A/B/C và trường phê duyệt (phụ thuộc T-124).
- [X] **T-126 [T-023]:** Nhận/ghi phê duyệt chủ dự án/người hướng dẫn cho data path, phiên bản protocol, định nghĩa event/matching, luật khóa ngưỡng và ethics volunteer; chỉ đánh dấu T-023 sau đó (phụ thuộc T-129; cần người duyệt).
- [X] **T-127 [T-023]:** Thêm test tổng hợp cho schema annotation, biên media, ID ổn định, trạng thái adjudication cuối, từ chối nhãn vòng tròn và leakage split người/phiên.
- [X] **T-128 [T-023]:** Triển khai loader/validator annotation thời gian độc lập dữ liệu và identity manifest ổn định; không tự duyệt dataset/protocol (phụ thuộc T-127).
- [X] **T-129 [T-023]:** Công bố template/hợp đồng trường CSV, chạy test/Ruff, ghi annotation thật còn bị chặn bởi T-126/T-024 (phụ thuộc T-128).

- [ ] **T-024 — Thu nhận/chuẩn bị video đánh giá có annotation và nhãn điều kiện** (Research/Data)
  - **Priority/Phụ thuộc:** P0; T-001, T-010, T-023.
  - **Yêu cầu:** DR-003–DR-008; NFR-006–NFR-007; RA-003, RA-005.
  - **Mục tiêu:** Có video có nhãn thời gian hợp pháp, consent khi áp dụng, để đánh giá alert.
  - **Các bước:** Review nguồn công khai và/hoặc thu volunteer chỉ với consent/hướng dẫn cơ quan đã duyệt. Ghi nguồn/license, ID phiên/người, điều kiện capture, nhãn/provenance annotation. Chỉ annotate kính/ánh sáng/head movement nếu quan sát được. Giữ video riêng tư ngoài Git theo access/retention được duyệt.
  - **Artifact/xác minh/hoàn tất:** `data/README.md`, vị trí dataset hạn chế, manifest nhãn/split có phiên bản, hồ sơ consent/provenance. Audit xác nhận quyền, coverage nhãn, tách split và không có file riêng tư trong Git; chỉ báo số lượng sau khi thật sự thu nhận. Corpus được duyệt hoặc task bị block có ghi khoảng trống dữ liệu/quyền, không được giả định data sẵn có.

#### Task con T-024 — Chuẩn bị corpus NITYMED

- [X] **T-135 [T-024]:** Thêm test tổng hợp cho hợp đồng video-manifest bảo vệ riêng tư, hash/ID xác định, metadata media, category path hỗ trợ, phát hiện trùng và giá trị subject/split unknown rõ ràng.
- [X] **T-136 [T-024]:** Triển khai inventory/manifest builder NITYMED chỉ đọc và CLI kiểm tra giải mã MP4, ghi relative path, category nguồn, duration/FPS/resolution, hash nội dung, provenance và grouping chưa giải quyết; không sao chép frame (phụ thuộc T-135).
- [X] **T-137 [T-024]:** Chạy inventory trên HDTV720, lưu manifest/worklist local bị ignore, công bố dataset card theo dõi có count thật, integrity, license/source, ngày lấy và sai khác count nhà cung cấp (phụ thuộc T-136).
- [X] **T-138 [T-024]:** Thêm worklist/tool annotation review do người thực hiện, ghi interval media-time độc lập theo schema đã duyệt và không nâng detector output thành ground truth (phụ thuộc T-137).
- [X] **T-150 [T-024]:** Sửa annotation reviewer để mở frame đầu ở trạng thái pause và phát theo FPS thật, giúp reviewer xem/gán nhãn tin cậy.
- [X] **T-151 [T-024]:** Ghi amendment Protocol v1.1 do owner duyệt: split xác định cân bằng 38 clip, khóa clip pilot đã xem vào validation và buộc công khai khả năng leakage người tham gia.
- [X] **T-152 [T-024]:** Test chọn category cân bằng/xác định, membership validation khóa, count 6+6/13+13, isolation clip/hash và identity split ổn định.
- [X] **T-153 [T-024]:** Triển khai split builder clip có phiên bản và CLI cục bộ dựa NITYMED manifest (phụ thuộc T-152).
- [X] **T-154 [T-024]:** Sinh/audit split 38 clip, annotation worklist, batch review, hash ổn định bị ignore; giữ bốn hàng pilot đã review (phụ thuộc T-153).
- [ ] **T-139 [T-024]:** Xác thực annotation cuối, isolation clip validation/test, condition tags, công khai thiếu participant mapping và manifest hash; giữ T-024 bị chặn nếu review timing sự kiện độc lập chưa xong (phụ thuộc T-126, T-154; cần người review).

- [X] **T-025 — Triển khai/unit-test metric đánh giá video/thời gian** (P1; T-023, T-022)
  - **Yêu cầu:** FR-019; NFR-001, NFR-006; RA-002–RA-004.
  - **Mục tiêu/các bước:** Tính riêng metric phân loại mắt và alert video/sự kiện theo định nghĩa công bố. Trong `experiments/`, xử lý Accuracy/confusion/class metric, score event/interval, false alarm mỗi đơn vị thời gian, misses, coverage/loss và điều kiện nhóm; fixture count đã biết, trường hợp empty/unknown tường minh.
  - **Artifact/xác minh/hoàn tất:** module metric, `test_experiment_metrics.py`, tài liệu định nghĩa. Fixture tính tay khớp giá trị, test bảo đảm count ảnh không bị dùng cho alert thời gian; metric/mẫu số được ghi, test và truy vết protocol.

#### Task con T-025 — Primitive metric sự kiện có tham số

Các task này có thể làm trên input tổng hợp trước T-023 vì tolerance/mẫu số là tham số rõ ràng; chúng không khóa protocol nháp, không hoàn tất T-025 hoặc cấp quyền chấm held-out.

- [X] **T-130 [T-025]:** Test tính tay cho ghép tuần tự một-một, biên early/late, alert giả, miss, latency có dấu, mẫu số 0 và coverage.
- [X] **T-131 [T-025]:** Triển khai xác thực interval có tham số, ghép event, event metric, tổng hợp latency/coverage (phụ thuộc T-130).
- [X] **T-132 [T-025]:** Tài liệu primitive metric nháp, test/Ruff; giữ T-025 pending T-023 (phụ thuộc T-131).
- [X] **T-140 [T-025]:** Test tính tay extraction alert episode, system Accuracy bin cố định giữ UNKNOWN trong mẫu số chính, chẩn đoán observed-only và nhóm điều kiện.
- [X] **T-141 [T-025]:** Triển khai episode, system-Accuracy và grouped metric theo protocol, không nhúng ngưỡng chưa duyệt (phụ thuộc T-140).
- [X] **T-142 [T-025]:** Đồng bộ tài liệu metric với protocol được duyệt, chạy focused/full verification và chỉ hoàn tất T-025 sau khi T-126 khóa định nghĩa (phụ thuộc T-126, T-141).

- [X] **T-026 — Đo latency alert và tình huống lỗi** (P1; T-023–T-025)
  - **Yêu cầu:** FR-017–FR-019; NFR-002, NFR-004, NFR-006; RA-003.
  - **Mục tiêu/các bước:** Đo delay onset-to-alert, false alarm, miss và gián đoạn quan sát. Tính latency từ onset tham chiếu/timestamp alert được duyệt; sự kiện bỏ lỡ là miss, chỉ báo phân phối latency cho event phát hiện kèm số miss; ghi điều kiện input/xử lý. Khi có ví dụ, đánh giá không mặt, mất tracking, kính, ánh sáng yếu, head movement, camera interruption, dự đoán không chắc.
  - **Artifact/xác minh/hoàn tất:** evaluator latency/lỗi, `test_alert_latency.py`, bảng/plot ở output ignore. Timing tổng hợp chứng minh cách xử lý latency/miss; claim dữ liệu thật nêu count event/condition; latency/false alarm/miss/loss là measure riêng, condition thiếu ghi unavailable.

#### Task con T-026 — Tổng hợp đánh giá và lỗi

- [X] **T-143 [T-026]:** Test tổng hợp ghép annotation/run record, latency/event media-time, eligibility chung, lý do loss, điều kiện xử lý và công khai condition thiếu.
- [X] **T-144 [T-026]:** Triển khai evaluator xác định: suy episode từ frame record, dùng matcher có tham số, tổng hợp latency/coverage/failure, xuất kết quả máy đọc được (phụ thuộc T-141, T-143).
- [X] **T-145 [T-026]:** Xác minh evaluator bằng fixture tổng hợp và pilot gán nhãn rõ; ghi condition NITYMED còn thiếu, giữ claim thật bị chặn đến T-139 (phụ thuộc T-144).

- [ ] **T-027 — Chạy đánh giá A/B/C có kiểm soát và so sánh** (Research; P0; G5, T-023–T-026, T-013)
  - **Yêu cầu:** FR-018–FR-019; NFR-001–NFR-003, NFR-006; RA-001–RA-004.
  - **Mục tiêu/các bước:** Trả lời câu hỏi nghiên cứu chính bằng kết quả held-out có thể so sánh. Khóa config/ngưỡng từ validation; chạy A/B/C trên cùng video/nhãn test đủ điều kiện, lấy PERCLOS landmark làm so sánh chính. Nếu thiết kế cho phép, chạy PERCLOS CNN là thí nghiệm phụ có nhãn riêng. Ghi hardware/runtime thật, không tune theo test.
  - **Artifact/xác minh/hoàn tất:** Run record/tables máy đọc được ở `outputs/results/` ignore, summary trong docs. Audit run ID/config/test membership, xác nhận cùng test và không test-informed tuning, tính lại summary từ raw run. Có metric hoàn chỉnh so sánh được hoặc kết quả blocked/incomplete có ghi; không bịa số hoặc tuyên bố mục tiêu Accuracy không có căn cứ.

#### Task con T-027 — Thực thi A/B/C có kiểm soát

- [X] **T-146 [T-027]:** Test batch plan buộc cùng clip, annotation/split ID, landmark-EAR, base temporal setting, eligibility/ngưỡng khóa giữa A/B/C.
- [X] **T-147 [T-027]:** Triển khai batch runner headless có resume và comparison exporter: failure từng clip, output không collision, run/config/data hash, không audio/UI side effect (phụ thuộc T-121, T-146).
- [X] **T-155 [T-027]:** Thêm config validation numeric-head-reference theo runner A/B/C, giữ boundary validation-only/held-out (phụ thuộc T-147).
- [X] **T-156 [T-027]:** Chạy baseline validation 12 clip đầy đủ A/B/C, audit 36/36 record/artifact ID, ghi coverage thấp không coi held-out claim (phụ thuộc T-155).
- [ ] **T-157 [T-027]:** Thêm replay validation offline xác định và sweep giới hạn warm-up/config trên quan sát lưu; tuning không chạy lại landmark hay xem test (phụ thuộc T-156).
- [ ] **T-158 [T-027]:** Chọn/khóa một config validation qua coverage, false alarm, miss, F1, latency; công bố selection rule/hash trước test scoring (phụ thuộc T-157).
- [ ] **T-159 [T-027]:** Review độc lập 26 test held-out theo batch nhỏ và hoàn tất manifest annotation không thấy model output (phụ thuộc T-158; cần người review).
- [X] **T-160 [T-159]:** Công bố handoff teammate: Phase 6 hiện tại, tiền đề private data, review control chính xác, bảy batch phục hồi được và checklist nghiệm thu.
- [ ] **T-148 [T-027]:** Chạy/kiểm tra pilot không claim trên validation đã duyệt để xác nhận replay/export/evaluator; không tune/chấm held-out (phụ thuộc T-139, T-145, T-147).
- [ ] **T-149 [T-027]:** Khóa config validation, chạy A/B/C một lần trên test held-out chung, tính lại summary từ raw record, audit comparability, công bố limitation (phụ thuộc T-013, T-022, T-026, T-148; cần phê duyệt research).

### Gate nghiệm thu Phase 6

G6 đạt khi protocol/corpus được duyệt, metric được test, mọi method khả thi chạy trên held-out chung, kết quả latency/lỗi/coverage/condition thật được ghi và giới hạn rõ. Thiếu dữ liệu/nhãn hợp pháp là blocker, không phải lý do thay kết quả bịa.

## Phase 7 — Xác minh cuối và bàn giao

**Kết quả mốc:** Tin cậy hồi quy, bằng chứng yêu cầu truy vết được, hướng dẫn tái lập và artifact demo/báo cáo sẵn sàng.

- [X] **T-161 [Phase 7]:** Audit readiness Phase 7, tạo nhánh `phase/7-final-validation-delivery` phục hồi được từ baseline Phase 6 đã merge, chia T-028–T-031 mà không bỏ qua G4/G6 mở (recovery branch `task/T-161-phase7-readiness`).

- [ ] **T-028 — Chạy suite integration và regression** (P0; G2–G6)
  - **Yêu cầu:** FR-001–FR-020; NFR-004–NFR-009; RA-006–RA-007.
  - **Mục tiêu/các bước:** Xác minh toàn bộ triển khai, tìm regression xuyên input, inference, temporal rule, alert và experiment. Chạy lint/test tại root, scenario video ghi sẵn xác định, webcam/audio thủ công có sẵn; ghi OS/Python/dependency/model/input và skip phụ thuộc hardware.
  - **Artifact/xác minh/hoàn tất:** cập nhật `verification.md`, output CI/test hoặc run log review. Suite tự động đạt; manual check nêu môi trường thật, không gọi skip là pass; critical failure được sửa/ghi owner-blocker, không đổi source không liên quan.

#### Task con T-028 — Bằng chứng regression đa nền tảng/cuối

T-162–T-164 có thể chạy trước G6 vì không dùng/tuyên bố held-out; T-028 mở cho đến T-165 sau G6 và có mọi bằng chứng hardware.

- [X] **T-162 [T-028]:** Thêm CI Ubuntu/Windows cho dependency khóa, Ruff, toàn bộ test tại `.github/workflows/ci.yml`; camera/audio là non-CI (phụ thuộc T-161; branch `task/T-162-ci-platform-matrix`).
- [X] **T-163 [T-028]:** Thêm smoke package-build CI bằng `uv build`, không publish artifact/đưa deployment credential (phụ thuộc T-162; branch `task/T-163-package-build-check`).
- [X] **T-164 [T-028]:** Chạy local Ruff, pytest, package-build; ghi chuẩn bị Phase 7 và blocker G4/G6 trong verification (phụ thuộc T-163; branch `task/T-164-preliminary-regression`).
- [ ] **T-165 [T-028]:** Sau G6, chạy lại automated/deterministic recorded-video regression cuối, thêm kết quả webcam/audio thật nếu có, audit failure/skip và hoàn tất T-028 khi evidence reviewable (phụ thuộc G6, T-164; branch `task/T-165-final-regression`).

- [ ] **T-029 — Hoàn tất truy vết requirement-to-evidence** (P0; T-028, T-027)
  - **Yêu cầu:** Mọi FR/DR/NFR/RA; Constitution Principle VII.
  - **Mục tiêu/các bước:** Tạo/cập nhật `requirement-coverage.md` ánh xạ FR, DR, NFR, RA và quyết định G0 tới implementation path, test/evidence và status. Phân biệt code tồn tại với hành vi đã xác minh/mục tiêu với kết quả đo.
  - **Artifact/xác minh/hoàn tất:** requirement coverage; mọi requirement bắt buộc có status/evidence/blocker rõ; A/B/C và >=0.90 không được suy từ scaffold. Reviewer truy vết được đến test/record/hạn chế mở.

#### Task con T-029 — Audit bằng chứng requirement

- [ ] **T-166 [T-029]:** Lập `requirement-coverage.md` từ SPEC đã duyệt, map mọi FR/DR/NFR/RA/G0 sang implementation/bằng chứng khả dĩ, ghi bằng chứng chưa giải quyết (phụ thuộc T-165, T-027; branch `task/T-166-requirement-coverage`).
- [ ] **T-167 [T-029]:** Review từng mapping với test/result đã lưu; phân biệt implemented, verified, measured, blocked, deferred; chỉ hoàn tất khi không có claim mục tiêu/A-B-C không được hỗ trợ (phụ thuộc T-166; branch `task/T-167-traceability-review`).

- [ ] **T-030 — Hoàn thiện hướng dẫn setup/chạy tái lập** (P1; T-028, T-029)
  - **Yêu cầu:** NFR-005–NFR-008; RA-005–RA-007.
  - **Mục tiêu/các bước:** Để nhà nghiên cứu khác cài đặt, chuẩn bị dữ liệu được phép, chạy demo webcam/video và tái lập experiment. Cập nhật README/docs/data/model với setup, source/license, vị trí private data, command train/eval/demo, config, output, limit, advisory-only; không bundle raw data bị hạn chế.
  - **Artifact/xác minh/hoàn tất:** README/data/model README và docs liên quan. Theo workflow ở môi trường sạch hoặc ghi blocker môi trường; command/path khớp entry point/output thật. Nhà nghiên cứu mới chạy được không cần path ngầm/ngưỡng không ghi.

#### Task con T-030 — Bàn giao tái lập

- [ ] **T-168 [T-030]:** Đồng bộ README, `data/README.md`, `models/README.md`, docs với command cuối, asset/data placement, config khóa, output, privacy/limit (phụ thuộc T-167; branch `task/T-168-reproducibility-docs`).
- [ ] **T-169 [T-030]:** Chạy setup/command đại diện ở môi trường sạch, sửa drift path/command, ghi blocker asset ngoài và hoàn tất T-030 (phụ thuộc T-168; branch `task/T-169-clean-environment-check`).

- [ ] **T-031 — Chuẩn bị figure, export kết quả và evidence bàn giao** (P1; T-027–T-030)
  - **Yêu cầu:** FR-019; NFR-006; RA-001–RA-007.
  - **Mục tiêu/các bước:** Tạo table/figure reviewable, evidence demo cho report/slide từ kết quả đã lưu (không gõ lại thủ công); kiểm tra method label/unit; chuẩn bị ví dụ warning không cá nhân; inventory source/checkpoint/config phân phối được và restriction license/consent. Theo dõi report 35–45 trang/slide như đầu vào handoff, không bịa kết quả thiếu.
  - **Artifact/xác minh/hoàn tất:** script export tái lập, output/figure/checklist bàn giao. Table sinh lại khớp run record, không có media riêng tư/artifact không được phép trong Git/public delivery; evidence package hỗ trợ báo cáo hoặc nêu tiền đề/kết quả thiếu.

#### Task con T-031 — Evidence bàn giao tái lập

- [ ] **T-170 [T-031]:** Triển khai/hoàn thiện exporter xác định tạo table/figure report từ run record, có method label, unit, count và provenance được test (phụ thuộc T-027–T-030; branch `task/T-170-result-exporters`).
- [ ] **T-171 [T-031]:** Sinh lại/audit delivery evidence, xác nhận không có private/restricted media, ghi artifact phân phối/license constraint; chỉ hoàn tất T-031/G7 sau owner review (phụ thuộc T-170; branch `task/T-171-delivery-audit`).

### Gate nghiệm thu Phase 7

G7 đạt khi regression, truy vết evidence, setup tái lập và result export được review. Report/slide cuối chỉ nêu kết quả được dữ liệu duyệt và evidence experiment đã lưu hỗ trợ.

## Đồ thị phụ thuộc và critical path

```text
G0/T-001 → T-002 → T-003 → T-004 → G1
G1 → T-005 → T-006 → T-007 → T-008 → T-009 → G2
G1 → T-010 → T-011 → T-012 → T-013 → T-014
G2 → T-015 → (T-016, T-017) → T-018 → G4
G2 → (T-019, T-020) → T-021 → T-022 → G5
G1 + G5 → T-023 → T-024 → T-025 → T-026 → T-027 → G6 → T-028 → T-029 → T-030/T-031 → G7
```

## Kiểm soát nguồn

Checklist tiếng Anh vẫn là nguồn chuẩn để cập nhật trạng thái và tiêu chí nghiệm thu. Bản dịch này giữ mục tiêu, task, phụ thuộc, artifact và quy tắc chính bằng tiếng Việt; khi có khác biệt phải theo `specs/001-drowsyalert/tasks.md`.
