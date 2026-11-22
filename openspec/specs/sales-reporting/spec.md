# sales-reporting Specification

## Purpose
会計・注文管理から供給される売上レコードを重複なく蓄積し、日次・月次・年次およびチャネル別売上集計を提供する。

## Requirements

### Requirement: 売上登録
`POST /sales/records` で登録できなければならない（SHALL）。`order_id`重複時は409を返さなければならない（MUST）。

#### Scenario: 登録と重複拒否
- **WHEN** `POST /sales/records` へ送信する
- **THEN** 201 で `SalesRecord`、重複は 409 を返す

### Requirement: 売上集計
`daily`・`monthly`・`yearly` で総売上・件数・チャネル内訳を返さなければならない（SHALL）。

#### Scenario: 期間別集計
- **WHEN** `date`・`month`・`year` で集計を呼ぶ
- **THEN** `SalesSummary` を 200 で返す

### Requirement: サブモジュール参照のコミット指定管理

本リポジトリは `.gitmodules` に `branch` 設定を持たせず `reference/system-integration` を確定コミット SHA（gitlink）指定で管理しなければならず（MUST）、`reference/system-integration/` 配下を読み取り専用として直接変更してはならない（SHALL）。

#### Scenario: サブモジュール参照の更新とマージ

- **WHEN** `system-integration` の確定コミット SHA（`<commit-sha>`）を `reference/system-integration` にチェックアウトし、`system-integration` PR の Merge commit マージ後に本リポジトリの PR を `main` にマージするとき
- **THEN** `.gitmodules` の書き換えやマージ後の `main` 戻し作業なしで、正しい仕様・画像参照を維持したままマージが完了する（SHALL）
