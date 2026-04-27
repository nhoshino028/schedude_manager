"""
月次集計 (reports) リソースのスキーマ定義雛形（仕様書 §5.1）。

役割:
    GET /reports/monthly のレスポンス用 pydantic モデルの雛形を提供する。
    本ファイルは受講者課題用の雛形であり、Phase2 模範解答時点では
    クラス本体は未実装。

公開物 (実装後):
    MonthlyReport: 月次集計 1 行を表すレスポンスモデル

呼び出し関係:
    - 上流 (受講者が後で書く): app/routes/reports.py
    - 下流: app/schemas/users.py の User をネスト (もしくは {id, name} のサブモデル)

実装ヒント:
    - お手本: app/schemas/work_status_types.py + 仕様書 §5.1 のレスポンス例
    - 仕様書: docs/spec/API仕様書.md §5.1
    - フィールド:
        user: { id: int, name: str }  (簡易ユーザーモデルをネスト)
        year_month: str = Field(alias="yearMonth")  (例: "2026-03")
        office_days: int = Field(alias="officeDays")
        remote_days: int = Field(alias="remoteDays")
        paid_leave_days: int = Field(alias="paidLeaveDays")
        am_leave_count: int = Field(alias="amLeaveCount")
        pm_leave_count: int = Field(alias="pmLeaveCount")
        absence_days: int = Field(alias="absenceDays")
        updated_at: datetime = Field(alias="updatedAt")

TODO（受講者）:
    MonthlyReport モデルを定義する。user 部分は別の小さな pydantic
    BaseModel を作るか、Dict で扱うか選ぶ。
"""

from datetime import datetime  # noqa: F401

from pydantic import BaseModel, ConfigDict, Field  # noqa: F401

# class MonthlyReportUser(BaseModel):
#     id: int
#     name: str
#
# class MonthlyReport(BaseModel):
#     model_config = ConfigDict(populate_by_name=True, from_attributes=True)
#     user: MonthlyReportUser
#     year_month: str = Field(alias="yearMonth")
#     ...
