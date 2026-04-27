# Phase2 受講者向けガイド: Web API 実装の手引き

## 1. このドキュメントの位置付け

本ガイドは [概要.md](../../概要.md) Phase2「Web API」の受講者課題に取り組む人のための **手引き** である。模範解答にはお手本となる API が 2 本だけ実装済み（GET /work-status-types と POST /schedules）で、残りは受講者が自分で書くのが課題。

ガイドとコードコメントの分担:

- **コードコメント**（各 `.py` のファイル冒頭・関数 docstring）: 関数 1 つ単位の局所的文脈・処理ステップ・暗黙引数。
- **本ガイド md**: Phase2 全体の地図 / お手本コードの読み解き / 課題進行順 / 動作確認 / よくあるハマりどころ。

両方を行き来しながら進めると効率がよい。仕様の根拠は `docs/spec/API仕様書.md` と `docs/spec/DB定義書.md` を参照する。

---

## 2. Phase2 のゴール

Phase2 で完成すべき API（仕様書 §3〜§5）:

| メソッド | パス | 模範解答状態 | 受講者が書く |
|---|---|---|---|
| GET | `/work-status-types` | お手本完全実装 | — |
| POST | `/schedules` | お手本完全実装 | — |
| GET | `/teams` | 雛形のみ | ★ |
| GET | `/users` | 雛形のみ | ★ |
| GET | `/schedules` | 雛形のみ（schedules.py 内 TODO） | ★ |
| PUT | `/schedules/{id}` | 雛形のみ | ★ |
| DELETE | `/schedules/{id}` | 雛形のみ | ★ |
| GET | `/reports/monthly` | 雛形のみ | ★ |

★ が受講者が実装する 6 本。これらの中身を埋めれば Phase2 完了。

各 Blueprint は `create_app()` で **既に登録済み**。受講者は対応する `routes/*.py` ファイルにハンドラ関数を生やすだけで動く（雛形 Blueprint なので、ハンドラ未定義の URL に GET すると 404、URL は存在するが該当メソッドが無い場合は 405 が返る ― いずれも `app/errors.py` の HTTPException ハンドラが共通エラー形式 JSON に整形する）。

---

## 3. 基盤層の概要

`backend/app/` 配下の役割を 1 章ずつ整理する。

### 3-1. `app/__init__.py` — Application Factory

`create_app()` で Flask アプリを組み立てる。受講者が触る必要は通常ない。新しい Blueprint ファイルを追加するときは register_blueprint の行を追記する想定だが、本 Phase2 模範解答では **すべての Blueprint が既に登録済み** なので不要。

### 3-2. `app/config.py` — 環境変数読み込み

pydantic-settings で `DATABASE_URL` / `FLASK_DEBUG` を読む。`current_app.config["SETTINGS"]` 経由で全コードから参照できる。

### 3-3. `app/db.py` — DB 接続ライフサイクル

`get_db()` でリクエスト用の psycopg 接続を取り、`teardown_appcontext` で自動 close する。**受講者は `from app.db import get_db` してハンドラの最初で `db = get_db()` するだけ**。プールも複雑な ORM もない。

`row_factory=dict_row` が指定されているので `cur.fetchall()` / `cur.fetchone()` の戻り値は `{"カラム名": 値}` の dict（または dict のリスト）になる。

### 3-4. `app/errors.py` — 共通エラーハンドラ

仕様書 §1 のエラー形式 `{"code", "message", "details"}` に統一する。

- `pydantic.ValidationError` を raise すれば 400 が返る（受講者は何もしなくても model_validate(...) が勝手に発火する）。
- `app.errors.NotFoundError("...")` を raise すれば 404、`ConflictError("...")` で 409。
- 想定外の例外は最終受けで 500 になる。

### 3-5. `app/schemas/` — pydantic モデル

リクエスト検証 + レスポンス整形。各リソース 1 ファイル。

camelCase 変換は `Field(alias="camelCase")` を 1 個ずつ書く。受講者は `schemas/teams.py` 等の TODO コメントに従って同じ形でモデルを書く。`model_dump(mode="json", by_alias=True)` で camelCase + JSON 互換型の dict が返るので、それを `jsonify` する。

### 3-6. `app/routes/` — エンドポイント実装

各リソース 1 ファイル。受講者は `routes/teams.py` / `users.py` / `reports.py` の各ファイルに `@bp.get("/...")` のハンドラを書き足し、`schedules.py` の TODO コメント箇所を実装で埋めていく。

