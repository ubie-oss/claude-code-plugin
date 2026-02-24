---
name: pubmed
description: 生物医学文献の検索・取得・分析を行うスキル。PubMed E-utilities API を使用して、3,600万件以上の医学文献データベースにアクセス。ユーザーが「PubMed で検索」「医学論文を探す」「文献レビュー」「最新の研究を調べる」「関連論文を見つける」などのリクエストをした際に使用。がん、免疫療法、COVID-19、薬剤、臨床試験など、あらゆる生物医学トピックに対応。
---

# PubMed 文献検索スキル

## 概要

このスキルは、PubMed E-utilities API を使用して生物医学文献の検索・取得・分析を効率的に行います。3,600万件以上の論文データベースから、関連性の高い文献を見つけ、詳細情報や抄録を取得できます。

## ワークフロー

### ステップ1: 検索戦略の決定

ユーザーのリクエストに基づいて、適切な検索戦略を選択します。

**検索タイプ**:

1. **キーワード検索** - 一般的な文献検索
   - 例: 「がん免疫療法に関する最新の研究を探してください」
   - 使用ツール: `scripts/pubmed_search.py search`

2. **特定論文の取得** - PMID が分かっている場合
   - 例: 「PMID 12345678 の論文の詳細を教えてください」
   - 使用ツール: `scripts/pubmed_search.py fetch`

3. **関連論文の探索** - 既知の論文から関連文献を見つける
   - 例: 「この論文に関連する研究を探してください」
   - 使用ツール: `scripts/pubmed_search.py related`

### ステップ2: 検索の実行

適切なコマンドとパラメータで検索を実行します。

#### コマンドリファレンス

```bash
python scripts/pubmed_search.py --help
```

#### キーワード検索

```bash
python scripts/pubmed_search.py search "cancer immunotherapy" \
  --max-results 20 \
  --sort pub_date \
```

**検索クエリの構築**:

- **複数キーワード**: `"cancer AND immunotherapy"`
- **OR 検索**: `"cancer OR tumor"`
- **フレーズ**: `"\"lung cancer\""`
- **フィールド指定**: `"cancer[Title] AND 2023[PDAT]"`
- **論文タイプ**: `"cancer AND Randomized Controlled Trial[PT]"`

**検索の最適化**:

- 広すぎる結果の場合: フィールド指定や日付範囲で絞り込む
- 狭すぎる結果の場合: 同義語や OR 検索で拡張
- 日本語文献: `Japanese[Language]` または `Japan[Affiliation]` を追加

詳細な検索構文は `references/api_reference.md` を参照。

#### 論文詳細の取得

```bash
python scripts/pubmed_search.py fetch 12345678,87654321
```

複数の PMID をカンマ区切りで指定可能。

#### 関連論文の検索

```bash
python scripts/pubmed_search.py related 12345678 --max-results 10
```

### ステップ3: 結果の分析と提示

取得した結果を解析し、ユーザーに分かりやすく提示します。

**提示する情報**:

- **タイトル**: 論文のタイトル
- **著者**: 主要著者（3名まで + et al.）
- **雑誌**: 掲載雑誌名
- **出版年月**: 出版時期
- **PMID**: PubMed ID（一意の識別子）
- **URL**: PubMed の論文ページ
- **DOI**: デジタルオブジェクト識別子（利用可能な場合）
- **抄録**: 論文の要約（詳細取得時）

**分析のポイント**:

- 検索結果の総数を報告
- 最も関連性の高い論文をハイライト
- 研究のトレンドや傾向を特定
- 臨床試験、メタアナリシス、レビュー論文などの重要な論文タイプを指摘

### ステップ4: フォローアップ

必要に応じて追加の検索や分析を提案します。

**よくあるフォローアップ**:

- 特定の論文の詳細取得
- 検索条件の調整（日付範囲、論文タイプなど）
- 関連論文の探索
- 文献レビューのための体系的な検索戦略

## よくある使用例

### 例1: 特定トピックの最新研究

**ユーザー**: 「COVID-19 ワクチンに関する2023年の最新研究を探してください」

**実行**:

