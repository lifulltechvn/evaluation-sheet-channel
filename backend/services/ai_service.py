"""AI service — Feedback & Recommend using Gemini with detailed skill knowledge base."""

import os
import json

# Detailed technical skill descriptions per position/grade (from Confluence Business Docs)
SKILL_KB: dict[str, dict[str, dict[str, str]]] = {
    "application_engineer": {
        "G0": {
            "Programming": "Có thể lập trình backend, frontend của 1 trang EC cơ bản (chọn sản phẩm → nhập thông tin → mua hàng). Chưa cần chức năng thanh toán, security.",
            "Data Store": "Có thể viết SQL cơ bản (get/update/delete). Hiểu INNER JOIN, LEFT/RIGHT/FULL JOIN.",
            "Testing": "Có thể tạo normal testcase để kiểm tra các thao tác cơ bản của chức năng.",
            "Architecture": "",
            "Server-Middleware": "",
            "Infrastructure-Network": "",
            "Security": "Hiểu được tại sao các giải pháp bảo mật lại cần thiết.",
            "Frontend": "",
            "Định nghĩa yêu cầu": "Có thể đặt các câu hỏi cần thiết đúng thời điểm về các task của bản thân.",
            "Quản lý tiến độ": "Có thể hiểu rõ schedule của dự án và luôn ý thức để đảm bảo tiến độ task đúng với schedule.",
            "Data Analysis": "",
            "Đề xuất cải thiện": "",
        },
        "G1": {
            "Programming": "Có thể lập trình ứng dụng được giao theo đúng specs.",
            "Data Store": "Có kiến thức cơ bản về data normalization và data type, có thể thực hiện truy vấn dữ liệu từ data store.",
            "Testing": "Nắm được kỹ thuật Equivalence Partitioning, Boundary value, Condition Coverage để tạo testcase không bị thiếu. Có thể tuân theo tài liệu test để tiến hành kiểm thử và báo cáo lỗi.",
            "Architecture": "Có kiến thức cơ bản về OOP, có ý thức về design pattern như MVC trong quá trình phát triển.",
            "Server-Middleware": "Nắm được kiến thức cơ bản về Linux server-Middleware. Hiểu và giải thích được cấu trúc server đang sử dụng.",
            "Infrastructure-Network": "Nắm được kiến thức cơ bản về Name resolution, routing, network, cách kết nối với server trên Cloud, Security.",
            "Security": "Hiểu cơ bản về Session, Cookie, JavaScript, HTML, HTTP method, request params và header. Có thể thiết lập validation và xử lý escape hợp lý.",
            "Frontend": "Có kiến thức về lập trình frontend (html, css, JavaScript), hiểu data type, primitive. Có thể sử dụng các thư viện có sẵn và chỉnh sửa file markup.",
            "Định nghĩa yêu cầu": "Có thể hiểu chính xác yêu cầu từ cấp trên.",
            "Quản lý tiến độ": "Có thể hoàn thành task đúng tiến độ khi có sự trợ giúp về quản lý tiến độ từ cấp trên.",
            "Data Analysis": "Cùng với sự trợ giúp của cấp trên, có thể dựa vào data đã thu thập để đưa ra kết luận phù hợp.",
            "Đề xuất cải thiện": "Có thể đưa ra giải pháp cải thiện cho 1 chức năng hoặc 1 page nhờ sự giúp đỡ của cấp trên.",
        },
        "G2": {
            "Programming": "Luôn cân nhắc tới khả năng tái sử dụng (reusability), hiểu và thực hiện được các xử lý retry cũng như error handling.",
            "Data Store": "Có kiến thức cơ bản về đặc trưng của từng data store, có thể sử dụng trong ứng dụng mình phụ trách.",
            "Testing": "Có thể review testcase, đưa ra feedback về thiếu case/điều kiện. Có thể viết unit test bao phủ C0, C1, C2.",
            "Architecture": "Có thể đưa ra thiết kế hệ thống dễ maintain, đảm bảo OOP (phân chia thuộc tính, trừu tượng hóa object), thể hiện qua sequence diagram.",
            "Server-Middleware": "Trên Linux server, có thể hiểu và sử dụng hợp lý các đặc trưng tính năng của middleware (xử lý song song, connection pool, cache).",
            "Infrastructure-Network": "Có kiến thức về các phương pháp kiểm tra kết nối khi xảy ra vấn đề, có thể sử dụng để thảo luận và giải quyết vấn đề.",
            "Security": "Có kiến thức cơ bản về các phương pháp tấn công (SQL injection, XSS, CSRF, Directory traversal, session hijacking) và cách khắc phục.",
            "Frontend": "Hiểu Closure, xử lý bất đồng bộ, ngữ cảnh thực thi. Cân nhắc encapsulation và tính hiệu quả.",
            "Định nghĩa yêu cầu": "Có thể tự mình hiểu được yêu cầu của khách hàng dựa vào tài liệu.",
            "Quản lý tiến độ": "Có thể tạo schedule cá nhân phù hợp với schedule team và hoàn thành đúng tiến độ.",
            "Data Analysis": "Dựa vào data thu thập được, đưa ra nhận định hợp lý về plan đang phụ trách (ở mức độ Project).",
            "Đề xuất cải thiện": "Có thể đưa ra giải pháp cải thiện cho 1 page/chức năng dựa trên tìm hiểu thực trạng và market.",
        },
        "G3": {
            "Programming": "Có sự cân nhắc về tối ưu hóa memory usage, tốc độ thực thi. Tối ưu data store và số lần gọi API. Thêm error handling và log phân tích nguyên nhân lỗi.",
            "Data Store": "Có thể thực hiện thiết kế data store (physical và logical), tính toán chi phí và hiệu năng.",
            "Testing": "Có cân nhắc tới Testability trong phát triển. Có thể test và phát hiện vấn đề liên quan tới yêu cầu phi chức năng (security test, performance test).",
            "Architecture": "Tuân thủ DRY, SOLID, KISS. Thiết kế hệ thống loose coupling, tạo được sub object của chức năng/hệ thống.",
            "Server-Middleware": "Có thể phân tích đánh giá hiệu năng server/middleware, chỉ ra vấn đề và đưa ra phương án cải thiện.",
            "Infrastructure-Network": "Có thể đưa ra đề xuất về infra/network để cải thiện vấn đề tồn tại (tốc độ, tính khả dụng).",
            "Security": "Có thể review code và test documents về khía cạnh security và đưa ra feedback.",
            "Frontend": "Hiểu ES5, CSS2.x, có thể tự mình thực hiện một module trong 1 trang web.",
            "Định nghĩa yêu cầu": "Với sự hỗ trợ của cấp trên, có thể tài liệu hóa specs ứng dụng đáp ứng yêu cầu khách hàng.",
            "Quản lý tiến độ": "Có thể tạo schedule cho toàn bộ dự án với sự trợ giúp từ cấp trên. Quản lý tiến độ task của team.",
            "Data Analysis": "Đưa ra nhận định hợp lý ở mức độ Project. Có thể đưa ra chỉ thị, kiểm tra kết quả phân tích của member G0~G2.",
            "Đề xuất cải thiện": "Có thể đưa ra giải pháp tổng thể cho service, giải quyết vấn đề quy mô lớn và phức tạp với trợ giúp từ cấp trên.",
        },
        "G4": {
            "Programming": "Có cái nhìn tổng thể về hệ thống, cân nhắc tối ưu memory/tốc độ. Quan tâm xử lý bất đồng bộ, multi-thread.",
            "Data Store": "Có kiến thức về mã hóa, tuning, backup. Hiểu rõ cơ chế truyền tải thông tin và triển khai bảo mật phù hợp.",
            "Testing": "Ở bước review specs, có thể chỉ ra mâu thuẫn và vấn đề bảo mật. Đề xuất cách thức kiểm thử tối ưu.",
            "Architecture": "Có thể đưa domain model vào thiết kế kiến trúc, xây dựng hệ thống có khả năng mở rộng bằng Cloud Services.",
            "Server-Middleware": "Hiểu rõ đặc trưng server/middleware, có thể điều tra, kiểm tra và thực hiện basic design cho từng dự án.",
            "Infrastructure-Network": "Có thể lựa chọn resources cần thiết, thực hiện operational design và basic design phù hợp.",
            "Security": "Nắm được sự khác nhau giữa authentication và authorization/ACL. Có thể thiết kế/dựng service phù hợp (OAuth, SAML).",
            "Frontend": "Hiểu UI-Thread, xây dựng ứng dụng phản hồi cao. Kiến thức về lỗ hổng frontend và giải pháp bảo mật. Hiểu W3C recommendation.",
            "Định nghĩa yêu cầu": "Có thể tạo định nghĩa yêu cầu dựa trên yêu cầu khách hàng với sự hỗ trợ cấp trên. Đề xuất specs từ quan điểm user.",
            "Quản lý tiến độ": "Có thể tạo schedule toàn bộ dự án. Phân tích nguyên nhân chậm trễ và đưa ra phương án giải quyết.",
            "Data Analysis": "Đưa ra nhận định ở mức độ triển khai giải pháp cụ thể. Kiểm tra kết quả phân tích của member G0~G3.",
            "Đề xuất cải thiện": "Có thể đưa ra phương án giải quyết vấn đề tổng thể service dựa trên hiểu biết về vision công ty.",
        },
    },
    "bse": {
        "G0": {
            "Năng lực điều phối": "Với sự trợ giúp của cấp trên, có thể tạo đề xuất schedule chi tiết và quản lý tiến độ. Có thể trao đổi với cấp trên về vấn đề khó xử lý.",
            "Định nghĩa yêu cầu": "Đọc hiểu được tài liệu thiết kế, specs được tạo dựa trên các yêu cầu đã thống nhất.",
            "Estimation": "",
            "Data Store": "",
            "Infra-Network": "",
            "Security": "Hiểu được tại sao các giải pháp security lại cần thiết.",
            "Data Analysis": "",
            "Đề xuất cải thiện": "",
            "Năng lực tiếng Nhật": "Có thể giao tiếp bằng tiếng Nhật trong các buổi họp online với sự trợ giúp của cấp trên.",
            "Đảm bảo chất lượng": "Có thể thực hiện test kết hợp sau khi đã hiểu specs nhờ sự trợ giúp của cấp trên.",
        },
        "G1": {
            "Năng lực điều phối": "Có thể tạo đề xuất schedule chi tiết và quản lý tiến độ. Đối với vấn đề khó, có thể đưa ra phương án giải quyết để trao đổi với cấp trên.",
            "Định nghĩa yêu cầu": "Sau khi xác nhận tài liệu thiết kế do người khác tạo, có thể trao đổi, xác nhận với khách hàng và điều chỉnh thông tin chưa rõ ràng.",
            "Estimation": "Với sự trợ giúp của cấp trên, có thể đưa ra công số hợp lý cho công đoạn lập trình, unit test. Tạo được schedule và quản lý tiến độ.",
            "Data Store": "Có kiến thức cơ bản về đặc trưng data store, data normalization, data type. Hiểu được ER Diagram.",
            "Infra-Network": "",
            "Security": "Hiểu được security rules nội bộ LIFULL. Hiểu cơ bản về Session, Cookie, JavaScript, HTML, HTTP methods.",
            "Data Analysis": "Cùng với sự trợ giúp của cấp trên, có thể dựa vào data để đưa ra kết luận phù hợp.",
            "Đề xuất cải thiện": "Có thể đưa ra giải pháp cải thiện cho 1 chức năng/page nhờ sự giúp đỡ của cấp trên.",
            "Năng lực tiếng Nhật": "Có thể đặt câu hỏi, tạo báo cáo qua chat/mail. Hiểu yêu cầu tiếng Nhật trong họp online và giải thích lại chính xác bằng tiếng Việt. Tương đương N2.",
            "Đảm bảo chất lượng": "Có thể thực hiện test kết hợp sau khi đã hiểu specs, thiết kế của ứng dụng.",
        },
        "G2": {
            "Năng lực điều phối": "Có thể dẫn dắt dự án với tư cách Project Leader từ công đoạn code/unit test. Vận hành team dựa vào communication flow đã được quyết định.",
            "Định nghĩa yêu cầu": "Với sự trợ giúp của cấp trên, sau khi lắng nghe yêu cầu khách hàng, có thể tạo Functions List, Screens Transition, Wireframe, Business flow.",
            "Estimation": "Có thể đưa ra công số hợp lý cho lập trình, unit test. Tạo schedule và quản lý tiến độ.",
            "Data Store": "Có thể thực hiện Chuẩn hóa dữ liệu, tạo được ER Diagram.",
            "Infra-Network": "Có kiến thức cơ bản về Linux server-Middleware. Biết mục đích sử dụng các service chính của AWS. Nắm kiến thức cơ bản về Name resolution, routing, network.",
            "Security": "Có kiến thức cơ bản về các phương pháp tấn công (SQL injection, XSS, CSRF) và cách khắc phục. Kiến thức về lỗ hổng bảo mật trên mobile app.",
            "Data Analysis": "Dựa vào data thu thập được, đưa ra nhận định hợp lý ở mức độ Project đang phụ trách.",
            "Đề xuất cải thiện": "Có thể đưa ra giải pháp cải thiện cho 1 page/chức năng dựa trên tìm hiểu thực trạng và market.",
            "Năng lực tiếng Nhật": "Với sự giúp đỡ của cấp trên, có thể tạo tài liệu bằng tiếng Nhật và giải thích nội dung cho người Nhật. Không chỉ dịch mà còn hiểu ý đồ người nói.",
            "Đảm bảo chất lượng": "Nắm được thiết kế và specs, với sự hỗ trợ của cấp trên có thể tạo testcase test kết hợp bao phủ các điều kiện.",
        },
        "G3": {
            "Năng lực điều phối": "Có thể dẫn dắt dự án với tư cách Project Leader ngay từ công đoạn upstream. Đưa ra phương án mà tất cả mọi người đều tán thành. Có quan điểm QCD.",
            "Định nghĩa yêu cầu": "Sau khi lắng nghe yêu cầu khách hàng, có thể tạo Functions List, Screens Transition, Wireframe, Business flow. Quyết định format tài liệu và cách thức giao tiếp.",
            "Estimation": "Với sự trợ giúp của cấp trên, có thể điều chỉnh, thiết lập công việc cho toàn bộ công đoạn, tạo schedule chi tiết. Có thể đảm nhận Scrum Master.",
            "Data Store": "Có thể tạo tài liệu Logical Design của Data Store thỏa mãn yêu cầu ứng dụng.",
            "Infra-Network": "Có thể tài liệu hóa infra-network design, hoặc hiểu được giải thích về thiết kế infra.",
            "Security": "Nắm được sự khác nhau giữa authentication và authorization/ACL. Hiểu thiết kế phù hợp cho service (OAuth, SAML). Có thể trao đổi với team bảo mật.",
            "Data Analysis": "Đưa ra nhận định hợp lý ở mức độ Project. Có thể đưa ra chỉ thị, kiểm tra kết quả phân tích của member G0~G2.",
            "Đề xuất cải thiện": "Có thể đưa ra giải pháp tổng thể cho service, giải quyết vấn đề quy mô lớn với trợ giúp từ cấp trên.",
            "Năng lực tiếng Nhật": "Có thể tạo tài liệu bằng tiếng Nhật và giải thích nội dung cho người Nhật một cách chuẩn xác. Tương đương N1.",
            "Đảm bảo chất lượng": "Nắm được thiết kế và specs, tạo được testcase bao phủ các điều kiện. Có thể review testcase và chỉ ra vấn đề.",
        },
    },
}

