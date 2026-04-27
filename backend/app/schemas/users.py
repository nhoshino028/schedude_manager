"""
ユーザー (users) リソースのスキーマ定義雛形（仕様書 §3.2）。

役割:
    GET /users のレスポンス用 pydantic モデルの雛形を提供する。
    本ファイルは受講者課題用の雛形であり、Phase2 模範解答時点では
    クラス本体は未実装。

公開物 (実装後):
    User: ユーザー 1 行を表すレスポンスモデル (team をネストで保持)

呼び出し関係:
    - 上流 (受講者が後で書く): app/routes/users.py
    - 下流: app/schemas/teams.py の Team を import (ネスト用)

実装ヒント:
    - お手本: app/schemas/work_status_types.py + 仕様書 §3.2 のレスポンス例
    - 仕様書: docs/spec/API仕様書.md §3.2
    - フィールド:
        id: int
        employee_code: str = Field(alias="employeeCode")
        name: str
        team: Team  (← schemas/teams.py の Team をネスト)
        created_at: datetime = Field(alias="createdAt")
    - クエリ teamId 任意は routes 側で扱う (本スキーマでは持たない)

TODO（受講者）:
    User モデルを定義する。先に schemas/teams.py の Team を実装してから着手。
"""

from datetime import datetime  # noqa: F401  受講者の import 用に残す

from pydantic import BaseModel, ConfigDict, Field  # noqa: F401

# from app.schemas.teams import Team
#
# class User(BaseModel):
#     model_config = ConfigDict(populate_by_name=True, from_attributes=True)
#     id: int
#     employee_code: str = Field(alias="employeeCode")
#     name: str
#     team: Team
#     created_at: datetime = Field(alias="createdAt")
