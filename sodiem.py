from flask import (
    Flask,
    request,
    jsonify,
    abort,
    redirect,
    url_for,
    make_response
)
from markupsafe import escape
import csv
import io


app = Flask(__name__)

app.json.ensure_ascii = False

STUDENTS = {
    "23T1020001": {
        "name": "Nguyễn Văn An",
        "lop": "K47A",
        "scores": {
            "PMMNM": 8.5,
            "CSDL": 7.0,
            "MMT": 9.0
        }
    },

    "23T1020002": {
        "name": "Trần Thị Bình",
        "lop": "K47A",
        "scores": {
            "PMMNM": 6.0,
            "CSDL": 5.5,
            "MMT": 7.0
        }
    },

    "23T1020003": {
        "name": "Lê Hoàng Cường",
        "lop": "K47B",
        "scores": {
            "PMMNM": 9.5,
            "CSDL": 9.0
        }
    },

    "23T1020004": {
        "name": "Phạm Minh Dũng",
        "lop": "K47B",
        "scores": {
            "PMMNM": 4.0,
            "CSDL": 3.5,
            "MMT": 5.0
        }
    },

    "23T1020005": {
        "name": "Hoàng Thu Hà",
        "lop": "K47A",
        "scores": {}
    },

    "23T1020006": {
        "name": "Võ Quốc Khánh",
        "lop": "K47C",
        "scores": {
            "PMMNM": 7.5,
            "MMT": 8.0
        }
    }
}


def average(scores):
    if not scores:
        return None

    return round(sum(scores.values()) / len(scores), 2)


def rank(avg):
    if avg is None:
        return "Chưa có điểm"

    if avg >= 8.5:
        return "Giỏi"

    if avg >= 7.0:
        return "Khá"

    if avg >= 5.0:
        return "Trung bình"

    return "Yếu"


def student_summary(mssv):
    student = STUDENTS[mssv]

    avg = average(student["scores"])

    return {
        "mssv": mssv,
        "name": student["name"],
        "lop": student["lop"],
        "scores": student["scores"],
        "average": avg,
        "rank": rank(avg)
    }


def layout(title, body):
    title = escape(title)

    return f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>{title} - Sổ điểm</title>

    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
        }}

        nav {{
            margin-bottom: 20px;
        }}

        table {{
            border-collapse: collapse;
            margin-top: 15px;
        }}

        th, td {{
            border: 1px solid #999;
            padding: 8px 12px;
        }}

        th {{
            background: #eeeeee;
        }}

        a {{
            text-decoration: none;
        }}
    </style>
</head>

<body>

<nav>
    <a href="{url_for('home')}">Trang chủ</a>
    |
    <a href="{url_for('student_list')}">Sinh viên</a>
    |
    <a href="{url_for('search')}">Tìm kiếm</a>
</nav>

<hr>

{body}