# Grade carry-forward rules (from Guidebook)
GRADE_CARRY_FORWARD_RULES = """
Khi nhân viên lên level mới, điểm các skill không nằm trong mục tiêu kỳ này được tính như sau:
- Nếu đã có kết quả đánh giá trước đó ở cùng cấp độ → dùng điểm đó.
- Nếu chưa có → mặc định 1 điểm.
- Nếu kỳ trước đạt 4 điểm → level mới được 2 điểm.
- Nếu kỳ trước đạt 5 điểm → level mới được 3 điểm.
"""

# Scoring rubric
SCORING_RUBRIC = """
Thang điểm đánh giá kỹ năng chuyên môn (1-5):
- 5: Đạt 100% tiêu chuẩn yêu cầu ở cấp độ tiếp theo
- 4: Đạt từ 50% trở lên tiêu chuẩn yêu cầu ở cấp độ tiếp theo
- 3: Đạt 100% tiêu chuẩn yêu cầu ở cấp độ hiện tại
- 2: Đạt từ 50% trở lên tiêu chuẩn yêu cầu ở cấp độ hiện tại
- 1: Chưa đạt 50% tiêu chuẩn yêu cầu ở cấp độ hiện tại
"""

_NEXT_GRADE = {"G0": "G1", "G1": "G2", "G2": "G3", "G3": "G4", "G4": "G5", "G5": "G6"}


