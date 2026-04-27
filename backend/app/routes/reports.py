"""
月次集計エンドポイントを提供する Blueprint 雛形 (仕様書 §5.1)。

役割:
    GET /reports/monthly を提供する予定の Blueprint。Phase2 模範解答
    では Blueprint 自体は create_app() に登録するが、ハンドラは未実装。
    そのため /reports/monthly にアクセスすると Flask 既定の 404 が返る。

公開物:
    reports_bp: Flask Blueprint (ハンドラ未定義)。

呼び出し関係:
    - 上流 (Phase2 で配線): app/__init__.py の create_app()
    - 下流 (受講者が実装):
        - app.db.get_db()
        - app.schemas.reports.MonthlyReport

受講者向けのヒント:
    - お手本コード: app/routes/work_status_types.py
    - 関連スキーマ: app/schemas/reports.py
    - 仕様書: docs/spec/API仕様書.md §5.1
    - 補足: バッチ未実装の段階では schedules を集計して返してもよい。
      Phase4 のバッチ実装後は monthly_schedule_summary を SELECT する形に
      切り替える方針。本 Phase2 では受講者の選択任せ。

実装手順 (受講者):
    1. クエリ yearMonth (必須) と teamId (任意) を取得。
       yearMonth 欠落時は VALIDATION_ERROR で 400。
    2. monthly_schedule_summary を SELECT (Phase1 サンプルあり)。
       JOIN users / teams で user.id / user.name を一緒に取る。
       teamId 指定時は WHERE u.team_id = %s。
    3. MonthlyReport モデルに変換し jsonify(list)。

TODO（受講者）:
    ここに @reports_bp.get("/reports/monthly") のハンドラを実装する。
"""

from flask import Blueprint  # noqa: F401

reports_bp = Blueprint("reports", __name__)

# このコメント行より下に @reports_bp.get(...) を生やす。
