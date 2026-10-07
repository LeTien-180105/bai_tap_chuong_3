# Sổ điểm lớp học

## 1. Chạy chương trình

Ứng dụng chạy tại:
http://127.0.0.1:8000
## 2. Các chức năng
- Trang chủ
- Danh sách sinh viên
- Lọc sinh viên theo lớp
- Chi tiết sinh viên
- Link rút gọn 301
- Xuất bảng điểm CSV
- Tìm kiếm sinh viên
- API đọc danh sách
- API đọc sinh viên
- API thêm, sửa, xóa điểm
- Xử lý lỗi 400, 404, 405
## 3. API
Danh sách
GET /api/students
Lọc lớp
GET /api/students?lop=K47A
Lọc điểm
GET /api/students?min_avg=7
Chi tiết sinh viên
GET /api/students/23T1020001
Điểm học phần
GET /api/students/23T1020001/scores/MMT
PUT /api/students/23T1020005/scores/WEB?score=9
DELETE /api/students/23T1020005/scores/WEB
## 4. Trả lời câu hỏi
Vì sao Câu 4 dùng 301 còn Câu 8 trả 201 kèm Location?
Câu 4 dùng 301 vì đây là chuyển hướng vĩnh viễn từ URL cũ
/sv/<mssv> sang URL chính /students/<mssv>.
Câu 8 dùng 201 khi tạo mới một điểm. Location chỉ tới
resource vừa được tạo.
Thêm điểm cho 23T1020005 rồi khởi động lại server,
điểm đó còn không? Vì sao?
Không. Dữ liệu STUDENTS chỉ nằm trong bộ nhớ RAM.
Khi khởi động lại server, dữ liệu quay lại trạng thái ban đầu
trong mã nguồn.