---

## 4. お手本 GET の読み解き — `routes/work_status_types.py`

→ 該当ファイル: [`backend/app/routes/work_status_types.py`](../../backend/app/routes/work_status_types.py)

学んでほしい技術ポイント（コードを開いた状態で本ガイドと照らし合わせる前提）:

1. **Blueprint 生成**: `Blueprint("work_status_types", __name__)` で名前空間を作る。`create_app()` でこれを `register_blueprint` する。
2. **URL マッピング**: `@work_status_types_bp.get("/work-status-types")` で GET メソッドだけを受ける。POST / PUT / DELETE などは別途デコレータを書く（書かなければ 405 Method Not Allowed が返る）。
3. **DB 接続**: `db = get_db()` で取得。with 文で cursor を開き、SELECT。
4. **SQL**: `ORDER BY id` で並び順を保証。マスタは件数が少ないので WHERE / LIMIT は不要。
5. **dict_row**: `cur.fetchall()` の戻り値が `[{"id": 1, "status_code": "OFFICE", "status_name": "出社"}, ...]`。タプルではなく dict であることに注目。
6. **pydantic 通し**: `WorkStatusType.model_validate(row)` で型と alias を確認 → `model_dump(mode="json", by_alias=True)` で camelCase + JSON 互換型に変換。本リソースには date/time/datetime が含まれないため `mode="json"` は実質 no-op だが、お手本 2 本で記法を揃えるため付与している (詳細は §8-1 / §8-5)。dict をそのまま jsonify でも動くが、教育目的でモデル経由を採る。
7. **レスポンス**: `jsonify(items), 200` で 200 OK + JSON 配列を返す。jsonify は Content-Type: application/json を自動付与。

このパターンをほぼそのまま `GET /teams` / `GET /users` に応用できる。違うのは SQL（JOIN の有無）と pydantic モデルだけ。

---

## 5. お手本 POST の読み解き — `routes/schedules.py` の `create_schedule()`

→ 該当ファイル: [`backend/app/routes/schedules.py`](../../backend/app/routes/schedules.py)

学んでほしい技術ポイント:

1. **JSON ボディ取得**: `request.get_json(silent=True) or {}`。silent=True で JSON パース失敗時に None を返す → `or {}` で空 dict にフォールバック。これで pydantic に「全フィールド欠落」として処理させると、自然に必須欠落の 400 が返る。
2. **リクエスト検証**: `ScheduleCreateRequest.model_validate(payload)`。失敗すると `pydantic.ValidationError` が raise され、`errors.py` の `@app.errorhandler(ValidationError)` が 400 + details に変換する。受講者は try/except を書かなくてよい。
3. **クロスフィールド検証**: `schemas/schedules.py` の `@model_validator(mode="after")` を見る。`startTime > endTime` で `ValueError` を raise すると、これも ValidationError 経由で 400 になる。
4. **named プレースホルダ**: `INSERT ... VALUES (%(user_id)s, %(target_date)s, ...)` と `cur.execute(sql, body.model_dump())` で dict を渡す方式。`body.model_dump()` は **既定で snake_case の dict** を返す（`by_alias=False` 既定）ため、SQL のキーと一致する。
5. **`created_at` / `updated_at` を SQL の `now()` で渡す**: `docs/spec/DB定義書.md` §共通方針 (line 71) で「監査系: アプリ側で設定」と決まっており、init.sql に DEFAULT を持たせない設計。INSERT 文で明示的に `now(), now()` を渡す。
6. **`RETURNING *`**: 挿入直後の行を SELECT 不要で取得。`fetchone()` で dict を受ける。
7. **FK 違反捕捉**: `psycopg.errors.ForeignKeyViolation` を try/except でキャッチ。`db.rollback()` してから `raise ConflictError(...) from e`。`from e` を付けると stacktrace に元例外が連鎖する（教育目的でわかりやすい）。
8. **commit / rollback**: `autocommit=False` のため、INSERT 後に明示的に `db.commit()`。エラー時は rollback。
9. **201 + Location**: 仕様書 §4.2 では特に Location ヘッダを要求していないが、REST の慣習として返す。`url_for("schedules.create_schedule")` は POST 自身の URL `/schedules` を返すので、`+ f"/{row['id']}"` で `/schedules/<id>` を生成。
10. **レスポンス整形**: `ScheduleResponse.model_validate(row).model_dump(mode="json", by_alias=True)` で camelCase + JSON 互換型 (date/time/datetime → ISO 8601 文字列) に変換 → `jsonify(response_body), 201, headers`。`mode="json"` を付けないと time / datetime が Python オブジェクトのまま残り flask.jsonify が TypeError で 500 を返す（§8-1 / §8-5 参照）。

