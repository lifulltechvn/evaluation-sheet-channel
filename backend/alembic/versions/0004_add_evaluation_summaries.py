"""add evaluation_summaries table

Revision ID: 0004
Revises: 0003
Create Date: 2026-05-11
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE TABLE evaluation_summaries (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            evaluation_id UUID NOT NULL UNIQUE REFERENCES evaluations(id) ON DELETE CASCADE,
            employee_id UUID NOT NULL REFERENCES users(id),
            period_id UUID NOT NULL REFERENCES evaluation_periods(id),
            skills_score JSONB NOT NULL,
            total_average FLOAT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Seed fake data for testing
    op.execute("""
        INSERT INTO evaluation_summaries (evaluation_id, employee_id, period_id, skills_score, total_average)
        VALUES (
            'EVAL_U224',
            'U224',
            '1',
            '{"チームマネジメント Quản lý team": null, "課題解決能力 要求定義に対する評価 Năng lực giải quyết vấn đề Đánh giá về Định nghĩa yêu cầu business": null, "要件・仕様に対する評価 Đánh giá yêu cầu hệ thống-Specs": 3, "アプリケーション設計レビュー Review thiết kế ứng dụng": 4, "テスト計画 Lên kế hoạch test": 2, "タスク管理 Quản lý task": 5, "テスト項目作成 Tạo test case": 3, "テスト項目レビュー Review test case": 4, "テスト実行・不具合起票/分析・結果レビュー Thực hiện test - Báo cáo/Phân tích lỗi - Đánh giá kết quả": 2, "開発工程改善 Cải thiện công đoạn phát triển": 5, "Foundation Nền tảng": 3, "Advance Nâng cao": 4}',
            3.5
        );
    """)


def downgrade():
    op.drop_table("evaluation_summaries")
