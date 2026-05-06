"""init schema and seed data

Revision ID: 0001
Revises:
Create Date: 2026-05-04
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.create_table(
        "roles",
        sa.Column("id",          sa.String(36),  primary_key=True),
        sa.Column("name",        sa.String(50),  nullable=False, unique=True),
        sa.Column("permissions", JSONB,          nullable=False),
        sa.Column("created_at",  sa.DateTime,    server_default=sa.func.now()),
    )

    op.create_table(
        "teams",
        sa.Column("id",        sa.String(36),  primary_key=True),
        sa.Column("name",      sa.String(100), nullable=False),
        sa.Column("parent_id", sa.String(36),  sa.ForeignKey("teams.id"), nullable=True),
        sa.Column("type",      sa.String(10),  nullable=False),
        sa.CheckConstraint("type IN ('UNIT','GROUP')", name="ck_team_type"),
    )

    op.create_table(
        "users",
        sa.Column("id",         sa.String(36),  primary_key=True),
        sa.Column("email",      sa.String(100), nullable=False, unique=True),
        sa.Column("password",   sa.String(255), nullable=False),
        sa.Column("full_name",  sa.String(100), nullable=False),
        sa.Column("role_id",    sa.String(36),  sa.ForeignKey("roles.id"),  nullable=False),
        sa.Column("team_id",    sa.String(36),  sa.ForeignKey("teams.id"),  nullable=True),
        sa.Column("manager_id", sa.String(36),  sa.ForeignKey("users.id"),  nullable=True),
        sa.Column("status",     sa.String(10),  server_default="active"),
        sa.Column("deleted_at", sa.DateTime,    nullable=True),
        sa.CheckConstraint("status IN ('active','inactive')", name="ck_user_status"),
    )

    op.create_table(
        "evaluation_periods",
        sa.Column("id",         sa.String(36),  primary_key=True),
        sa.Column("name",       sa.String(100), nullable=False),
        sa.Column("start_date", sa.Date,        nullable=False),
        sa.Column("end_date",   sa.Date,        nullable=False),
        sa.Column("folder_id",  sa.String(100), nullable=True),
        sa.Column("status",     sa.String(10),  server_default="active"),
        sa.Column("created_at", sa.DateTime,    server_default=sa.func.now()),
        sa.CheckConstraint("status IN ('active','closed')", name="ck_period_status"),
    )

    op.create_table(
        "templates",
        sa.Column("id",             sa.String(36),  primary_key=True),
        sa.Column("name",           sa.String(100), nullable=False),
        sa.Column("google_file_id", sa.String(100), nullable=False),
        sa.Column("description",    sa.Text,        nullable=True),
        sa.Column("created_at",     sa.DateTime,    server_default=sa.func.now()),
        sa.Column("updated_at",     sa.DateTime,    server_default=sa.func.now()),
    )

    op.create_table(
        "evaluations",
        sa.Column("id",                 sa.String(36),  primary_key=True),
        sa.Column("employee_id",        sa.String(36),  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("template_id",        sa.String(36),  sa.ForeignKey("templates.id"),          nullable=False),
        sa.Column("period_id",          sa.String(36),  sa.ForeignKey("evaluation_periods.id"), nullable=False),
        sa.Column("spreadsheet_id",     sa.String(100), nullable=False),
        sa.Column("spreadsheet_url",    sa.Text,        nullable=False),
        sa.Column("status",             sa.String(30),  server_default="Self_Evaluating"),
        sa.Column("current_handler_id", sa.String(36),  sa.ForeignKey("users.id"), nullable=True),
        sa.Column("final_score",        sa.Float,       nullable=True),
        sa.Column("rank",               sa.String(10),  nullable=True),
        sa.Column("created_at",         sa.DateTime,    server_default=sa.func.now()),
        sa.Column("updated_at",         sa.DateTime,    server_default=sa.func.now()),
        sa.Column("deleted_at",         sa.DateTime,    nullable=True),
        sa.CheckConstraint(
            "status IN ('Self_Evaluating','Leader_Reviewing','Manager_Reviewing','Completed')",
            name="ck_eval_status"
        ),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id",          sa.String(36),  primary_key=True, server_default=sa.text("gen_random_uuid()::text")),
        sa.Column("actor_id",    sa.String(36),  sa.ForeignKey("users.id"), nullable=False),
        sa.Column("action",      sa.String(50),  nullable=False),
        sa.Column("target_type", sa.String(50),  nullable=False),
        sa.Column("target_id",   sa.String(36),  nullable=True),
        sa.Column("details",     JSONB,          nullable=True),
        sa.Column("created_at",  sa.DateTime,    server_default=sa.func.now()),
    )
    op.create_index("idx_audit_actor_time", "audit_logs", ["actor_id", "created_at"])
    op.create_index("idx_audit_action",     "audit_logs", ["action"])

    # ── Seed data ──────────────────────────────────────────────────────────────
    op.execute("""
        INSERT INTO roles (id, name, permissions) VALUES
        ('R1', 'CEO',          '{"all": true, "view_all": true, "manage_all": true}'),
        ('R2', 'HR',           '{"manage_all": true, "view_all": true, "export_reports": true}'),
        ('R3', 'Unit Manager', '{"view_unit": true, "manage_unit": true, "approve_evaluations": true}'),
        ('R4', 'Group Leader', '{"view_group": true, "manage_group": true, "review_evaluations": true}'),
        ('R5', 'Member',       '{"view_self": true, "edit_self": true}')
    """)

    op.execute("""
        INSERT INTO teams (id, name, parent_id, type) VALUES
        ('U1',   'Software Development Unit 1',   NULL, 'UNIT'),
        ('U2',   'Software Development Unit 2',   NULL, 'UNIT'),
        ('U3',   'Software Development Unit 3',   NULL, 'UNIT'),
        ('U5',   'Software Development Unit 5',   NULL, 'UNIT'),
        ('UDIV', 'Software Development Division', NULL, 'UNIT'),
        ('G_CHINTAI',   'Chintai Group',           'U1', 'GROUP'),
        ('G_RYUTSU',    'Ryutsu Group',             'U1', 'GROUP'),
        ('G_ADM',       'ADM/CRM Group',            'U1', 'GROUP'),
        ('G_KODATE',    'Kodate Group',             'U2', 'GROUP'),
        ('G_MANSION',   'Mansion Group',            'U2', 'GROUP'),
        ('G_BAIKYAKU',  'Baikyaku Group',           'U2', 'GROUP'),
        ('G_CHUMON',    'Chumon Group',             'U3', 'GROUP'),
        ('G_APP',       'App Group',                'U3', 'GROUP'),
        ('G_MADOGUCHI', 'Madoguchi Group',          'U3', 'GROUP'),
        ('G_MANAGER',   'Manager Group',            'U5', 'GROUP'),
        ('G_CHANNEL',   'Channel Group',            'U5', 'GROUP'),
        ('G_ODAN',      'Odan/SRE Group',           'U5', 'GROUP'),
        ('G_QA',        'QA Group',                 'U5', 'GROUP'),
        ('G_SALESFORCE','Salesforce Group',         'U5', 'GROUP'),
        ('G_RAKUTEN',   'Rakuten Group',            'U5', 'GROUP'),
        ('G_LX',        'LX Group',                 'U5', 'GROUP'),
        ('G_LISTING',   'Listing Screening Group',  'U5', 'GROUP'),
        ('G_TEMP',      'Temporary Group',          'U5', 'GROUP')
    """)

    op.execute("""
        INSERT INTO users (id, email, password, full_name, role_id, team_id, manager_id) VALUES
        ('U106', 'sondv@lifull.com',      crypt('sondv@123', gen_salt('bf')),      'Đặng Văn Sơn',          'R1', 'UDIV',       NULL),
        ('U85',  'hienttn@lifull.com',    crypt('hienttn@123', gen_salt('bf')),    'Trịnh Thị Như Hiền',    'R3', 'U1',         'U106'),
        ('U187', 'tripm@lifull.com',      crypt('tripm@123', gen_salt('bf')),      'Phan Minh Trí',          'R3', 'U2',         'U106'),
        ('U139', 'ducnt@lifull.com',      crypt('ducnt@123', gen_salt('bf')),      'Nguyễn Trung Đức',      'R3', 'U3',         'U106'),
        ('U158', 'haoln@lifull.com',      crypt('haoln@123', gen_salt('bf')),      'Lê Ngọc Hảo',           'R3', 'U5',         'U106'),
        ('U74',  'xuandd@lifull.com',     crypt('xuandd@123', gen_salt('bf')),     'Đinh Diễm Xuân',        'R4', 'G_CHINTAI',  'U85'),
        ('U209', 'thanglt@lifull.com',    crypt('thanglt@123', gen_salt('bf')),    'Lê Tấn Thắng',          'R4', 'G_RYUTSU',   'U85'),
        ('U132', 'phongdh@lifull.com',    crypt('phongdh@123', gen_salt('bf')),    'Đỗ Hoàng Phong',        'R4', 'G_ADM',      'U85'),
        ('U10',  'hienl@lifull.com',      crypt('hienl@123', gen_salt('bf')),      'Lâm Hiền',               'R4', 'G_CHUMON',   'U139'),
        ('U131', 'nhatdt@lifull.com',     crypt('nhatdt@123', gen_salt('bf')),     'Đỗ Thanh Nhật',         'R4', 'G_MADOGUCHI','U139'),
        ('U174', 'hiendt@lifull.com',     crypt('hiendt@123', gen_salt('bf')),     'Đặng Thế Hiền',         'R4', 'G_MANAGER',  'U158'),
        ('U172', 'baolq@lifull.com',      crypt('baolq@123', gen_salt('bf')),      'Lưu Quốc Bảo',          'R4', 'G_CHANNEL',  'U158'),
        ('U199', 'anhvp@lifull.com',      crypt('anhvp@123', gen_salt('bf')),      'Võ Phương Anh',         'R4', 'G_ODAN',     'U158'),
        ('U155', 'hienntt@lifull.com',    crypt('hienntt@123', gen_salt('bf')),    'Ngô Thị Thái Hiền',     'R4', 'G_QA',       'U158'),
        ('U35',  'haimv@lifull.com',      crypt('haimv@123', gen_salt('bf')),      'Mai Văn Hải',            'R5', 'G_CHINTAI',  'U74'),
        ('U148', 'thinhnt@lifull.com',    crypt('thinhnt@123', gen_salt('bf')),    'Nguyễn Tiến Thịnh',     'R5', 'G_CHINTAI',  'U74'),
        ('U191', 'truongkx@lifull.com',   crypt('truongkx@123', gen_salt('bf')),   'Khương Xuân Trường',    'R5', 'G_CHINTAI',  'U74'),
        ('U224', 'thanhhvv@lifull.com',   crypt('thanhhvv@123', gen_salt('bf')),   'Hồ Viết Vũ Thanh',      'R5', 'G_CHINTAI',  'U74'),
        ('U46',  'giangnt@lifull.com',    crypt('giangnt@123', gen_salt('bf')),    'Nguyễn Trường Giang',   'R5', 'G_RYUTSU',   'U209'),
        ('U96',  'toailc@lifull.com',     crypt('toailc@123', gen_salt('bf')),     'Lương Công Toại',        'R5', 'G_RYUTSU',   'U209'),
        ('U180', 'sonnc@lifull.com',      crypt('sonnc@123', gen_salt('bf')),      'Nguyễn Công Sơn',        'R5', 'G_RYUTSU',   'U209'),
        ('U185', 'ngoclth@lifull.com',    crypt('ngoclth@123', gen_salt('bf')),    'Lê Thị Hồng Ngọc',      'R5', 'G_RYUTSU',   'U209'),
        ('U210', 'khanhpv@lifull.com',    crypt('khanhpv@123', gen_salt('bf')),    'Phạm Văn Khánh',         'R5', 'G_RYUTSU',   'U209'),
        ('U214', 'tiendk@lifull.com',     crypt('tiendk@123', gen_salt('bf')),     'Đặng Kim Tiến',          'R5', 'G_RYUTSU',   'U209'),
        ('U16',  'vunh@lifull.com',       crypt('vunh@123', gen_salt('bf')),       'Nguyễn Hoàng Vũ',        'R5', 'G_ADM',      'U132'),
        ('U23',  'kienhn@lifull.com',     crypt('kienhn@123', gen_salt('bf')),     'Hoàng Ngọc Kiên',        'R5', 'G_ADM',      'U132'),
        ('U80',  'khoand@lifull.com',     crypt('khoand@123', gen_salt('bf')),     'Nguyễn Đăng Khoa',       'R5', 'G_ADM',      'U132'),
        ('U133', 'hieunk@lifull.com',     crypt('hieunk@123', gen_salt('bf')),     'Nguyễn Khắc Hiếu',      'R5', 'G_ADM',      'U132'),
        ('U173', 'trungdq@lifull.com',    crypt('trungdq@123', gen_salt('bf')),    'Đoàn Quang Trung',       'R5', 'G_ADM',      'U132'),
        ('U189', 'thinhps@lifull.com',    crypt('thinhps@123', gen_salt('bf')),    'Phạm Sơn Thịnh',         'R5', 'G_ADM',      'U132'),
        ('U43',  'hoangbm@lifull.com',    crypt('hoangbm@123', gen_salt('bf')),    'Bùi Minh Hoàng',         'R5', 'G_CHUMON',   'U10'),
        ('U116', 'sonhq@lifull.com',      crypt('sonhq@123', gen_salt('bf')),      'Huỳnh Quốc Sơn',         'R5', 'G_CHUMON',   'U10'),
        ('U184', 'vuvta@lifull.com',      crypt('vuvta@123', gen_salt('bf')),      'Võ Tấn Anh Vũ',          'R5', 'G_CHUMON',   'U10'),
        ('U194', 'haonm@lifull.com',      crypt('haonm@123', gen_salt('bf')),      'Nguyễn Mạnh Hào',        'R5', 'G_CHUMON',   'U10'),
        ('U197', 'trungnt@lifull.com',    crypt('trungnt@123', gen_salt('bf')),    'Nguyễn Thành Trung',     'R5', 'G_CHUMON',   'U10'),
        ('U71',  'minhtd@lifull.com',     crypt('minhtd@123', gen_salt('bf')),     'Trần Đức Minh',           'R5', 'G_KODATE',   'U187'),
        ('U100', 'trangnvm@lifull.com',   crypt('trangnvm@123', gen_salt('bf')),   'Nguyễn Võ Minh Trang',   'R5', 'G_KODATE',   'U187'),
        ('U135', 'phuongtth@lifull.com',  crypt('phuongtth@123', gen_salt('bf')),  'Trần Thị Hằng Phương',   'R5', 'G_KODATE',   'U187'),
        ('U178', 'sangpp@lifull.com',     crypt('sangpp@123', gen_salt('bf')),     'Phan Phước Sang',         'R5', 'G_KODATE',   'U187'),
        ('U193', 'thuna@lifull.com',      crypt('thuna@123', gen_salt('bf')),      'Nguyễn Anh Thư',          'R5', 'G_KODATE',   'U187'),
        ('U200', 'dathlt@lifull.com',     crypt('dathlt@123', gen_salt('bf')),     'Huỳnh Long Thành Đạt',   'R5', 'G_KODATE',   'U187'),
        ('U201', 'dudh@lifull.com',       crypt('dudh@123', gen_salt('bf')),       'Đặng Hoàng Dũ',           'R5', 'G_KODATE',   'U187'),
        ('U165', 'linhntd@lifull.com',    crypt('linhntd@123', gen_salt('bf')),    'Nguyễn Thị Diệu Linh',   'R5', 'G_MANAGER',  'U174'),
        ('U167', 'haivh@lifull.com',      crypt('haivh@123', gen_salt('bf')),      'Võ Hoàng Hải',            'R5', 'G_MANAGER',  'U174'),
        ('U181', 'tienlv@lifull.com',     crypt('tienlv@123', gen_salt('bf')),     'Lê Vũ Tiến',              'R5', 'G_MANAGER',  'U174'),
        ('U188', 'doankv@lifull.com',     crypt('doankv@123', gen_salt('bf')),     'Kiều Văn Đoàn',           'R5', 'G_MANAGER',  'U174'),
        ('U212', 'khanhld@lifull.com',    crypt('khanhld@123', gen_salt('bf')),    'Lê Đăng Khánh',           'R5', 'G_MANAGER',  'U174'),
        ('U216', 'hoanglh@lifull.com',    crypt('hoanglh@123', gen_salt('bf')),    'Lê Huy Hoàng',            'R5', 'G_MANAGER',  'U174'),
        ('U149', 'tuanpq@lifull.com',     crypt('tuanpq@123', gen_salt('bf')),     'Phan Quốc Tuấn',          'R5', 'G_ODAN',     'U199'),
        ('U171', 'annv@lifull.com',       crypt('annv@123', gen_salt('bf')),       'Nguyễn Vĩnh An',          'R5', 'G_ODAN',     'U199'),
        ('U176', 'quyenbt@lifull.com',    crypt('quyenbt@123', gen_salt('bf')),    'Bùi Tín Quyền',           'R5', 'G_ODAN',     'U199'),
        ('U213', 'lamntt@lifull.com',     crypt('lamntt@123', gen_salt('bf')),     'Nguyễn Thị Thuý Lam',    'R5', 'G_ODAN',     'U199'),
        ('U225', 'toidb@lifull.com',      crypt('toidb@123', gen_salt('bf')),      'Đặng Bá Tới',             'R5', 'G_ODAN',     'U199'),
        ('U140', 'dungdd@lifull.com',     crypt('dungdd@123', gen_salt('bf')),     'Đào Duy Dũng',            'R5', 'G_CHANNEL',  'U172'),
        ('U190', 'tiennn@lifull.com',     crypt('tiennn@123', gen_salt('bf')),     'Nguyễn Nhựt Tiến',       'R5', 'G_CHANNEL',  'U172'),
        ('U195', 'baobtg@lifull.com',     crypt('baobtg@123', gen_salt('bf')),     'Bùi Trần Gia Bảo',       'R5', 'G_CHANNEL',  'U172'),
        ('U198', 'tuanta@lifull.com',     crypt('tuanta@123', gen_salt('bf')),     'Trần Anh Tuấn',           'R5', 'G_CHANNEL',  'U172'),
        ('U211', 'namhn@lifull.com',      crypt('namhn@123', gen_salt('bf')),      'Huỳnh Nhật Nam',          'R5', 'G_CHANNEL',  'U172')
    """)

    op.execute("""
        INSERT INTO templates (id, name, google_file_id, description) VALUES
        ('TEMP_2026_Q1', 'Performance Evaluation Q1 2026', '1ABC_MASTER_TEMPLATE_ID', 'Mẫu đánh giá hiệu suất Q1/2026'),
        ('TEMP_TECH',    'Technical Skills Assessment',     '1XYZ_TECH_TEMPLATE_ID',  'Đánh giá kỹ năng kỹ thuật')
    """)

    op.execute("""
        INSERT INTO evaluation_periods (id, name, start_date, end_date, folder_id, status) VALUES
        ('PERIOD_2026_Q1', 'Đánh giá hiệu suất Q1 2026', '2026-04-01', '2026-04-30', 'FOLDER_Q1_2026_ID', 'active'),
        ('PERIOD_2026_Q2', 'Đánh giá hiệu suất Q2 2026', '2026-07-01', '2026-07-31', 'FOLDER_Q2_2026_ID', 'active')
    """)

    op.execute("""
        INSERT INTO evaluations
            (id, employee_id, template_id, period_id, spreadsheet_id, spreadsheet_url, status, current_handler_id, final_score, rank)
        VALUES
        ('EVAL_U35',  'U35',  'TEMP_2026_Q1','PERIOD_2026_Q1','SHEET_U35_Q1', 'https://docs.google.com/spreadsheets/d/SHEET_U35_Q1', 'Self_Evaluating',   'U35',  NULL, NULL),
        ('EVAL_U148', 'U148', 'TEMP_2026_Q1','PERIOD_2026_Q1','SHEET_U148_Q1','https://docs.google.com/spreadsheets/d/SHEET_U148_Q1','Leader_Reviewing',  'U74',  NULL, NULL),
        ('EVAL_U191', 'U191', 'TEMP_2026_Q1','PERIOD_2026_Q1','SHEET_U191_Q1','https://docs.google.com/spreadsheets/d/SHEET_U191_Q1','Manager_Reviewing', 'U85',  NULL, NULL),
        ('EVAL_U224', 'U224', 'TEMP_2026_Q1','PERIOD_2026_Q1','SHEET_U224_Q1','https://docs.google.com/spreadsheets/d/SHEET_U224_Q1','Completed',         'U85',  8.5,  'A'),
        ('EVAL_U46',  'U46',  'TEMP_2026_Q1','PERIOD_2026_Q1','SHEET_U46_Q1', 'https://docs.google.com/spreadsheets/d/SHEET_U46_Q1', 'Self_Evaluating',   'U46',  NULL, NULL),
        ('EVAL_U96',  'U96',  'TEMP_2026_Q1','PERIOD_2026_Q1','SHEET_U96_Q1', 'https://docs.google.com/spreadsheets/d/SHEET_U96_Q1', 'Completed',         'U85',  7.8,  'B'),
        ('EVAL_U16',  'U16',  'TEMP_2026_Q1','PERIOD_2026_Q1','SHEET_U16_Q1', 'https://docs.google.com/spreadsheets/d/SHEET_U16_Q1', 'Leader_Reviewing',  'U132', NULL, NULL),
        ('EVAL_U23',  'U23',  'TEMP_2026_Q1','PERIOD_2026_Q1','SHEET_U23_Q1', 'https://docs.google.com/spreadsheets/d/SHEET_U23_Q1', 'Completed',         'U85',  9.0,  'A'),
        ('EVAL_U43',  'U43',  'TEMP_2026_Q1','PERIOD_2026_Q1','SHEET_U43_Q1', 'https://docs.google.com/spreadsheets/d/SHEET_U43_Q1', 'Self_Evaluating',   'U43',  NULL, NULL),
        ('EVAL_U116', 'U116', 'TEMP_2026_Q1','PERIOD_2026_Q1','SHEET_U116_Q1','https://docs.google.com/spreadsheets/d/SHEET_U116_Q1','Manager_Reviewing', 'U139', NULL, NULL)
    """)

    op.execute("""
        INSERT INTO audit_logs (actor_id, action, target_type, target_id, details) VALUES
        ('U35',  'VIEW_FILE',          'EVALUATION', 'EVAL_U35',  '{"ip": "192.168.1.100", "user_agent": "Chrome/120"}'),
        ('U74',  'UPDATE_STATUS',      'EVALUATION', 'EVAL_U148', '{"old_status": "Self_Evaluating", "new_status": "Leader_Reviewing"}'),
        ('U85',  'APPROVE_EVALUATION', 'EVALUATION', 'EVAL_U224', '{"final_score": 8.5, "rank": "A"}'),
        ('U106', 'EXPORT_REPORT',      'EVALUATION', NULL,        '{"period": "PERIOD_2026_Q1", "format": "PDF"}')
    """)


def downgrade():
    op.drop_table("audit_logs")
    op.drop_table("evaluations")
    op.drop_table("evaluation_periods")
    op.drop_table("templates")
    op.drop_table("users")
    op.drop_table("teams")
    op.drop_table("roles")