このパターンを `PUT /schedules/{id}` に応用すると、INSERT が UPDATE に変わるだけでほぼ同じ形になる（プラス NotFoundError の判定）。`DELETE` はさらに簡単で `RETURNING id` で存在チェック → 204 No Content を返す。

---

## 6. 受講者課題の進め方（おすすめ順）

下記の順で進めると、簡単なものから難しいものへ段階的に取り組める。

1. **`GET /teams`**: 一番簡単。GET /work-status-types とほぼ同じ。`schemas/teams.py` の Team を完成させ、`routes/teams.py` にハンドラを書く。
2. **`GET /users`**: GET /teams ができれば JOIN の追加だけ。`schemas/users.py` の User を Team ネストで作る。クエリ teamId 任意は `request.args.get("teamId")` で。
3. **`DELETE /schedules/{id}`**: お手本 POST に比べてバリデーションがほぼ無い。`DELETE FROM schedules WHERE id = %(id)s RETURNING id` → fetchone() が None なら NotFoundError、成功なら `("", 204)`。
4. **`PUT /schedules/{id}`**: `schemas/schedules.py` の `ScheduleUpdateRequest` を完成（ScheduleCreateRequest と同じ形）→ お手本 POST の INSERT を UPDATE に書き換え + NotFoundError 判定。`updated_at` は `now()` で更新する。
5. **`GET /schedules`**: 検索クエリのバリデーション（`date と from/to 同時不可` 等）が少しだけ複雑。クエリの組み合わせで動的 SQL を組む（必ずプレースホルダ経由で文字列連結禁止）。
6. **`GET /reports/monthly`**: 必須クエリ `yearMonth` の検証 + monthly_schedule_summary を SELECT。バッチが Phase4 まで動かないので、データの最新性は保証されない。Phase1 で投入したサンプル 5 件で動作確認する想定。

各課題完了ごとに動作確認（次章）して、コミットする習慣をつけると後戻りしにくい。

---

## 7. 動作確認手順

### 起動

```bash
docker compose up --build -d
```

`http://localhost:8000` で API、`http://localhost:5432` で DB（外部から psql / DBeaver で覗ける）。

### お手本の動作確認（最初の疎通）

```bash
# ヘルス
curl -s http://localhost:8000/

# 勤務区分マスタ
curl -s http://localhost:8000/work-status-types | python -m json.tool

# 予定登録
curl -s -i -X POST http://localhost:8000/schedules \
  -H "Content-Type: application/json" \
  -d '{"userId": 1, "targetDate": "2026-04-27", "statusTypeId": 1, "startTime": "09:00:00", "endTime": "18:00:00", "comment": "test"}'
```

### 受講者課題の動作確認テンプレート

実装するたびに以下のような curl で確認すると速い。

```bash
# GET の正常系
curl -s "http://localhost:8000/teams" | python -m json.tool
curl -s "http://localhost:8000/users?teamId=1" | python -m json.tool
curl -s "http://localhost:8000/schedules?date=2026-04-27" | python -m json.tool
curl -s "http://localhost:8000/reports/monthly?yearMonth=2026-03" | python -m json.tool

# PUT の正常系
curl -s -i -X PUT http://localhost:8000/schedules/1 \
  -H "Content-Type: application/json" \
  -d '{"userId": 1, "targetDate": "2026-04-27", "statusTypeId": 2, "startTime": null, "endTime": null, "comment": "在宅に変更"}'

# DELETE
curl -s -i -X DELETE http://localhost:8000/schedules/999

# バリデーションエラー（必須欠落）
curl -s -i -X POST http://localhost:8000/schedules \
  -H "Content-Type: application/json" \
  -d '{"userId": 1}'
```

レスポンスは仕様書 §1 の `{"code", "message", "details"}` 形式に揃っているはず。揃っていない場合は `app/errors.py` のハンドラに渡る前のどこかで例外を呑み込んでいる可能性が高い。

---

## 8. よくあるハマりどころ

### 8-1. camelCase / snake_case の取り違え + `mode="json"` 忘れ

- リクエスト JSON は **camelCase**（`userId`, `statusTypeId` など）。
- Python コード内は **snake_case**（`user_id`, `status_type_id`）。
- DB のカラム名も **snake_case**。
- 変換は pydantic の `Field(alias=...)` が担当。