def _build_prompt(sheet: dict, previous_sheet: dict | None) -> str:
    position = sheet.get("position", "")
    grade = sheet.get("grade", "G0")
    next_grade = _NEXT_GRADE.get(grade)

    # Get detailed skill descriptions for current and next level
    current_skills = SKILL_KB.get(position, {}).get(grade, {})
    next_skills = SKILL_KB.get(position, {}).get(next_grade, {}) if next_grade else {}

    current_skills_text = "\n".join(f"  - {k}: {v}" for k, v in current_skills.items() if v)
    next_skills_text = "\n".join(f"  - {k}: {v}" for k, v in next_skills.items() if v) if next_skills else ""

    prev_scores_text = ""
    if previous_sheet:
        prev_scores_text = f"\nĐiểm kỳ trước ({previous_sheet.get('period', '')}):\n{json.dumps(previous_sheet.get('scoring_criteria', {}), ensure_ascii=False, indent=2)}\n"

    # Historical scores from G Level tab
    historical_text = ""
    historical = sheet.get("historical_scores", {})
    if historical:
        historical_text = f"\nĐiểm lịch sử từ G Level (các kỳ trước):\n{json.dumps(historical, ensure_ascii=False, indent=2)}\n"

    comments_text = ""
    comments = sheet.get("comments", [])
    if comments:
        comments_text = f"\nComment tự đánh giá của nhân viên:\n" + "\n".join(f"  - {c}" for c in comments[:10])

    return f"""Bạn là AI hỗ trợ HR đánh giá nhân viên tại LIFULL Tech Vietnam.

Thông tin nhân viên:
- Tên: {sheet.get('employee_name', '')}
- Vị trí: {position}
- Cấp độ hiện tại: {grade}
- Kỳ đánh giá: {sheet.get('period', '')}

{SCORING_RUBRIC}

Tiêu chuẩn kỹ năng chuyên môn ở cấp độ hiện tại ({grade}):
{current_skills_text}

{f"Tiêu chuẩn kỹ năng chuyên môn ở cấp độ tiếp theo ({next_grade}):" if next_grade else "Đây là cấp độ cao nhất."}
{next_skills_text}

Điểm tự đánh giá kỳ này:
{json.dumps(sheet.get('scoring_criteria', {}), ensure_ascii=False, indent=2)}
{prev_scores_text}{historical_text}{comments_text}

Quy tắc tính điểm khi lên level:
{GRADE_CARRY_FORWARD_RULES}

Hãy viết phản hồi bằng tiếng Việt gồm 2 phần:
1. **Feedback** (3-5 câu): Nhận xét kết quả kỳ này — điểm mạnh, điểm yếu, so sánh với kỳ trước nếu có. Đối chiếu điểm tự đánh giá với tiêu chuẩn cấp độ hiện tại.
2. **Recommend** (3-5 câu): Gợi ý cụ thể skill nào cần cải thiện{f" để hướng tới {next_grade}" if next_grade else ""}. Dựa trên tiêu chuẩn cấp độ tiếp theo để chỉ ra gap cần lấp.

Trả về JSON:
{{
  "feedback": "...",
  "recommend": "..."
}}"""