</body>
</html>
"""

@app.get("/")
def home():

    total = len(STUDENTS)

    classes = len({
        student["lop"]
        for student in STUDENTS.values()
    })

    body = f"""
    <h1>Sổ điểm lớp học</h1>

    <p>Tổng số sinh viên: {total}</p>

    <p>Số lớp: {classes}</p>

    <p>
        <a href="{url_for('student_list')}">
            Xem danh sách sinh viên
        </a>
    </p>

    <p>
        <a href="{url_for('api_students')}">
            API sinh viên
        </a>
    </p>
    """

    return layout("Trang chủ", body)

@app.get("/students")
def student_list():

    lop = request.args.get("lop")

    rows = ""

    for mssv, student in STUDENTS.items():

        if lop and student["lop"].lower() != lop.lower():
            continue

        avg = average(student["scores"])

        avg_display = (
            avg
            if avg is not None
            else "—"
        )

        rows += f"""
        <tr>
            <td>
                <a href="{url_for('student_detail', mssv=mssv)}">
                    {escape(mssv)}
                </a>
            </td>

            <td>{escape(student["name"])}</td>

            <td>{escape(student["lop"])}</td>

            <td>{avg_display}</td>

            <td>{escape(rank(avg))}</td>
        </tr>
        """

    if not rows:
        rows = """
        <tr>
            <td colspan="5">
                Không có sinh viên phù hợp.
            </td>
        </tr>
        """

    classes = sorted({
        student["lop"]
        for student in STUDENTS.values()
    })

    filter_links = f"""
    <p>
        Lọc:

        <a href="{url_for('student_list')}">
            Tất cả
        </a>
    """

    for class_name in classes:
        filter_links += f"""
        |
        <a href="{url_for('student_list', lop=class_name)}">
            {escape(class_name)}
        </a>
        """

    filter_links += "</p>"

    body = f"""
    <h1>Danh sách sinh viên</h1>

    {filter_links}

    <form method="get"
          action="{url_for('student_list')}">

        <label>Lọc theo lớp:</label>

        <input
            type="text"
            name="lop"
            value="{escape(lop or '')}"
            placeholder="Ví dụ: K47A"
        >

        <button type="submit">
            Lọc
        </button>

    </form>

    <table>
        <tr>
            <th>MSSV</th>
            <th>Họ tên</th>
            <th>Lớp</th>
            <th>Điểm TB</th>
            <th>Xếp loại</th>
        </tr>

        {rows}
    </table>
    """

    return layout("Danh sách sinh viên", body)

@app.get("/students/<mssv>")
def student_detail(mssv):

    if mssv not in STUDENTS:
        abort(
            404,
            description=f"Không có sinh viên với MSSV = {mssv}."
        )

    student = STUDENTS[mssv]

    avg = average(student["scores"])

    rows = ""

    for course, score in student["scores"].items():
        rows += f"""
        <tr>
            <td>{escape(course)}</td>
            <td>{score}</td>
        </tr>
        """

    if not rows:
        rows = """
        <tr>
            <td colspan="2">
                Chưa có điểm.
            </td>
        </tr>
        """

    body = f"""
    <h1>Chi tiết sinh viên</h1>

    <p>
        <strong>MSSV:</strong>
        {escape(mssv)}
    </p>

    <p>
        <strong>Họ tên:</strong>
        {escape(student["name"])}
    </p>

    <p>
        <strong>Lớp:</strong>

        <a href="{url_for('student_list', lop=student['lop'])}">
            {escape(student["lop"])}
        </a>
    </p>

    <p>
        <strong>Điểm TB:</strong>
        {avg if avg is not None else "—"}
    </p>

    <p>
        <strong>Xếp loại:</strong>
        {escape(rank(avg))}
    </p>

    <h2>Bảng điểm</h2>

    <table>
        <tr>
            <th>Học phần</th>
            <th>Điểm</th>
        </tr>

        {rows}
    </table>

    <p>
        <a href="{url_for('export_scores', mssv=mssv)}">
            Tải bảng điểm (CSV)
        </a>
    </p>

    <p>
        <a href="{url_for('short_student', mssv=mssv)}">
            Link rút gọn
        </a>
    </p>
    """

    return layout("Chi tiết sinh viên", body)

@app.get("/sv/<mssv>")
def short_student(mssv):

    if mssv not in STUDENTS:
        abort(
            404,
            description=f"Không có sinh viên với MSSV = {mssv}."
        )

    return redirect(
        url_for("student_detail", mssv=mssv),
        code=301
    )


@app.get("/students/<mssv>/export")
def export_scores(mssv):

    if mssv not in STUDENTS:
        abort(
            404,
            description=f"Không có sinh viên với MSSV = {mssv}."
        )

    student = STUDENTS[mssv]

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "hoc_phan",
        "diem"
    ])

    for course, score in student["scores"].items():
        writer.writerow([
            course,
            score
        ])

    response = make_response(output.getvalue())

    response.headers["Content-Type"] = (
        "text/csv; charset=utf-8"
    )

    response.headers["Content-Disposition"] = (
        f"attachment; filename=diem_{mssv}.csv"
    )

    return response

@app.get("/search")
def search():

    keyword = request.args.get(
        "q",
        ""
    ).strip()

    results = []

    for mssv, student in STUDENTS.items():

        if (
            keyword.lower() in student["name"].lower()
            or
            keyword.lower() in mssv.lower()
        ):
            results.append(
                student_summary(mssv)
            )

    rows = ""

    for student in results:

        rows += f"""
        <tr>
            <td>
                <a href="{url_for(
                    'student_detail',
                    mssv=student['mssv']
                )}">
                    {escape(student["mssv"])}
                </a>
            </td>

            <td>
                {escape(student["name"])}
            </td>

            <td>
                {escape(student["lop"])}
            </td>

            <td>
                {
                    student["average"]
                    if student["average"] is not None
                    else "—"
                }
            </td>

            <td>
                {escape(student["rank"])}
            </td>
        </tr>
        """

    if not rows:
        rows = """
        <tr>
            <td colspan="5">
                Không tìm thấy sinh viên phù hợp.
            </td>
        </tr>
        """

    body = f"""
    <h1>Tìm kiếm sinh viên</h1>

    <form method="get"
          action="{url_for('search')}">

        <input
            type="text"
            name="q"
            value="{escape(keyword)}"
            placeholder="Nhập tên hoặc MSSV"
        >

        <button type="submit">
            Tìm kiếm
        </button>

    </form>

    <p>
        Tìm thấy {len(results)}
        kết quả cho
        “{escape(keyword)}”
    </p>

    <table>
        <tr>
            <th>MSSV</th>
            <th>Họ tên</th>
            <th>Lớp</th>
            <th>Điểm TB</th>
            <th>Xếp loại</th>
        </tr>

        {rows}
    </table>
    """

    return layout("Tìm kiếm", body)


@app.get("/api/students")
def api_students():

    lop = request.args.get("lop")

    if "min_avg" not in request.args:
        min_avg = None
    else:
        try:
            min_avg = float(
                request.args.get("min_avg")
            )
        except (TypeError, ValueError):
            abort(
                400,
                description="min_avg phải là một số."
            )

    results = []

    for mssv, student in STUDENTS.items():

      
        if lop:
            if student["lop"].lower() != lop.lower():
                continue

        summary = student_summary(mssv)

        
        if min_avg is not None:

            avg = summary["average"]

            if avg is None:
                continue

            if avg < min_avg:
                continue

        results.append(summary)

    return jsonify(results)


@app.get("/api/students/<mssv>")
def api_student_detail(mssv):

    if mssv not in STUDENTS:
        abort(
            404,
            description=f"Không có sinh viên với MSSV = {mssv}."
        )

    return jsonify(
        student_summary(mssv)
    )


@app.route(
    "/api/students/<mssv>/scores/<course>",
    methods=["GET", "PUT", "DELETE"]
)
def api_score(mssv, course):

    
    if mssv not in STUDENTS:
        abort(
            404,
            description=f"Không có sinh viên với MSSV = {mssv}."
        )

    
    course = course.upper()

    scores = STUDENTS[mssv]["scores"]


    if request.method == "GET":

        if course not in scores:
            abort(
                404,
                description=(
                    f"Sinh viên {mssv} "
                    f"chưa có điểm học phần {course}."
                )
            )

        return jsonify({
            "mssv": mssv,
            "course": course,
            "score": scores[course]
        })


    if request.method == "PUT":

        score_text = request.args.get("score")

        
        if score_text is None:
            abort(
                400,
                description="Thiếu tham số score."
            )

        
        try:
            score = float(score_text)
        except ValueError:
            abort(
                400,
                description="score phải là một số."
            )

        
        if score < 0 or score > 10:
            abort(
                400,
                description="score phải nằm trong khoảng từ 0 đến 10."
            )

    
        existed = course in scores

       
        scores[course] = score

        avg = average(scores)

        result = {
            "mssv": mssv,
            "course": course,
            "score": score,
            "average": avg
        }


        if not existed:

            response = make_response(
                jsonify(result),
                201
            )

            response.headers["Location"] = url_for(
                "api_score",
                mssv=mssv,
                course=course
            )

            return response

       
        return jsonify(result)


    if request.method == "DELETE":

        if course not in scores:
            abort(
                404,
                description=(
                    f"Sinh viên {mssv} "
                    f"chưa có điểm học phần {course}."
                )
            )

        del scores[course]

        return "", 204


@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(405)
def handle_error(error):

    code = error.code

    if code == 400:
        title = "Dữ liệu không hợp lệ"

    elif code == 404:
        title = "Không tìm thấy"

    else:
        title = "Phương thức không được hỗ trợ"

    detail = error.description

   
    if request.path.startswith("/api/"):

        return jsonify({
            "error": title,
            "detail": detail
        }), code

    body = f"""
    <h1>{code} - {escape(title)}</h1>

    <p>
        {escape(detail)}
    </p>

    <p>
        <a href="{url_for('home')}">
            Quay về trang chủ
        </a>
    </p>
    """

    return layout(
        f"{code} - {title}",
        body
    ), code



if __name__ == "__main__":
    app.run(
        debug=True,
        port=8000
    )