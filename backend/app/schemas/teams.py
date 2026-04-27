"""
チーム (teams) リソースのスキーマ定義雛形（仕様書 §3.1）。

役割:
    GET /teams のレスポンス用 pydantic モデルの雛形を提供する。
    本ファイルは受講者課題用の雛形であり、Phase2 模範解答時点では
    クラス本体は未実装。

公開物 (実装後):
    Team: チーム 1 行を表すレスポンスモデル

呼び出し関係:
    - 上流 (受講者が後で書く): app/routes/teams.py
    - 下流: なし

実装ヒント:
    - お手本: app/schemas/work_status_types.py の WorkStatusType
    - 仕様書: docs/spec/API仕様書.md §3.1
    - フィールド: id (int), team_code (alias="teamCode"), name (str)
    - model_config = ConfigDict(populate_by_name=True, from_attributes=True)

TODO（受講者）:
    Team モデルを定義する。
"""

from pydantic import BaseModel, ConfigDict, Field  # noqa: F401  受講者の import 用に残す

# class Team(BaseModel):
#     model_config = ConfigDict(populate_by_name=True, from_attributes=True)
#     id: int
#     team_code: str = Field(alias="teamCode")
#     name: str