def generate_feedback_and_recommend(sheet: dict, previous_sheet: dict | None = None) -> dict:
    """Call Gemini to generate feedback and recommendations for an employee's evaluation sheet."""
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return _mock_response(sheet)

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={"response_mime_type": "application/json"},
        )
        response = model.generate_content(_build_prompt(sheet, previous_sheet))
        return json.loads(response.text)
    except Exception as e:
        return {"feedback": f"[AI Error] {e}", "recommend": ""}


def _mock_response(sheet: dict) -> dict:
    name = sheet.get("employee_name", "Nhân viên")
    grade = sheet.get("grade", "G0")
    next_grade = _NEXT_GRADE.get(grade)
    scores = sheet.get("scoring_criteria", {})
    top_skill = max(scores, key=scores.get) if scores else "các kỹ năng"

    return {
        "feedback": (
            f"[MOCK AI] {name} đã hoàn thành kỳ đánh giá {grade} với điểm nổi bật ở {top_skill}. "
            "Nhìn chung kết quả phản ánh đúng năng lực hiện tại."
        ),
        "recommend": (
            f"[MOCK AI] Để chuẩn bị cho {next_grade}, hãy tập trung phát triển thêm các kỹ năng còn thấp điểm "
            "và chủ động nhận thêm trách nhiệm trong dự án."
        ) if next_grade else "[MOCK AI] Đây là cấp độ cao nhất. Hãy tiếp tục duy trì và chia sẻ kinh nghiệm cho team.",
    }
