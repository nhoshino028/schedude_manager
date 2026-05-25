# スケジュール管理アプリ（教育用 ）

## プロジェクトの概要

スケジュール管理アプリ

社内メンバーの一日の勤務予定を記録管理する

予定の登録
　　日付ごとに記録を登録可能

登録した予定の

- 月間勤務予定の一覧表示
- 月間勤務予定から予定を検索
- 予定の更新
- 予定の削除

の機能を提供しています。

## 前提ツール

・VS Code以外でOSに直接インストールするもの

- コンテナ
  - Docker Desktop / Docker Engine + Compose v2など、docker composeコマンドが使える環境

・必要なVS code拡張機能

- Dev Container
- Python Debugger等のpythonファイルのデバッグが可能な拡張機能

## 環境構築、手順

★開発環境立ち上げまでの手順とコマンド例を記載する。

・環境設定ファイル（envファイルの準備)手順

- 前提条件
  - Docker Desktopがインストールされていること

        1.リポジトリをローカル環境に作成する
        ```bash
        git clone git@github.com:nhoshino028/schedule_manager.git
        cd schedule_manager
        git switch develop
        ```

        2.環境設定ファイルの準備
        backendフォルダ配下に `.env` ファイルを作成
        以下の設定を記入する

        ```env
          POSTGRES_USER=postgres
          POSTGRES_PASSWORD=postgres
          POSTGRES_DB=postgres

          DATABASE_URL=postgresql://postgres:postgres@postgres:5432/schedule_manager

          FLASK_DEBUG=1

          VITE_API_BASE_URL=http://localhost:8000
        ```

        3.ターミナルを起動し、起動コマンドを入力
        　開発環境を立ち上げる
        　

・docker compose 全体起動／停止
リポジトリ直下でBashを起動

- 全体起動
  `docker compose up -d`

- 全体停止
  `docker compose stop`

・ サービス単体での起動／停止

- 単体起動
  `docker compose up [サービス名]`

- 単体停止
  `docker compose stop [サービス名]`

・イメージの再ビルド方法
`docker compose up --build -d`

・DBデータを初期化しての起動方法（ボリュームの削除）
`docker compose down -v`
`docker compose up --build -d`

## dev containerによる開発手順（バックエンドのみ）

★dev container による開発の説明を記載する
・dev container での開発環境の開き方
・VS Code上でのデバッグの仕方（ブレークポイントで止める）の手順

- 注意点
  通常起動、個別での開発コンテナ立ち上げ時には、8000番ポートでアプリが起動します。
  Python Debuggerによるデバッグ実行では、ポート番号重複を避けるためにPython Debuggerデフォルト設定の5000番ポートを使用します。

- 開発環境の開き方
  - 前提条件
    - DevContainerが拡張機能からインストールされていること
  - 開発方法
    1.backendフォルダをVSCodeで開く

    2.「.devcontainer」フォルダを作成
    　フォルダ内にdevcontainer.jsonを作成し、開発環境の設定を追加する

    3-1.初回、または変更点があった場合の開き方
    　`ctrl + Shift + P`でコマンドパレットを開き、`Dev Containers: Rebuild and Reopen in Container`を選択
    　backendフォルダがDevContainerで開かれる
    VScode画面左下に「開発コンテナー:backend_dev」と表示されていれば、起動が完了しています。

    3-2.初回以降の開発コンテナの開き方
    `ctrl + Shift + P`でコマンドパレットを開き、`Dev Containers: Reopen in Container`を選択
    　backendフォルダがDevContainerで開かれる
    VScode画面左下に「開発コンテナー:backend_dev」と表示されていれば、起動が完了しています。

    4.ブラウザで、http://localhost:8000/を開きます。
    ページが表示されていれば、問題なく開発コンテナの起動が完了しています。

- デバッグ方法
  　- 前提条件
  　- Python Debuggerが拡張機能からインストールされていること
  　　(launch.json内で開発コンテナの起動時にインストールするよう設定済みです。)

　 - デバッグ
　　1.backendを開発コンテナで起動をした状態で`F5`を押下すると、flaskアプリが実行されます。

　　2.ブラウザで、http://localhost:5000/を開きます。
　　　ページが表示されていれば、問題なくデバッグ実行ができています。

　 - ブレークポイントを設定する
　 　　動作や挿入される値の確認をしたい箇所にブレークポイントを設定
　　　`F5`を押下しデバッグ実行を行うと、対象のブレークポイント位置で動作が一時停止します。

## データベースへアクセス情報

★UIツール（A5M2など）でDBにアクセスするのに必要な情報を記載

- DB
  サーバー名：localhost
  データベース名：schedule_manager
  ユーザーID：postgres
  パスワード：postgres
  ポート番号：5432
