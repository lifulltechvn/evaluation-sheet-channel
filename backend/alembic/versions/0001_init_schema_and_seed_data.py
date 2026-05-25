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
        sa.Column("id",          sa.String(36),  primary_key=True),
        sa.Column("email",       sa.String(100), nullable=False, unique=True),
        sa.Column("password",    sa.String(255), nullable=False),
        sa.Column("full_name",   sa.String(100), nullable=False),
        sa.Column("role_id",     sa.String(36),  sa.ForeignKey("roles.id"),  nullable=False),
        sa.Column("team_id",     sa.String(36),  sa.ForeignKey("teams.id"),  nullable=True),
        sa.Column("manager_id",  sa.String(36),  sa.ForeignKey("users.id"),  nullable=True),
        sa.Column("template_id", sa.String(36),  nullable=True),
        sa.Column("current_rank",sa.String(10),  nullable=True),
        sa.Column("status",      sa.String(10),  server_default="active"),
        sa.Column("deleted_at",  sa.DateTime,    nullable=True),
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
        ('G_TEMP',      'Temporary Group',          'U5', 'GROUP'),
        ('UBOD',        'Back Office Division',     NULL, 'UNIT'),
        ('G_HR',        'HR Group',                 'UBOD', 'GROUP'),
        ('G_ADMIN',     'Admin Group',              'UBOD', 'GROUP'),
        ('G_FINANCE',   'Finance/Accounting Group', 'UBOD', 'GROUP')
    """)

    op.execute("""
        INSERT INTO users (id, email, password, full_name, role_id, team_id, manager_id, template_id, current_rank) VALUES
        ('U106', 'sondv@lifull.com', crypt('sondv@123', gen_salt('bf')), 'Đặng Văn Sơn', 'R1', 'UDIV', NULL, '2', NULL),
        ('U141', 'vyndn@lifull.com', crypt('vyndn@123', gen_salt('bf')), 'Nguyễn Đặng Như Vy', 'R1', 'UBOD', NULL, NULL, NULL),
        ('U192', 'katoyuta@lifull.com', crypt('katoyuta@123', gen_salt('bf')), 'Kato Yuta', 'R1', 'UDIV', NULL, NULL, 'G1'),
        ('U85', 'hienttn@lifull.com', crypt('hienttn@123', gen_salt('bf')), 'Trịnh Thị Như Hiền', 'R3', 'U1', 'U106', '2', NULL),
        ('U187', 'tripm@lifull.com', crypt('tripm@123', gen_salt('bf')), 'Phan Minh Trí', 'R3', 'U2', 'U106', '2', NULL),
        ('U139', 'ducnt@lifull.com', crypt('ducnt@123', gen_salt('bf')), 'Nguyễn Trung Đức', 'R3', 'U3', 'U106', '2', NULL),
        ('U158', 'haoln@lifull.com', crypt('haoln@123', gen_salt('bf')), 'Lê Ngọc Hảo', 'R3', 'U5', 'U106', '2', NULL),
        ('U74', 'xuandd@lifull.com', crypt('xuandd@123', gen_salt('bf')), 'Đinh Diễm Xuân', 'R4', 'G_CHINTAI', 'U85', '1', NULL),
        ('U209', 'thanglt@lifull.com', crypt('thanglt@123', gen_salt('bf')), 'Lê Tấn Thắng', 'R4', 'G_RYUTSU', 'U85', '2', NULL),
        ('U132', 'phongdh@lifull.com', crypt('phongdh@123', gen_salt('bf')), 'Đỗ Hoàng Phong', 'R4', 'G_ADM', 'U85', '1', NULL),
        ('U10', 'hienl@lifull.com', crypt('hienl@123', gen_salt('bf')), 'Lâm Hiền', 'R4', 'G_CHUMON', 'U139', '1', NULL),
        ('U131', 'nhatdt@lifull.com', crypt('nhatdt@123', gen_salt('bf')), 'Đỗ Thanh Nhật', 'R4', 'G_MADOGUCHI', 'U139', '1', NULL),
        ('U174', 'hiendt@lifull.com', crypt('hiendt@123', gen_salt('bf')), 'Đặng Thế Hiền', 'R4', 'G_MANAGER', 'U158', '2', NULL),
        ('U172', 'baolq@lifull.com', crypt('baolq@123', gen_salt('bf')), 'Lưu Quốc Bảo', 'R4', 'G_CHANNEL', 'U158', '1', NULL),
        ('U199', 'anhvp@lifull.com', crypt('anhvp@123', gen_salt('bf')), 'Võ Phương Anh', 'R4', 'G_ODAN', 'U158', '2', NULL),
        ('U155', 'hienntt@lifull.com', crypt('hienntt@123', gen_salt('bf')), 'Ngô Thị Thái Hiền', 'R4', 'G_QA', 'U158', '3', NULL),
        ('U120', 'hangptt@lifull.com', crypt('hangptt@123', gen_salt('bf')), 'Phan Thị Thúy Hằng', 'R4', 'G_ADMIN', 'U141', NULL, NULL),
        ('U169', 'haln@lifull.com', crypt('haln@123', gen_salt('bf')), 'Lê Ngân Hà', 'R4', 'G_HR', 'U141', NULL, NULL),
        ('U70', 'dunglt@lifull.com', crypt('dunglt@123', gen_salt('bf')), 'Lê Thị Dung', 'R2', 'G_FINANCE', 'U141', NULL, 'G1'),
        ('U130', 'truyenltn@lifull.com', crypt('truyenltn@123', gen_salt('bf')), 'Lê Thị Ngọc Truyền', 'R2', 'G_HR', 'U169', NULL, 'G1'),
        ('U219', 'phuongdtt@lifull.com', crypt('phuongdtt@123', gen_salt('bf')), 'Đào Thị Thuỳ Phương', 'R2', 'G_ADMIN', 'U120', NULL, 'G1'),
        ('U16', 'vunh@lifull.com', crypt('vunh@123', gen_salt('bf')), 'Nguyễn Hoàng Vũ', 'R5', 'G_ADM', 'U132', '1', 'G1'),
        ('U23', 'kienhn@lifull.com', crypt('kienhn@123', gen_salt('bf')), 'Hoàng Ngọc Kiên', 'R5', 'G_ADM', 'U132', '1', 'G1'),
        ('U35', 'haimv@lifull.com', crypt('haimv@123', gen_salt('bf')), 'Mai Văn Hải', 'R5', 'G_CHINTAI', 'U74', '1', 'G1'),
        ('U43', 'hoangbm@lifull.com', crypt('hoangbm@123', gen_salt('bf')), 'Bùi Minh Hoàng', 'R5', 'G_CHUMON', 'U10', '1', 'G1'),
        ('U46', 'giangnt@lifull.com', crypt('giangnt@123', gen_salt('bf')), 'Nguyễn Trường Giang', 'R5', 'G_RYUTSU', 'U209', '1', 'G1'),
        ('U54', 'thontm@lifull.com', crypt('thontm@123', gen_salt('bf')), 'Nguyễn Thị Minh Thơ', 'R5', 'G_SALESFORCE', NULL, '1', 'G1'),
        ('U71', 'minhtd@lifull.com', crypt('minhtd@123', gen_salt('bf')), 'Trần Đức Minh', 'R5', 'G_KODATE', NULL, '1', 'G1'),
        ('U80', 'khoand@lifull.com', crypt('khoand@123', gen_salt('bf')), 'Nguyễn Đăng Khoa', 'R5', 'G_ADM', 'U132', '1', 'G1'),
        ('U96', 'toailc@lifull.com', crypt('toailc@123', gen_salt('bf')), 'Lương Công Toại', 'R5', 'G_RYUTSU', 'U209', '1', 'G1'),
        ('U99', 'ducla@lifull.com', crypt('ducla@123', gen_salt('bf')), 'Lê Anh Đức', 'R5', 'G_LX', NULL, '1', 'G1'),
        ('U100', 'trangnvm@lifull.com', crypt('trangnvm@123', gen_salt('bf')), 'Nguyễn Võ Minh Trang', 'R5', 'G_KODATE', NULL, '1', 'G1'),
        ('U108', 'binhpc@lifull.com', crypt('binhpc@123', gen_salt('bf')), 'Phạm Chí Bình', 'R5', 'G_APP', NULL, '1', 'G1'),
        ('U110', 'trivm@lifull.com', crypt('trivm@123', gen_salt('bf')), 'Võ Minh Trí', 'R5', 'G_RAKUTEN', NULL, '1', 'G1'),
        ('U112', 'nhuptt@lifull.com', crypt('nhuptt@123', gen_salt('bf')), 'Phạm Thị Thanh Như', 'R5', 'G_SALESFORCE', NULL, '3', 'G1'),
        ('U116', 'sonhq@lifull.com', crypt('sonhq@123', gen_salt('bf')), 'Huỳnh Quốc Sơn', 'R5', 'G_CHUMON', 'U10', '2', 'G1'),
        ('U129', 'minhld@lifull.com', crypt('minhld@123', gen_salt('bf')), 'Lê Đình Minh', 'R5', 'G_RAKUTEN', NULL, '1', 'G1'),
        ('U133', 'hieunk@lifull.com', crypt('hieunk@123', gen_salt('bf')), 'Nguyễn Khắc Hiếu', 'R5', 'G_ADM', 'U132', '1', 'G1'),
        ('U135', 'phuongtth@lifull.com', crypt('phuongtth@123', gen_salt('bf')), 'Trần Thị Hằng Phương', 'R5', 'G_KODATE', NULL, '3', 'G1'),
        ('U140', 'dungdd@lifull.com', crypt('dungdd@123', gen_salt('bf')), 'Đào Duy Dũng', 'R5', 'G_CHANNEL', 'U172', '3', 'G1'),
        ('U143', 'duyenptm@lifull.com', crypt('duyenptm@123', gen_salt('bf')), 'Phan Thị Mỹ Duyên', 'R5', 'G_QA', 'U155', '3', 'G1'),
        ('U148', 'thinhnt@lifull.com', crypt('thinhnt@123', gen_salt('bf')), 'Nguyễn Tiến Thịnh', 'R5', 'G_CHINTAI', 'U74', '1', 'G1'),
        ('U149', 'tuanpq@lifull.com', crypt('tuanpq@123', gen_salt('bf')), 'Phan Quốc Tuấn', 'R5', 'G_ODAN', 'U199', '1', 'G1'),
        ('U151', 'sonpt@lifull.com', crypt('sonpt@123', gen_salt('bf')), 'Phạm Tuấn Sơn', 'R5', 'G_BAIKYAKU', NULL, '3', 'G1'),
        ('U154', 'taitna@lifull.com', crypt('taitna@123', gen_salt('bf')), 'Trần Ngọc Anh Tài', 'R5', 'G_MADOGUCHI', 'U131', '1', 'G1'),
        ('U160', 'longlh@lifull.com', crypt('longlh@123', gen_salt('bf')), 'Lê Hoàng Long', 'R5', 'G_MANSION', NULL, '1', 'G1'),
        ('U161', 'tinvt@lifull.com', crypt('tinvt@123', gen_salt('bf')), 'Võ Trí Tín', 'R5', 'G_LISTING', NULL, '1', 'G1'),
        ('U163', 'duyht21@lifull.com', crypt('duyht21@123', gen_salt('bf')), 'Huỳnh Thanh Duy', 'R5', 'G_BAIKYAKU', NULL, '1', 'G1'),
        ('U165', 'linhntd@lifull.com', crypt('linhntd@123', gen_salt('bf')), 'Nguyễn Thị Diệu Linh', 'R5', 'G_MANAGER', 'U174', '1', 'G1'),
        ('U166', 'vanttt@lifull.com', crypt('vanttt@123', gen_salt('bf')), 'Tôn Thị Thanh Vân', 'R5', 'G_BAIKYAKU', NULL, '1', 'G1'),
        ('U167', 'haivh@lifull.com', crypt('haivh@123', gen_salt('bf')), 'Võ Hoàng Hải', 'R5', 'G_MANAGER', 'U174', '1', 'G1'),
        ('U171', 'annv@lifull.com', crypt('annv@123', gen_salt('bf')), 'Nguyễn Vĩnh An', 'R5', 'G_ODAN', 'U199', '1', 'G1'),
        ('U173', 'trungdq@lifull.com', crypt('trungdq@123', gen_salt('bf')), 'Đoàn Quang Trung', 'R5', 'G_ADM', 'U132', '3', 'G1'),
        ('U175', 'quangtv@lifull.com', crypt('quangtv@123', gen_salt('bf')), 'Trịnh Văn Quang', 'R5', 'G_BAIKYAKU', NULL, '1', 'G1'),
        ('U176', 'quyenbt@lifull.com', crypt('quyenbt@123', gen_salt('bf')), 'Bùi Tín Quyền', 'R5', 'G_ODAN', 'U199', '1', 'G1'),
        ('U177', 'hoangna@lifull.com', crypt('hoangna@123', gen_salt('bf')), 'Nguyễn Anh Hoàng', 'R5', 'G_MANSION', NULL, '1', 'G1'),
        ('U178', 'sangpp@lifull.com', crypt('sangpp@123', gen_salt('bf')), 'Phan Phước Sang', 'R5', 'G_KODATE', NULL, '1', 'G1'),
        ('U180', 'sonnc@lifull.com', crypt('sonnc@123', gen_salt('bf')), 'Nguyễn Công Sơn', 'R5', 'G_RYUTSU', 'U209', '1', 'G1'),
        ('U181', 'tienlv@lifull.com', crypt('tienlv@123', gen_salt('bf')), 'Lê Vũ Tiến', 'R5', 'G_MANAGER', 'U174', '1', 'G1'),
        ('U184', 'vuvta@lifull.com', crypt('vuvta@123', gen_salt('bf')), 'Võ Tấn Anh Vũ', 'R5', 'G_CHUMON', 'U10', '1', 'G1'),
        ('U185', 'ngoclth@lifull.com', crypt('ngoclth@123', gen_salt('bf')), 'Lê Thị Hồng Ngọc', 'R5', 'G_RYUTSU', 'U209', '1', 'G1'),
        ('U188', 'doankv@lifull.com', crypt('doankv@123', gen_salt('bf')), 'Kiều Văn Đoàn', 'R5', 'G_MANAGER', 'U174', '1', 'G1'),
        ('U189', 'thinhps@lifull.com', crypt('thinhps@123', gen_salt('bf')), 'Phạm Sơn Thịnh', 'R5', 'G_ADM', 'U132', '1', 'G1'),
        ('U190', 'tiennn@lifull.com', crypt('tiennn@123', gen_salt('bf')), 'Nguyễn Nhựt Tiến', 'R5', 'G_CHANNEL', 'U172', '1', 'G1'),
        ('U191', 'truongkx@lifull.com', crypt('truongkx@123', gen_salt('bf')), 'Khương Xuân Trường', 'R5', 'G_CHINTAI', 'U74', '1', 'G1'),
        ('U193', 'thuna@lifull.com', crypt('thuna@123', gen_salt('bf')), 'Nguyễn Anh Thư', 'R5', 'G_KODATE', NULL, '1', 'G1'),
        ('U194', 'haonm@lifull.com', crypt('haonm@123', gen_salt('bf')), 'Nguyễn Mạnh Hào', 'R5', 'G_CHUMON', 'U10', '1', 'G1'),
        ('U195', 'baobtg@lifull.com', crypt('baobtg@123', gen_salt('bf')), 'Bùi Trần Gia Bảo', 'R5', 'G_CHANNEL', 'U172', '1', 'G1'),
        ('U197', 'trungnt@lifull.com', crypt('trungnt@123', gen_salt('bf')), 'Nguyễn Thành Trung', 'R5', 'G_CHUMON', 'U10', '1', 'G1'),
        ('U198', 'tuanta@lifull.com', crypt('tuanta@123', gen_salt('bf')), 'Trần Anh Tuấn', 'R5', 'G_CHANNEL', 'U172', '1', 'G1'),
        ('U200', 'dathlt@lifull.com', crypt('dathlt@123', gen_salt('bf')), 'Huỳnh Long Thành Đạt', 'R5', 'G_KODATE', NULL, '1', 'G1'),
        ('U201', 'dudh@lifull.com', crypt('dudh@123', gen_salt('bf')), 'Đặng Hoàng Dũ', 'R5', 'G_KODATE', NULL, '1', 'G1'),
        ('U202', 'phucng@lifull.com', crypt('phucng@123', gen_salt('bf')), 'Nguyễn Gia Phúc', 'R5', 'G_BAIKYAKU', NULL, '1', 'G1'),
        ('U203', 'thiendh@lifull.com', crypt('thiendh@123', gen_salt('bf')), 'Đỗ Hữu Thiện', 'R5', 'G_SALESFORCE', NULL, '1', 'G1'),
        ('U204', 'toina@lifull.com', crypt('toina@123', gen_salt('bf')), 'Nguyễn Anh Tới', 'R5', 'G_SALESFORCE', NULL, '1', 'G1'),
        ('U205', 'emmtc@lifull.com', crypt('emmtc@123', gen_salt('bf')), 'Mai Thế Chuyển Em', 'R5', 'G_BAIKYAKU', NULL, '1', 'G1'),
        ('U207', 'vyhy@lifull.com', crypt('vyhy@123', gen_salt('bf')), 'Hoàng Yến Vy', 'R5', 'G_TEMP', NULL, '2', 'G1'),
        ('U208', 'namtn@lifull.com', crypt('namtn@123', gen_salt('bf')), 'Mai Thị Ngọc Na', 'R5', 'G_MADOGUCHI', 'U131', '2', 'G1'),
        ('U210', 'khanhpv@lifull.com', crypt('khanhpv@123', gen_salt('bf')), 'Phạm Văn Khánh', 'R5', 'G_RYUTSU', 'U209', '1', 'G1'),
        ('U211', 'namhn@lifull.com', crypt('namhn@123', gen_salt('bf')), 'Huỳnh Nhật Nam', 'R5', 'G_CHANNEL', 'U172', '1', 'G1'),
        ('U212', 'khanhld@lifull.com', crypt('khanhld@123', gen_salt('bf')), 'Lê Đăng Khánh', 'R5', 'G_MANAGER', 'U174', '1', 'G1'),
        ('U213', 'lamntt@lifull.com', crypt('lamntt@123', gen_salt('bf')), 'Nguyễn Thị Thuý Lam', 'R5', 'G_ODAN', 'U199', '1', 'G1'),
        ('U214', 'tiendk@lifull.com', crypt('tiendk@123', gen_salt('bf')), 'Đặng Kim Tiến', 'R5', 'G_RYUTSU', 'U209', '1', 'G1'),
        ('U215', 'nguyenlp@lifull.com', crypt('nguyenlp@123', gen_salt('bf')), 'Lê Phúc Nguyên', 'R5', 'G_SALESFORCE', NULL, '1', 'G1'),
        ('U216', 'hoanglh@lifull.com', crypt('hoanglh@123', gen_salt('bf')), 'Lê Huy Hoàng', 'R5', 'G_MANAGER', 'U174', '1', 'G1'),
        ('U217', 'haotv@lifull.com', crypt('haotv@123', gen_salt('bf')), 'Trương Vĩ Hào', 'R5', 'G_BAIKYAKU', NULL, '1', 'G1'),
        ('U218', 'thinhn@lifull.com', crypt('thinhn@123', gen_salt('bf')), 'Nguyễn Thịnh', 'R5', 'G_MANSION', NULL, '1', 'G1'),
        ('U220', 'gianth@lifull.com', crypt('gianth@123', gen_salt('bf')), 'Nguyễn Tài Hoàng Gia', 'R5', 'G_MADOGUCHI', 'U131', '1', 'G1'),
        ('U221', 'namph@lifull.com', crypt('namph@123', gen_salt('bf')), 'Phan Hoàng Nam', 'R5', 'G_APP', NULL, '1', 'G1'),
        ('U222', 'longlp@lifull.com', crypt('longlp@123', gen_salt('bf')), 'Lê Phi Long', 'R5', 'G_BAIKYAKU', NULL, '1', 'G1'),
        ('U223', 'minhnbh@lifull.com', crypt('minhnbh@123', gen_salt('bf')), 'Nguyễn Bảo Hồng Minh', 'R5', 'G_MANSION', NULL, '1', 'G1'),
        ('U224', 'thanhhvv@lifull.com', crypt('thanhhvv@123', gen_salt('bf')), 'Hồ Viết Vũ Thanh', 'R5', 'G_CHINTAI', 'U74', '1', 'G1'),
        ('U225', 'toidb@lifull.com', crypt('toidb@123', gen_salt('bf')), 'Đặng Bá Tới', 'R5', 'G_ODAN', 'U199', '1', 'G1')
    """)

    op.execute("""
        INSERT INTO templates (id, name, google_file_id, description) VALUES
        ('1', 'Application Engineer',    '1v9fLMy3sRFgbOZVww5PVzlKajZshatMKHKlbygxX2N0', 'Template đánh giá Application Engineer'),
        ('2', 'Bridge System Engineer',  '1pC0s7jwXVBtw2rfjCPCzMeWfuqLgbAsUCQME-zKyVg0', 'Template đánh giá Bridge System Engineer'),
        ('3', 'QA Engineer',             '1nitoS6cOurt6_FmR6j7xVVDNVzXMwOnNZ2VGXYwie5k', 'Template đánh giá QA Engineer')
    """)

    op.execute("""
        INSERT INTO evaluation_periods (id, name, start_date, end_date, folder_id, status) VALUES
        ('1', 'FY2026', '2026-04-01', '2027-03-31', '1EKSlX08sk_prgOFT2SSthlCWWUhFs3tH', 'active'),
        ('2', 'FY2027', '2027-04-01', '2028-03-31', '1tmaw3ve7g0SSdbdMDzP56XhFiCCBhmqF', 'active')
    """)

    op.execute("""
        INSERT INTO evaluations
            (id, employee_id, template_id, period_id, spreadsheet_id, spreadsheet_url, status, current_handler_id, final_score, rank)
        VALUES
        ('EVAL_U35',  'U35',  '1','1','SHEET_U35_Q1', 'https://docs.google.com/spreadsheets/d/SHEET_U35_Q1', 'Self_Evaluating',   'U35',  NULL, 'G1'),
        ('EVAL_U148', 'U148', '1','1','SHEET_U148_Q1','https://docs.google.com/spreadsheets/d/SHEET_U148_Q1','Leader_Reviewing',  'U74',  2.33, 'G1'),
        ('EVAL_U191', 'U191', '1','1','SHEET_U191_Q1','https://docs.google.com/spreadsheets/d/SHEET_U191_Q1','Manager_Reviewing', 'U85',  2.75, 'G1'),
        ('EVAL_U224', 'U224', '1','1','SHEET_U224_Q1','https://docs.google.com/spreadsheets/d/SHEET_U224_Q1','Completed',         'U85',  3.58, 'G1'),
        ('EVAL_U46',  'U46',  '1','1','SHEET_U46_Q1', 'https://docs.google.com/spreadsheets/d/SHEET_U46_Q1', 'Self_Evaluating',   'U46',  NULL, 'G1'),
        ('EVAL_U96',  'U96',  '1','1','SHEET_U96_Q1', 'https://docs.google.com/spreadsheets/d/SHEET_U96_Q1', 'Completed',         'U85',  3.25, 'G1'),
        ('EVAL_U16',  'U16',  '1','1','SHEET_U16_Q1', 'https://docs.google.com/spreadsheets/d/SHEET_U16_Q1', 'Leader_Reviewing',  'U132', NULL, 'G1'),
        ('EVAL_U23',  'U23',  '1','1','SHEET_U23_Q1', 'https://docs.google.com/spreadsheets/d/SHEET_U23_Q1', 'Completed',         'U85',  4.5,  'G1'),
        ('EVAL_U43',  'U43',  '1','1','SHEET_U43_Q1', 'https://docs.google.com/spreadsheets/d/SHEET_U43_Q1', 'Self_Evaluating',   'U43',  NULL, 'G1'),
        ('EVAL_U116', 'U116', '2','1','SHEET_U116_Q1','https://docs.google.com/spreadsheets/d/SHEET_U116_Q1','Manager_Reviewing', 'U139', 3.33, 'G1'),
        ('EVAL_U85',  'U85',  '2','1','SHEET_U85_Q1', 'https://docs.google.com/spreadsheets/d/SHEET_U85_Q1', 'Completed',         'U106', 4.67, 'G1'),
        ('EVAL_U187', 'U187', '2','1','SHEET_U187_Q1','https://docs.google.com/spreadsheets/d/SHEET_U187_Q1','Completed',         'U106', 3.42, 'G1'),
        ('EVAL_U209', 'U209', '2','1','SHEET_U209_Q1','https://docs.google.com/spreadsheets/d/SHEET_U209_Q1','Manager_Reviewing', 'U85',  3.33, 'G1'),
        ('EVAL_U207', 'U207', '2','1','SHEET_U207_Q1','https://docs.google.com/spreadsheets/d/SHEET_U207_Q1','Leader_Reviewing',  NULL,   2.33, 'G1'),
        ('EVAL_U155', 'U155', '3','1','SHEET_U155_Q1','https://docs.google.com/spreadsheets/d/SHEET_U155_Q1','Completed',         'U158', 4.0,  'G1'),
        ('EVAL_U143', 'U143', '3','1','SHEET_U143_Q1','https://docs.google.com/spreadsheets/d/SHEET_U143_Q1','Leader_Reviewing',  'U155', 3.0,  'G1')
    """)

    op.execute("""
        INSERT INTO audit_logs (actor_id, action, target_type, target_id, details) VALUES
        ('U35',  'VIEW_FILE',          'EVALUATION', 'EVAL_U35',  '{"ip": "192.168.1.100", "user_agent": "Chrome/120"}'),
        ('U74',  'UPDATE_STATUS',      'EVALUATION', 'EVAL_U148', '{"old_status": "Self_Evaluating", "new_status": "Leader_Reviewing"}'),
        ('U85',  'APPROVE_EVALUATION', 'EVALUATION', 'EVAL_U224', '{"final_score": 8.5, "rank": "A"}'),
        ('U106', 'EXPORT_REPORT',      'EVALUATION', NULL,        '{"period": "1", "format": "PDF"}')
    """)

    op.create_foreign_key("fk_users_template_id", "users", "templates", ["template_id"], ["id"])


def downgrade():
    op.drop_table("audit_logs")
    op.drop_table("evaluations")
    op.drop_table("evaluation_periods")
    op.drop_table("templates")
    op.drop_table("users")
    op.drop_table("teams")
    op.drop_table("roles")
