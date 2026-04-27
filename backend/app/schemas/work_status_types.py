"""
GET /work-status-types のレスポンススキーマ定義（仕様書 §3.3）。

役割:
    work_status_types テーブルの 1 行をそのまま JSON にする pydantic
    モデルを定義する。Phase2 のお手本実装の 1 つ。

公開物:
    WorkStatusType: 1 行を表す pydantic BaseModel。

呼び出し関係:
    - 上流: app/routes/work_status_types.py のハンドラが
      WorkStatusType.model_validate(row).model_dump(by_alias=True) を呼ぶ。
    - 下流: なし（純粋なデータ定義）。
"""

from pydantic import BaseModel, ConfigDict, Field


class WorkStatusType(BaseModel):
    """
    勤務区分マスタ 1 行を表すレスポンスモデル（仕様書 §3.3 のレスポンス要素）。

    属性:
        id: int
            work_status_types.id。1 から始まる連番。
        status_code: str
            "OFFICE" などの英大文字コード。JSON 上は "statusCode" で出る。
        status_name: str
            "出社" など日本語表示名。JSON 上は "statusName" で出る。

    暗黙的に利用するもの:
        - populate_by_name=True により snake_case (status_code) でも
          camelCase (statusCode) でも instantiate できる。
        - from_attributes=True により psycopg dict_row が返す
          {"status_code": ...} dict から直接 model_validate できる。
        - model_dump(by_alias=True) で camelCase の dict が返る。
    """
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: int
    status_code: str = Field(alias="statusCode")
    status_name: str = Field(alias="statusName")
