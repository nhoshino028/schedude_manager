"""
model_answer バックエンドの pydantic スキーマパッケージ。

役割:
    リクエスト / レスポンス JSON の型と camelCase 変換を集約する。
    リソース毎に 1 ファイルで分割（work_status_types.py / schedules.py /
    teams.py / users.py / reports.py）。

公開物:
    なし（各サブモジュールから明示的に import すること）。

設計方針:
    camelCase 変換は Field(alias="camelCase") を 1 個ずつ手書きする。
    alias_generator (例: to_camel) は使わない。理由は CLAUDE.md 教育目的:
    snake_case と camelCase の対応関係を受講者に意識させるため。
"""
