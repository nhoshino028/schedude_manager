"""
予定 (schedules) リソース関連の pydantic スキーマ定義。

役割:
    POST /schedules のリクエスト/レスポンス、PUT /schedules/{id} の
    リクエスト雛形（受講者課題用）、GET /schedules のレスポンス
    （= POST のレスポンスと同型）を一括で扱う。仕様書 §4。

公開物:
    ScheduleCreateRequest: POST /schedules の入力 (お手本完全実装)
    ScheduleResponse: POST/GET/PUT のレスポンス共通形 (お手本完全実装)
    ScheduleUpdateRequest: PUT /schedules/{id} の入力雛形 (受講者課題)

呼び出し関係:
    - 上流: app/routes/schedules.py (POST のお手本) /
            受講者が後で実装する GET / PUT / DELETE
    - 下流: なし
"""

from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ScheduleCreateRequest(BaseModel):
    """
    POST /schedules リクエストモデル（仕様書 §4.2）。

    属性:
        user_id: int  (alias: userId) — 必須。schedules.user_id (FK to users)
        target_date: date  (alias: targetDate) — 必須。
        status_type_id: int  (alias: statusTypeId) — 必須。FK to work_status_types
        start_time: time | None  (alias: startTime) — 任意。
        end_time: time | None  (alias: endTime) — 任意。
        comment: str | None  — 任意。

    バリデーション:
        - 必須属性は pydantic が自動的にチェック (欠落時は ValidationError)
        - start_time と end_time が両方指定された場合は start <= end を強制
          (仕様書 §4.2 のバリデーション)

    暗黙的に利用するもの:
        - populate_by_name=True で snake / camel どちらでも受け付ける。
        - model_validator(mode="after") は __init__ 後に self を受け取り、
          検証して self を返す。例外を raise すると ValidationError として
          外側に伝播する。
    """
    model_config = ConfigDict(populate_by_name=True)

    user_id: int = Field(alias="userId")
    target_date: date = Field(alias="targetDate")
    status_type_id: int = Field(alias="statusTypeId")
    start_time: time | None = Field(default=None, alias="startTime")
    end_time: time | None = Field(default=None, alias="endTime")
    comment: str | None = None

    @model_validator(mode="after")
    def _validate_time_order(self) -> "ScheduleCreateRequest":
        """
        startTime と endTime が両方指定されたとき、start <= end を強制する。

        処理: 両方が None でないとき start_time > end_time なら ValueError。
        引数: なし (self を pydantic が渡す)。
        戻り値: self (mode="after" の規約)。
        暗黙的に利用するもの: pydantic が ValueError を ValidationError に
        ラップして 400 ハンドラに引き渡す。
        """
        if self.start_time is not None and self.end_time is not None:
            if self.start_time > self.end_time:
                raise ValueError("startTime must be <= endTime")
        return self


class ScheduleResponse(BaseModel):
    """
    POST/GET/PUT /schedules のレスポンス共通モデル（仕様書 §4.2 / §4.3）。

    属性:
        id: int — schedules.id
        user_id: int  (alias: userId)
        target_date: date  (alias: targetDate)
        status_type_id: int  (alias: statusTypeId)
        start_time: time | None  (alias: startTime)
        end_time: time | None  (alias: endTime)
        comment: str | None
        created_at: datetime  (alias: createdAt) — タイムゾーン付き
        updated_at: datetime  (alias: updatedAt) — タイムゾーン付き

    暗黙的に利用するもの:
        - from_attributes=True で psycopg dict_row が返す行 dict から
          そのまま model_validate できる。
        - model_dump(by_alias=True) で API 仕様書通りの camelCase JSON。
        - datetime のシリアライズは pydantic 既定の RFC3339 形式
          (例: "2026-04-27T09:00:00+00:00") で API 仕様書 §1 と一致。
    """
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: int
    user_id: int = Field(alias="userId")
    target_date: date = Field(alias="targetDate")
    status_type_id: int = Field(alias="statusTypeId")
    start_time: time | None = Field(default=None, alias="startTime")
    end_time: time | None = Field(default=None, alias="endTime")
    comment: str | None = None
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


# =============================================================================
# 受講者課題用の雛形 (PUT /schedules/{id} 用)
# =============================================================================
class ScheduleUpdateRequest(BaseModel):
    """
    PUT /schedules/{id} リクエスト雛形（仕様書 §4.3）。

    本クラスは受講者課題のための雛形である。
    実装ヒント:
        ScheduleCreateRequest と同じ構造で良い (PUT は全項目更新を想定)。
        必須項目もクロスフィールド検証 (start <= end) も同様に必要。

    お手本: ScheduleCreateRequest を読み、フィールド定義と
    @model_validator(mode="after") の書き方を参考に同形を書き写す。

    TODO（受講者）:
        フィールドを定義する。コメントアウトされた例を参考にする。
    """
    model_config = ConfigDict(populate_by_name=True)
    # フィールド未定義。受講者がここに ScheduleCreateRequest と同様の
    # user_id / target_date / status_type_id / start_time / end_time / comment
    # を実装する。
