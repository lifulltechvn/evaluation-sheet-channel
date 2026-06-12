"""seed h1/h2 test data for completed evaluations

Revision ID: 0008
Revises: 0007
Create Date: 2026-06-05
"""
from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade():
    # ── Cập nhật evaluations đã Completed: ghi nhận H1 scores, CEO approve, chuyển phase 2 ──

    # EVAL_U224 (Completed) - H1 done, đang phase 2
    op.execute("""
        UPDATE evaluations SET
            phase = 2,
            h1_score = 3.58,
            h1_rank = 'G1',
            h1_approved_by = 'U106',
            h1_approved_at = '2026-10-15 09:00:00',
            h2_score = 3.75,
            h2_rank = 'G1',
            h2_approved_by = 'U106',
            h2_approved_at = '2027-03-20 09:00:00',
            final_score = 3.67
        WHERE id = 'EVAL_U224'
    """)

    # EVAL_U96 (Completed) - H1 done, H2 done
    op.execute("""
        UPDATE evaluations SET
            phase = 2,
            h1_score = 3.25,
            h1_rank = 'G1',
            h1_approved_by = 'U106',
            h1_approved_at = '2026-10-15 09:30:00',
            h2_score = 3.50,
            h2_rank = 'G1',
            h2_approved_by = 'U106',
            h2_approved_at = '2027-03-20 09:30:00',
            final_score = 3.38
        WHERE id = 'EVAL_U96'
    """)

    # EVAL_U23 (Completed) - H1 done, H2 done
    op.execute("""
        UPDATE evaluations SET
            phase = 2,
            h1_score = 4.50,
            h1_rank = 'G2',
            h1_approved_by = 'U106',
            h1_approved_at = '2026-10-15 10:00:00',
            h2_score = 4.67,
            h2_rank = 'G2',
            h2_approved_by = 'U106',
            h2_approved_at = '2027-03-20 10:00:00',
            final_score = 4.58
        WHERE id = 'EVAL_U23'
    """)

    # EVAL_U187 (Completed) - H1 done, H2 done
    op.execute("""
        UPDATE evaluations SET
            phase = 2,
            h1_score = 3.42,
            h1_rank = 'G1',
            h1_approved_by = 'U106',
            h1_approved_at = '2026-10-16 09:00:00',
            h2_score = 3.58,
            h2_rank = 'G1',
            h2_approved_by = 'U106',
            h2_approved_at = '2027-03-21 09:00:00',
            final_score = 3.50
        WHERE id = 'EVAL_U187'
    """)

    # EVAL_U155 (Completed) - H1 done, H2 done
    op.execute("""
        UPDATE evaluations SET
            phase = 2,
            h1_score = 4.00,
            h1_rank = 'G2',
            h1_approved_by = 'U106',
            h1_approved_at = '2026-10-16 10:00:00',
            h2_score = 4.17,
            h2_rank = 'G2',
            h2_approved_by = 'U106',
            h2_approved_at = '2027-03-21 10:00:00',
            final_score = 4.08
        WHERE id = 'EVAL_U155'
    """)

    # ── Cập nhật evaluations đang review: H1 đã có điểm nhưng chưa approve ──

    # EVAL_U191 (Manager_Reviewing) - đang chờ approve H1
    op.execute("""
        UPDATE evaluations SET
            phase = 1,
            h1_score = 2.75,
            h1_rank = NULL,
            h1_approved_by = NULL,
            h1_approved_at = NULL
        WHERE id = 'EVAL_U191'
    """)

    # EVAL_U209 (Manager_Reviewing) - đang chờ approve H1
    op.execute("""
        UPDATE evaluations SET
            phase = 1,
            h1_score = 3.33,
            h1_rank = NULL,
            h1_approved_by = NULL,
            h1_approved_at = NULL
        WHERE id = 'EVAL_U209'
    """)

    # EVAL_U148 (Leader_Reviewing) - leader đang chấm H1
    op.execute("""
        UPDATE evaluations SET
            phase = 1,
            h1_score = 2.33,
            h1_rank = NULL,
            h1_approved_by = NULL,
            h1_approved_at = NULL
        WHERE id = 'EVAL_U148'
    """)

    # EVAL_U116 (Manager_Reviewing) - đang chờ approve H1
    op.execute("""
        UPDATE evaluations SET
            phase = 1,
            h1_score = 3.33,
            h1_rank = NULL,
            h1_approved_by = NULL,
            h1_approved_at = NULL
        WHERE id = 'EVAL_U116'
    """)

    # ── Seed phase 2 cho evaluation_summaries (những eval đã Completed cả 2 phase) ──

    op.execute("""
        INSERT INTO evaluation_summaries (evaluation_id, employee_id, period_id, phase, skills_score, total_average)
        VALUES
        (
            'EVAL_U224', 'U224', '1', 2,
            '{"プログラミング Programming": 4, "データストア Data Store": 4, "テスティング Testing": 4, "アーキテクチャー Architecture": 4, "サーバー・ミドルウェア Server-Middleware": 3, "インフラ・ネットワーク Infrastructure-Network": 4, "セキュリティ Security": 4, "フロントエンド Frontend": 4, "要件定義・仕様作成 Requirements": 3, "スケジュール管理 Schedule Management": 4, "データ分析 Data Analysis": 4, "改善提案 Improvement Proposals": 4}',
            3.75
        ),
        (
            'EVAL_U96', 'U96', '1', 2,
            '{"プログラミング Programming": 4, "データストア Data Store": 3, "テスティング Testing": 4, "アーキテクチャー Architecture": 3, "サーバー・ミドルウェア Server-Middleware": 4, "インフラ・ネットワーク Infrastructure-Network": 3, "セキュリティ Security": 4, "フロントエンド Frontend": 3, "要件定義・仕様作成 Requirements": 4, "スケジュール管理 Schedule Management": 3, "データ分析 Data Analysis": 4, "改善提案 Improvement Proposals": 4}',
            3.50
        ),
        (
            'EVAL_U23', 'U23', '1', 2,
            '{"プログラミング Programming": 5, "データストア Data Store": 5, "テスティング Testing": 5, "アーキテクチャー Architecture": 5, "サーバー・ミドルウェア Server-Middleware": 4, "インフラ・ネットワーク Infrastructure-Network": 5, "セキュリティ Security": 5, "フロントエンド Frontend": 4, "要件定義・仕様作成 Requirements": 5, "スケジュール管理 Schedule Management": 4, "データ分析 Data Analysis": 5, "改善提案 Improvement Proposals": 5}',
            4.67
        ),
        (
            'EVAL_U187', 'U187', '1', 2,
            '{"調整力・推進力 Coordination": 4, "要求定義・要件定義 Requirements": 4, "見積策定・工程管理 Estimation": 4, "運用設計 Operational Design": 3, "データストア Data Store": 4, "インフラ・ネットワーク Infra": 4, "セキュリティ Security": 3, "データ分析 Data Analysis": 4, "改善提案 Improvement": 3, "日本語能力 Japanese": 4, "品質保証 Quality": 3, "改善提案2 Improvement2": 4}',
            3.58
        ),
        (
            'EVAL_U155', 'U155', '1', 2,
            '{"チームマネジメント Team Management": 4, "課題解決能力 Problem Solving": 5, "要件・仕様 Requirements": 4, "設計レビュー Design Review": 4, "テスト計画 Test Planning": 5, "タスク管理 Task Management": 4, "テスト項目作成 Test Cases": 5, "テスト項目レビュー Test Review": 4, "テスト実行 Test Execution": 5, "開発工程改善 Process Improvement": 4, "Foundation": 4, "Advance": 3}',
            4.17
        )
    """)


def downgrade():
    # Xóa phase 2 summaries
    op.execute("DELETE FROM evaluation_summaries WHERE phase = 2")

    # Reset evaluations về trạng thái ban đầu
    op.execute("""
        UPDATE evaluations SET
            phase = 1,
            h1_score = NULL, h1_rank = NULL, h1_approved_by = NULL, h1_approved_at = NULL,
            h2_score = NULL, h2_rank = NULL, h2_approved_by = NULL, h2_approved_at = NULL
    """)
