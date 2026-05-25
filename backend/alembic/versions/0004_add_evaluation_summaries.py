"""add evaluation_summaries table

Revision ID: 0004
Revises: 0003
Create Date: 2026-05-11
"""
from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE TABLE evaluation_summaries (
            id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
            evaluation_id VARCHAR(36) NOT NULL UNIQUE REFERENCES evaluations(id) ON DELETE CASCADE,
            employee_id VARCHAR(36) NOT NULL REFERENCES users(id),
            period_id VARCHAR(36) NOT NULL REFERENCES evaluation_periods(id),
            skills_score JSONB NOT NULL,
            total_average FLOAT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Seed fake data for testing
    op.execute("""
        INSERT INTO evaluation_summaries (evaluation_id, employee_id, period_id, skills_score, total_average)
        VALUES
        (
            'EVAL_U224', 'U224', '1',
            '{"プログラミング Programming": 4, "データストア Data Store": 4, "テスティング Testing": 3, "アーキテクチャー (設計思想、設計方式) Architecture (Tư duy thiết kế, phương pháp thiết kế)": 4, "サーバー・ミドルウェア Server-Middleware": 3, "インフラ・ネットワーク Infrastructure-Network": 3, "セキュリティ Security": 4, "フロントエンド Frontend": 4, "要件定義・仕様作成 Định nghĩa yêu cầu-Tạo mô tả chức năng": 3, "スケジュール管理 Quản lý tiến độ": 4, "データ分析 Data Analysis": 3, "改善提案 Đề xuất ý kiến cải thiện": 4}',
            3.58
        ),
        (
            'EVAL_U96', 'U96', '1',
            '{"プログラミング Programming": 4, "データストア Data Store": 3, "テスティング Testing": 4, "アーキテクチャー (設計思想、設計方式) Architecture (Tư duy thiết kế, phương pháp thiết kế)": 3, "サーバー・ミドルウェア Server-Middleware": 3, "インフラ・ネットワーク Infrastructure-Network": 3, "セキュリティ Security": 3, "フロントエンド Frontend": 3, "要件定義・仕様作成 Định nghĩa yêu cầu-Tạo mô tả chức năng": 4, "スケジュール管理 Quản lý tiến độ": 3, "データ分析 Data Analysis": 3, "改善提案 Đề xuất ý kiến cải thiện": 3}',
            3.25
        ),
        (
            'EVAL_U23', 'U23', '1',
            '{"プログラミング Programming": 5, "データストア Data Store": 5, "テスティング Testing": 4, "アーキテクチャー (設計思想、設計方式) Architecture (Tư duy thiết kế, phương pháp thiết kế)": 5, "サーバー・ミドルウェア Server-Middleware": 4, "インフラ・ネットワーク Infrastructure-Network": 4, "セキュリティ Security": 5, "フロントエンド Frontend": 4, "要件定義・仕様作成 Định nghĩa yêu cầu-Tạo mô tả chức năng": 5, "スケジュール管理 Quản lý tiến độ": 4, "データ分析 Data Analysis": 4, "改善提案 Đề xuất ý kiến cải thiện": 5}',
            4.5
        ),
        (
            'EVAL_U191', 'U191', '1',
            '{"プログラミング Programming": 3, "データストア Data Store": 3, "テスティング Testing": 3, "アーキテクチャー (設計思想、設計方式) Architecture (Tư duy thiết kế, phương pháp thiết kế)": 2, "サーバー・ミドルウェア Server-Middleware": 3, "インフラ・ネットワーク Infrastructure-Network": 2, "セキュリティ Security": 3, "フロントエンド Frontend": 3, "要件定義・仕様作成 Định nghĩa yêu cầu-Tạo mô tả chức năng": 3, "スケジュール管理 Quản lý tiến độ": 3, "データ分析 Data Analysis": 2, "改善提案 Đề xuất ý kiến cải thiện": 3}',
            2.75
        ),
        (
            'EVAL_U148', 'U148', '1',
            '{"プログラミング Programming": 3, "データストア Data Store": 2, "テスティング Testing": 3, "アーキテクチャー (設計思想、設計方式) Architecture (Tư duy thiết kế, phương pháp thiết kế)": 2, "サーバー・ミドルウェア Server-Middleware": 2, "インフラ・ネットワーク Infrastructure-Network": 2, "セキュリティ Security": 2, "フロントエンド Frontend": 3, "要件定義・仕様作成 Định nghĩa yêu cầu-Tạo mô tả chức năng": 2, "スケジュール管理 Quản lý tiến độ": 3, "データ分析 Data Analysis": 2, "改善提案 Đề xuất ý kiến cải thiện": 2}',
            2.33
        ),
        (
            'EVAL_U116', 'U116', '1',
            '{"調整力・推進力 Năng lực điều phối - năng lực thúc đẩy": 3, "要求定義・要件定義・仕様策定 Định nghĩa yêu cầu business - Định nghĩa yêu cầu hệ thống - Xác định spec": 4, "見積策定・工程管理 Estimation - Quản lý tiến độ": 4, "運用設計 Operational Design": 3, "データストア Data Store": 4, "インフラ・ネットワーク Infra - Network": 3, "セキュリティ Security": 3, "データ分析 Data Analysis": 3, "改善提案 Đề xuất cải thiện": 3, "日本語能力 Năng lực tiếng Nhật": 4, "品質保証 Đảm bảo chất lượng": 3, "改善提案 Đề xuất ý kiến cải thiện": 3}',
            3.33
        ),
        (
            'EVAL_U85', 'U85', '1',
            '{"調整力・推進力 Năng lực điều phối - năng lực thúc đẩy": 5, "要求定義・要件定義・仕様策定 Định nghĩa yêu cầu business - Định nghĩa yêu cầu hệ thống - Xác định spec": 5, "見積策定・工程管理 Estimation - Quản lý tiến độ": 5, "運用設計 Operational Design": 4, "データストア Data Store": 5, "インフラ・ネットワーク Infra - Network": 4, "セキュリティ Security": 5, "データ分析 Data Analysis": 4, "改善提案 Đề xuất cải thiện": 5, "日本語能力 Năng lực tiếng Nhật": 5, "品質保証 Đảm bảo chất lượng": 4, "改善提案 Đề xuất ý kiến cải thiện": 5}',
            4.67
        ),
        (
            'EVAL_U187', 'U187', '1',
            '{"調整力・推進力 Năng lực điều phối - năng lực thúc đẩy": 4, "要求定義・要件定義・仕様策定 Định nghĩa yêu cầu business - Định nghĩa yêu cầu hệ thống - Xác định spec": 4, "見積策定・工程管理 Estimation - Quản lý tiến độ": 3, "運用設計 Operational Design": 3, "データストア Data Store": 4, "インフラ・ネットワーク Infra - Network": 3, "セキュリティ Security": 3, "データ分析 Data Analysis": 4, "改善提案 Đề xuất cải thiện": 3, "日本語能力 Năng lực tiếng Nhật": 4, "品質保証 Đảm bảo chất lượng": 3, "改善提案 Đề xuất ý kiến cải thiện": 3}',
            3.42
        ),
        (
            'EVAL_U209', 'U209', '1',
            '{"調整力・推進力 Năng lực điều phối - năng lực thúc đẩy": 4, "要求定義・要件定義・仕様策定 Định nghĩa yêu cầu business - Định nghĩa yêu cầu hệ thống - Xác định spec": 3, "見積策定・工程管理 Estimation - Quản lý tiến độ": 4, "運用設計 Operational Design": 3, "データストア Data Store": 3, "インフラ・ネットワーク Infra - Network": 3, "セキュリティ Security": 3, "データ分析 Data Analysis": 3, "改善提案 Đề xuất cải thiện": 4, "日本語能力 Năng lực tiếng Nhật": 4, "品質保証 Đảm bảo chất lượng": 3, "改善提案 Đề xuất ý kiến cải thiện": 3}',
            3.33
        ),
        (
            'EVAL_U207', 'U207', '1',
            '{"調整力・推進力 Năng lực điều phối - năng lực thúc đẩy": 2, "要求定義・要件定義・仕様策定 Định nghĩa yêu cầu business - Định nghĩa yêu cầu hệ thống - Xác định spec": 3, "見積策定・工程管理 Estimation - Quản lý tiến độ": 2, "運用設計 Operational Design": 2, "データストア Data Store": 3, "インフラ・ネットワーク Infra - Network": 2, "セキュリティ Security": 2, "データ分析 Data Analysis": 3, "改善提案 Đề xuất cải thiện": 2, "日本語能力 Năng lực tiếng Nhật": 3, "品質保証 Đảm bảo chất lượng": 2, "改善提案 Đề xuất ý kiến cải thiện": 2}',
            2.33
        ),
        (
            'EVAL_U155', 'U155', '1',
            '{"チームマネジメント Quản lý team": 4, "課題解決能力 要求定義に対する評価 Năng lực giải quyết vấn đề Đánh giá về Định nghĩa yêu cầu business": 4, "要件・仕様に対する評価 Đánh giá yêu cầu hệ thống-Specs": 4, "アプリケーション設計レビュー Review thiết kế ứng dụng": 3, "テスト計画 Lên kế hoạch test": 5, "タスク管理 Quản lý task": 4, "テスト項目作成 Tạo test case": 5, "テスト項目レビュー Review test case": 4, "テスト実行・不具合起票/分析・結果レビュー Thực hiện test - Báo cáo/Phân tích lỗi - Đánh giá kết quả": 4, "開発工程改善 Cải thiện công đoạn phát triển": 4, "Foundation Nền tảng": 4, "Advance Nâng cao": 3}',
            4.0
        ),
        (
            'EVAL_U143', 'U143', '1',
            '{"チームマネジメント Quản lý team": null, "課題解決能力 要求定義に対する評価 Năng lực giải quyết vấn đề Đánh giá về Định nghĩa yêu cầu business": 3, "要件・仕様に対する評価 Đánh giá yêu cầu hệ thống-Specs": 3, "アプリケーション設計レビュー Review thiết kế ứng dụng": 2, "テスト計画 Lên kế hoạch test": 3, "タスク管理 Quản lý task": 3, "テスト項目作成 Tạo test case": 4, "テスト項目レビュー Review test case": 3, "テスト実行・不具合起票/分析・結果レビュー Thực hiện test - Báo cáo/Phân tích lỗi - Đánh giá kết quả": 4, "開発工程改善 Cải thiện công đoạn phát triển": 3, "Foundation Nền tảng": 3, "Advance Nâng cao": 2}',
            3.0
        );
    """)


def downgrade():
    op.drop_table("evaluation_summaries")
