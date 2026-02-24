# PubMed E-utilities API リファレンス

## 概要

PubMed E-utilities は、NCBI が提供する生物医学文献データベースへのプログラマティックアクセスを可能にする API です。3,600万件以上の引用文献と抄録にアクセスできます。

## 基本情報

- **ベース URL**: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`
- **データベース**: `pubmed`
- **レート制限**: 3リクエスト/秒（スクリプトで自動適用）
- **推奨**: `email` パラメータを必ず含める（NCBI が問題時に連絡可能）

## 主要なツール

### 1. ESearch - 検索

文献を検索し、PMID のリストを取得します。

**エンドポイント**: `esearch.fcgi`

**主要パラメータ**:

- `db`: データベース名（常に `pubmed`）
- `term`: 検索クエリ
- `retmax`: 返す最大結果数（デフォルト: 20、最大: 10,000）
- `retstart`: 開始位置（ページネーション用）
- `sort`: ソート順
  - `relevance`: 関連度順（デフォルト）
  - `pub_date`: 出版日順
  - `Author`: 著者名順
- `usehistory`: `y` を指定すると検索履歴を保存

**例**:

```text
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=cancer+immunotherapy&retmax=20&sort=pub_date
```

### 2. EFetch - 詳細取得

PMID から論文の詳細情報（タイトル、著者、抄録など）を取得します。

**エンドポイント**: `efetch.fcgi`

**主要パラメータ**:

- `db`: データベース名（常に `pubmed`）
- `id`: PMID（カンマ区切りで複数指定可能）
- `retmode`: 返却形式
  - `xml`: XML 形式（推奨）
  - `text`: テキスト形式
- `rettype`: 返却タイプ
  - `abstract`: 抄録を含む
  - `medline`: MEDLINE 形式

**例**:

```text
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=12345678,87654321&retmode=xml&rettype=abstract
```

### 3. ESummary - サマリー取得

PMID から簡略化されたサマリー情報を取得します（EFetch より高速）。

**エンドポイント**: `esummary.fcgi`

**主要パラメータ**:

- `db`: データベース名（常に `pubmed`）
- `id`: PMID（カンマ区切りで複数指定可能）
- `retmode`: `json` を推奨

**例**:

```text
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=12345678&retmode=json
```

### 4. ELink - 関連情報取得

論文の関連情報（引用、関連論文など）を取得します。

**エンドポイント**: `elink.fcgi`

**主要パラメータ**:

- `dbfrom`: 元のデータベース（`pubmed`）
- `db`: 関連先データベース（`pubmed`）
- `id`: PMID
- `cmd`: コマンド
  - `neighbor`: 関連レコード
  - `prlinks`: 出版社リンク
- `linkname`: リンクタイプ
  - `pubmed_pubmed`: 関連論文
  - `pubmed_pubmed_citedin`: この論文を引用している論文
  - `pubmed_pubmed_refs`: この論文が引用している論文

**例**:

```text
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&db=pubmed&id=12345678&cmd=neighbor&linkname=pubmed_pubmed
```

## 検索クエリの構文

### 基本的な検索

- **単一キーワード**: `cancer`
- **複数キーワード（AND）**: `cancer AND immunotherapy`
- **OR 検索**: `cancer OR tumor`
- **NOT 検索**: `cancer NOT breast`
- **フレーズ検索**: `"lung cancer"`

### フィールド指定

- **タイトル**: `cancer[Title]`
- **著者**: `Smith J[Author]`
- **雑誌**: `Nature[Journal]`
- **出版年**: `2023[PDAT]`
- **抄録**: `immunotherapy[Abstract]`
- **アフィリエーション**: `Harvard[Affiliation]`

### 日付範囲

- **特定年**: `2023[PDAT]`
- **範囲**: `2020:2023[PDAT]`
- **過去N日**: `"last 30 days"[PDAT]`

### 複合検索の例

```text
("lung cancer"[Title] OR "pulmonary neoplasm"[Title]) AND immunotherapy[Abstract] AND 2020:2023[PDAT] AND English[Language]
```

## 論文タイプフィルター

- **ランダム化比較試験**: `Randomized Controlled Trial[PT]`
- **メタアナリシス**: `Meta-Analysis[PT]`
- **システマティックレビュー**: `Systematic Review[PT]`
- **症例報告**: `Case Reports[PT]`
- **レビュー**: `Review[PT]`

## ベストプラクティス

### 1. メールアドレスの指定

すべてのリクエストに `email` パラメータを含めることが推奨されます：

```text
&email=your.email@example.com
```

NCBI が問題発生時に連絡できるようにするためです。

### 2. レート制限の遵守

このスキルのスクリプトは **自動的に3リクエスト/秒以下に制限** されています：

- 各リクエスト間に自動的に待機時間を挿入
- ユーザーは追加の設定不要
- NCBI の利用規約を自動的に遵守

### 3. エラーハンドリング

- HTTP ステータスコードを確認
- XML/JSON のパースエラーを処理
- ネットワークエラーに対してリトライロジックを実装

### 4. データのキャッシング

- 同じクエリを繰り返し実行しない
- 取得したデータをローカルにキャッシュ
- 定期的に更新が必要な場合のみ再取得

### 5. バッチ処理の活用

- 複数の PMID を一度に fetch することで、リクエスト回数を削減
- カンマ区切りで最大200件まで指定可能

## 日本語文献の検索

PubMed には日本語の文献も含まれています。以下のフィルターが有効です：

```text
cancer AND Japanese[Language]
```

または、日本の雑誌に絞り込む：

```text
cancer AND (Japan[Affiliation] OR Japanese[Language])
```

## よくある検索パターン

### 最新の臨床試験を検索

```text
cancer immunotherapy AND Randomized Controlled Trial[PT] AND "last 2 years"[PDAT]
```

### 特定の著者の最近の論文

```text
Smith J[Author] AND 2023[PDAT]
```

### レビュー論文のみ

```text
cancer immunotherapy AND (Review[PT] OR Meta-Analysis[PT] OR Systematic Review[PT])
```

### フリーテキストが利用可能な論文

```text
cancer AND free full text[SB]
```

## XML レスポンスの構造

EFetch で返される XML の主要な要素：

```xml
<PubmedArticleSet>
  <PubmedArticle>
    <MedlineCitation>
      <PMID>12345678</PMID>
      <Article>
        <ArticleTitle>タイトル</ArticleTitle>
        <Abstract>
          <AbstractText>抄録テキスト</AbstractText>
        </Abstract>
        <AuthorList>
          <Author>
            <LastName>姓</LastName>
            <ForeName>名</ForeName>
          </Author>
        </AuthorList>
        <Journal>
          <Title>雑誌名</Title>
        </Journal>
      </Article>
    </MedlineCitation>
    <PubmedData>
      <ArticleIdList>
        <ArticleId IdType="doi">10.1234/example</ArticleId>
        <ArticleId IdType="pmc">PMC1234567</ArticleId>
      </ArticleIdList>
    </PubmedData>
  </PubmedArticle>
</PubmedArticleSet>
```

## 参考リンク

- **公式ドキュメント**: https://www.ncbi.nlm.nih.gov/books/NBK25501/
- **検索フィールド一覧**: https://www.ncbi.nlm.nih.gov/books/NBK3827/
- **PubMed ヘルプ**: https://pubmed.ncbi.nlm.nih.gov/help/
