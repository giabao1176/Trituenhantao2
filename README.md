# Bài tập lớn môn Trí tuệ nhân tạo

Repository này chứa mã nguồn và kết quả của 3 bài toán lớn được thực hiện trong môn học Trí tuệ nhân tạo. Mỗi bài toán đều có giao diện đồ họa (GUI) đi kèm và thư mục chứa ảnh GIF mô phỏng chi tiết các bước chạy của từng thuật toán.

---

## 1. Robot Hút Bụi (`robothutbui/`)
Bài toán mô phỏng một robot tự động dọn dẹp các ô bụi trên bản đồ dạng lưới $M \times N$, có chứa các ô chướng ngại vật. Bài toán được chia thành các môi trường khác nhau để áp dụng nhiều nhóm giải thuật:

**Môi trường bình thường (Quan sát toàn phần - Full Observability)**: Robot biết trước vị trí của mình, vị trí bụi và vật cản. Các thuật toán tìm kiếm được áp dụng bao gồm:
- *Tìm kiếm mù*: BFS, DFS, IDS, UCS.
- *Tìm kiếm heuristic*: Greedy, A*, IDA*.
- *Tìm kiếm cục bộ*: Hill Climbing, Random Restart Hill, Local Beam Search, Simulated Annealing. (Trong đó giải thuật Hill Climbing sử dụng cơ chế sinh bản đồ ngẫu nhiên để đảm bảo robot chạy được một số bước trước khi dừng).

**Môi trường không cảm biến (Sensorless / Conformant Planning)**: Robot không biết vị trí xuất phát của mình và trạng thái bụi ban đầu (phải tự tính toán không gian trạng thái niềm tin - Belief State Space). Cả 11 giải thuật tìm kiếm nêu trên đều được áp dụng cho môi trường này để tìm ra một chuỗi hành động tuyến tính dọn sạch nhà.

**Môi trường quan sát một phần (Partially Observable) & Không đơn định**: Robot chỉ nhận biết được ô hiện tại có bụi hay không và các tường kề. Lời giải ở đây là một kế hoạch có điều kiện (conditional plan) dạng cây quyết định dựa trên cảm nhận nhận được sau mỗi hành động:
- *AND-OR Search*: Giải bài toán trong môi trường không đơn định (Erratic Vacuum World).
- *Partially Observable Search*: Tìm kiếm trên không gian trạng thái niềm tin kết hợp cập nhật cảm nhận sau mỗi bước đi thực tế.

---

## 2. Tô Màu Bản Đồ TP.HCM (`tomaubando/`)
Bài toán tô màu bản đồ hành chính gồm 22 quận/huyện của TP.HCM sao cho hai quận/huyện kề nhau không được trùng màu, sử dụng tối đa 4 màu khác nhau. Đây là bài toán Thỏa mãn ràng buộc (CSP) được giải quyết bằng các giải thuật:

**Backtracking**: Giải thuật quay lui cơ bản để tìm cấu hình màu hợp lệ.

**Forward Checking**: Kết hợp quay lui với kiểm tra trước các ràng buộc để phát hiện sớm các nhánh cụt và cắt tỉa miền giá trị.

**AC-3**: Nhất quán cung giúp lọc sạch miền giá trị của các quận/huyện trước khi bắt đầu tìm kiếm nhằm tối ưu thời gian.

**Min-Conflicts**: Thuật toán tìm kiếm cục bộ chuyên dụng cho CSP. Thuật toán chọn ngẫu nhiên các quận bị xung đột màu và gán lại màu mới để giảm thiểu tối đa số lượng xung đột một cách nhanh chóng.

---

## 3. Trò Chơi Tic-Tac-Toe (`tictactoe/`)
Bài toán game cờ ca-rô 3x3 để minh họa cho các giải thuật tìm kiếm đối kháng (Adversarial Search) trên cây trò chơi.

Ảnh GIF mô phỏng trận đấu được thiết kế dưới dạng **Người chơi (Human)** đấu với **AI**:
- *Người chơi (Quân X)*: Được mô phỏng bằng các nước đi ngẫu nhiên thực tế của con người, thống kê số node duyệt hiển thị là `N/A`.
- *AI (Quân O)*: Sử dụng các thuật toán đối kháng để tìm nước đi tối ưu và hiển thị số lượng node đã duyệt.

Các thuật toán AI được áp dụng và so sánh:
- **Minimax**: Tìm nước đi tối ưu tuyệt đối dựa trên giả định đối thủ cũng chơi hoàn hảo.
- **Alpha-Beta Pruning**: Cắt tỉa nhánh cây trò chơi để giảm số lượng trạng thái cần duyệt mà vẫn giữ nguyên kết quả tối ưu của Minimax.
- **Expectimax**: Ra quyết định trong môi trường có tính bất định (khi giả định đối thủ/người chơi có xác suất đi sai hoặc đi ngẫu nhiên), tối ưu giá trị kỳ vọng (expected value).
