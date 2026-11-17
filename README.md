# sales-management

飲食店の日次・月次・年次売上およびチャネル別（店内 / 持ち帰り）売上実績を集計・確認するツールです。  
店長・スタッフ共通ポータル（[ポータル画面イメージ](reference/system-integration/docs/images/portal/01-portal-dashboard.png)）において会計管理から供給される売上実績（I-4）の分析・レポートを提供します。

## 画面遷移図

縮小画面キャプチャを用いた `sales-management` の画面遷移図です（draw.io 編集用ソース: [transition.drawio](reference/system-integration/docs/images/sales_management/transition.drawio)）。

![sales-management 画面遷移図](reference/system-integration/docs/images/sales_management/transition.svg)

## 代表機能イメージ

### 1. 日次売上ダッシュボード (`GET /ui/sales/daily`)
指定日の総売上・計上注文件数・客単価と、店内飲食（`dine_in`）・持ち帰り（`takeout`）の売上構成比バーを表示します。

![日次売上ダッシュボード](reference/system-integration/docs/images/sales_management/01-daily-sales.png)

### 2. 月次・年次売上集計レポート (`GET /ui/sales/monthly`)
月間および年間累計の売上総額・注文件数・チャネル別内訳を左右対比で確認できます。

![月次・年次売上集計レポート](reference/system-integration/docs/images/sales_management/02-monthly-sales.png)

### 3. 売上計上明細一覧 (`GET /ui/sales/records`)
会計管理から供給された注文ID・決済ID・チャネル・金額・計上日時の実績レコード（重複排除済み）を一覧で確認できます。

![売上計上明細一覧](reference/system-integration/docs/images/sales_management/03-sales-records.png)

## 提供 API・UI エンドポイント

| 種別 | メソッド & パス | 機能概要 |
|---|---|---|
| API | `GET /health` | ヘルスチェック |
| API | `POST /sales/records` | 売上実績登録（注文ID重複時 409） (I-4) |
| API | `GET /sales/summary/daily` | 日次売上集計（`?date=YYYY-MM-DD`） |
| API | `GET /sales/summary/monthly` | 月次売上集計（`?month=YYYY-MM`） |
| API | `GET /sales/summary/yearly` | 年次売上集計（`?year=YYYY`） |
| UI | `GET /ui/sales/daily` | 日次売上ダッシュボード画面 |
| UI | `GET /ui/sales/monthly` | 月次・年次売上集計レポート画面 |
| UI | `GET /ui/sales/records` | 売上計上明細一覧画面 |

## テスト・静的解析の実行

```bash
../.venv/bin/python3 -m pytest -v
../.venv/bin/ruff check .
```