ハマるパターン:
- `body.model_dump()` をそのまま JSON に jsonify している → snake_case のままレスポンスされて仕様違反。`model_dump(mode="json", by_alias=True)` を忘れない。
- `mode="json"` を忘れると `time` / `datetime` が Python オブジェクトのまま残り、flask.jsonify が `TypeError: Object of type time is not JSON serializable` で 500 を返す。`schemas/schedules.py` の `ScheduleResponse` のように date/time/datetime を含むモデルでは必須。
- リクエストでも `populate_by_name=True` を model_config で指定し忘れて、camelCase でも snake_case でもどちらか一方しか受けない設定になっている。

### 8-2. `db.commit()` 忘れ

`autocommit=False` なので、INSERT / UPDATE / DELETE 後に `db.commit()` を呼ばないとリクエスト終了時の close で **コミットされず DB に反映されない**。

エラー時は `db.rollback()` を忘れずに（次の SQL で「current transaction is aborted」エラーが出る）。

### 8-3. 雛形 Blueprint が 404 / 405 を返す

`/teams` などにアクセスして 404 が返るのは **正常**。Blueprint は登録されているがハンドラ関数が定義されていないから。`@teams_bp.get("/teams")` を生やせば即動く。

`/schedules` に GET でアクセスすると **405 Method Not Allowed** が返る。これは POST だけ登録された URL に他のメソッドでアクセスした標準動作（werkzeug 仕様）。受講者が `@schedules_bp.get("/schedules")` を生やせば 200 になる。レスポンスボディは 404 と同じ共通エラー形式 (`HTTP_ERROR`) で統一されている。

### 8-4. CORS エラー（Phase3 連携時）

ブラウザのコンソールで `Access-Control-Allow-Origin` のエラーが出る場合、許可オリジンに該当アドレスが含まれていない。`app/__init__.py` の CORS 設定を見て、フロント側のオリジン（例: `http://localhost:5173`）を追加する。

Phase3 でフロントから fetch するときは `credentials: 'omit'` (既定) を使うこと。`credentials: 'include'` を使うとプリフライトで `Access-Control-Allow-Credentials` が必要になり、現状の設定（`supports_credentials=False`）では失敗する。

Phase2 で curl テストしている限りは CORS は無関係（curl はブラウザの SOP に縛られない）。

### 8-5. `target_date` / `start_time` の型変換と `mode="json"`

pydantic は文字列 `"2026-04-27"` を `datetime.date` に自動変換する。`"09:00:00"` は `datetime.time` に。psycopg もこれらを直接扱えるので、リクエスト → DB の変換コードは書かない。

レスポンス側の挙動はやや trickier:
- `model_dump(by_alias=True)` (mode 未指定) は `date` / `time` / `datetime` を **Python オブジェクトのまま** dict に入れる。これを `flask.jsonify` に渡すと `time` で TypeError。
- `model_dump(mode="json", by_alias=True)` は pydantic がそれぞれを ISO 8601 風の文字列に変換する（`time` → `"09:00:00"`、`date` → `"2026-04-27"`、`datetime` → `"2026-04-27T09:00:00.123456Z"`）。仕様書 §1 の「日時 ISO 8601」と整合。

お手本 2 本では一貫して `mode="json"` を付与している（WorkStatusType には date/time/datetime が無いため実質 no-op だが記法統一のため明示）。受講者も同じ書き方を踏襲することを強く推奨。

### 8-6. 文字列連結 SQL の禁止

`SELECT ... WHERE id = " + str(user_id)` のように SQL を文字列結合しない。**必ずプレースホルダ経由で値を渡す**。psycopg 3 では `cur.execute(sql, params_dict_or_tuple)` のように 2 引数で渡す。

教育目的だが、SQL インジェクション対策は身に付けておきたい基本。

---

## 9. 関連ドキュメント

- [概要.md](../../概要.md) — システム全体・Phase 構成
- [docs/spec/API仕様書.md](../spec/API仕様書.md) — 全エンドポイント仕様
- [docs/spec/DB定義書.md](../spec/DB定義書.md) — テーブル定義
- [CLAUDE.md](../../CLAUDE.md) — Claude / 開発ルール
- [docs/superpowers/specs/2026-04-27-phase2-api-foundation-design.md](../superpowers/specs/2026-04-27-phase2-api-foundation-design.md) — Phase2 設計スペック