```bash
python scripts/pubmed_search.py search \
  '"COVID-19" AND vaccine AND 2023[PDAT]' \
  --max-results 20 \
  --sort pub_date
```

### 例2: ランダム化比較試験のみ

**ユーザー**: 「糖尿病治療のランダム化比較試験を見つけてください」

**実行**:

```bash
python scripts/pubmed_search.py search \
  'diabetes treatment AND Randomized Controlled Trial[PT]' \
  --max-results 20 \
  --sort pub_date
```

### 例3: 日本語文献の検索

**ユーザー**: 「日本の研究機関による認知症の研究を探してください」

**実行**:

```bash
python scripts/pubmed_search.py search \
  'dementia AND Japan[Affiliation]' \
  --max-results 20
```

### 例4: レビュー論文のみ

**ユーザー**: 「がん免疫療法のレビュー論文を探してください」

**実行**:

```bash
python scripts/pubmed_search.py search \
  'cancer immunotherapy AND (Review[PT] OR Meta-Analysis[PT] OR Systematic Review[PT])' \
  --max-results 20
```

### 例5: 特定著者の論文

**ユーザー**: 「山中伸弥氏の最近の論文を探してください」

**実行**:

```bash
python scripts/pubmed_search.py search \
  'Yamanaka S[Author] AND "last 2 years"[PDAT]' \
  --max-results 20
```

## API 制限と推奨事項

### レート制限

このスクリプトは **自動的に秒間3リクエスト以下に制限** されています。NCBI の利用規約を遵守するため、各リクエスト間に自動的に待機時間が挿入されます。

- **制限**: 3リクエスト/秒（約0.34秒/リクエスト）
- **自動適用**: スクリプトが自動的に制限を適用
- **追加設定不要**: ユーザーは何も設定する必要なし

### メールアドレスの指定

NCBI はメールアドレスの指定を推奨しています（問題発生時の連絡用）:

```bash
python scripts/pubmed_search.py search "cancer" --email user@example.com
```

### 大量リクエストの処理

多数の論文を処理する場合:

- レート制限は自動適用されるため、待機時間の考慮は不要
- バッチ処理（複数 PMID を一度に fetch）を活用すると効率的
- 長時間の処理になる場合は、進捗表示の実装を検討

## トラブルシューティング

### 検索結果が0件

- クエリが厳しすぎる可能性: AND を OR に変更、日付範囲を拡大
- スペルミスを確認
- 同義語や代替用語を試す

### API エラー

- **HTTP 429**: レート制限超過 - リクエスト間隔を広げる
- **HTTP 400**: クエリ構文エラー - クエリを確認
- **HTTP 500**: サーバーエラー - 時間を置いて再試行

### requests ライブラリがない

```bash
pip install requests
```

## リソース

### スクリプト

- `scripts/pubmed_search.py`: PubMed API クライアント
  - `search`: キーワード検索
  - `fetch`: 詳細情報取得
  - `related`: 関連論文検索

### リファレンス

- `references/api_reference.md`: PubMed E-utilities API の詳細ドキュメント
  - API エンドポイント
  - パラメータ仕様
  - 検索クエリ構文
  - ベストプラクティス

## 高度な使用例

### 体系的文献レビュー

複数の検索を組み合わせて包括的なレビューを実施:

1. 広範な検索で全体像を把握
2. 論文タイプでフィルタリング（RCT、メタアナリシス）
3. 日付範囲で絞り込み
4. 関連論文を探索して漏れを防ぐ

### 引用ネットワークの構築

1. 基準論文から開始
2. `related` コマンドで関連論文を取得
3. 各関連論文の詳細を `fetch` で取得
4. 引用関係を分析

### トレンド分析

年ごとに検索を実行し、研究トレンドを可視化:

```bash
for year in {2020..2024}; do
  python scripts/pubmed_search.py search \
    "CRISPR AND ${year}[PDAT]" \
    --max-results 1
done
```

## 注意事項

- PubMed のデータは公開情報ですが、論文本文へのアクセスには出版社の許可が必要な場合があります
- 抄録は著作権で保護されている場合があるため、商用利用には注意が必要です
- API の利用規約を遵守してください: https://www.ncbi.nlm.nih.gov/home/about/policies/
