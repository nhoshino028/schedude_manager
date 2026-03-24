# 画面モック（静的HTML）

## 開き方

- `mock/index.html` をブラウザで開く

## Docker Composeでプレビュー（推奨）

```sh
docker compose -f docker-compose.mock.yml up
```

ブラウザで `http://localhost:8080/` を開く。

停止

```sh
docker compose -f docker-compose.mock.yml down
```

## 画面

- メンバー一覧: `mock/members.html`
- 予定一覧: `mock/schedules.html`
- 予定登録/編集: `mock/schedule-form.html`
- 月次集計: `mock/monthly.html`

## クエリ例（任意）

- `mock/schedules.html?date=2026-03-11`
- `mock/schedules.html?userId=10`
- `mock/schedule-form.html?editId=100`
- `mock/members.html?teamId=1`
- `mock/monthly.html?teamId=1&yearMonth=2026-03`

## 注意

- API/DBには接続しません（ダミーデータで描画）。
- 予定一覧の「削除」は確認ダイアログとメッセージ表示のみ（実データは変化しません）。
