#!/usr/bin/env python3
"""
PubMed E-utilities API を使用して文献を検索・取得するスクリプト

使用例:
    # キーワード検索
    python pubmed_search.py search "cancer immunotherapy"

    # 詳細情報取得
    python pubmed_search.py fetch 12345678

    # 複数の PMID を取得
    python pubmed_search.py fetch 12345678,87654321

    # 関連論文を検索
    python pubmed_search.py related 12345678
"""

import argparse
import json
import sys
import time
import urllib.parse
from typing import Dict, List, Optional
from xml.etree import ElementTree as ET

try:
    import requests
except ImportError:
    print("Error: requests ライブラリが必要です", file=sys.stderr)
    print("pip install requests で  インストールしてください", file=sys.stderr)
    sys.exit(1)


class PubMedClient:
    """PubMed E-utilities API クライアント（レート制限: 秒間3リクエスト）"""

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    RATE_LIMIT_DELAY = 0.34  # 秒（3リクエスト/秒 = 0.33秒/リクエスト、余裕を持たせて0.34秒）

    def __init__(self, email: Optional[str] = None):
        """
        Args:
            email: NCBI に登録したメールアドレス（推奨）
        """
        self.email = email
        self.session = requests.Session()
        self.last_request_time = 0.0

    def _rate_limit(self):
        """レート制限を適用（秒間3リクエスト以下）"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.RATE_LIMIT_DELAY:
            sleep_time = self.RATE_LIMIT_DELAY - time_since_last_request
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _build_params(self, **kwargs) -> Dict:
        """共通パラメータを構築"""
        params = {"db": "pubmed"}
        if self.email:
            params["email"] = self.email
        params.update(kwargs)
        return params

    def search(
        self,
        query: str,
        max_results: int = 20,
        sort: str = "relevance"
    ) -> Dict:
        """
        キーワードで PubMed を検索

        Args:
            query: 検索クエリ
            max_results: 最大結果数
            sort: ソート順 ("relevance", "pub_date", "Author")

        Returns:
            検索結果（PMID のリストを含む）
        """
        self._rate_limit()  # レート制限を適用

        params = self._build_params(
            term=query,
            retmax=max_results,
            sort=sort,
            usehistory="y"
        )

        response = self.session.get(f"{self.BASE_URL}/esearch.fcgi", params=params)
        response.raise_for_status()

        # XML レスポンスをパース
        root = ET.fromstring(response.text)

        # PMID リストを抽出
        id_list = [id_elem.text for id_elem in root.findall(".//Id")]
        count = int(root.findtext(".//Count", "0"))

        return {
            "query": query,
            "count": count,
            "returned": len(id_list),
            "pmids": id_list
        }

    def fetch(self, pmids: List[str]) -> List[Dict]:
        """
        PMID から詳細情報を取得

        Args:
            pmids: PMID のリスト

        Returns:
            論文情報のリスト
        """
        if isinstance(pmids, str):
            pmids = [pmids]

        self._rate_limit()  # レート制限を適用

        params = self._build_params(
            id=",".join(pmids),
            rettype="abstract",
            retmode="xml"
        )

        response = self.session.get(f"{self.BASE_URL}/efetch.fcgi", params=params)
        response.raise_for_status()

        # XML をパース
        root = ET.fromstring(response.text)
        articles = []

        for article in root.findall(".//PubmedArticle"):
            articles.append(self._parse_article(article))

        return articles

    def _parse_article(self, article_elem: ET.Element) -> Dict:
        """PubmedArticle XML をパースして辞書に変換"""
        medline = article_elem.find(".//MedlineCitation")
        article = medline.find(".//Article")

        # 基本情報
        pmid = medline.findtext(".//PMID", "")
        title = article.findtext(".//ArticleTitle", "")

        # 抄録
        abstract_texts = article.findall(".//AbstractText")
        abstract = "\n\n".join(
            f"{ab.get('Label', '')}: {ab.text}" if ab.get('Label') else ab.text or ""
            for ab in abstract_texts
        )

        # 著者
        authors = []
        for author in article.findall(".//Author"):
            last_name = author.findtext("LastName", "")
            fore_name = author.findtext("ForeName", "")
            if last_name:
                authors.append(f"{last_name} {fore_name}".strip())

        # 雑誌情報
        journal = article.find(".//Journal")
        journal_title = journal.findtext(".//Title", "") if journal is not None else ""

        # 出版日
        pub_date = article.find(".//PubDate")
        year = pub_date.findtext("Year", "") if pub_date is not None else ""
        month = pub_date.findtext("Month", "") if pub_date is not None else ""

        # DOI
        doi = ""
        for article_id in article_elem.findall(".//ArticleId"):
            if article_id.get("IdType") == "doi":
                doi = article_id.text
                break

        return {
            "pmid": pmid,
            "title": title,
            "abstract": abstract,
            "authors": authors,
            "journal": journal_title,
            "year": year,
            "month": month,
            "doi": doi,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        }

    def get_related(self, pmid: str, max_results: int = 10) -> Dict:
        """
        関連論文を取得

        Args:
            pmid: 基準となる PMID
            max_results: 最大結果数

        Returns:
            関連論文の PMID リスト
        """
        self._rate_limit()  # レート制限を適用

        params = self._build_params(
            id=pmid,
            dbfrom="pubmed",
            cmd="neighbor",
            linkname="pubmed_pubmed"
        )

        response = self.session.get(f"{self.BASE_URL}/elink.fcgi", params=params)
        response.raise_for_status()

        root = ET.fromstring(response.text)
        related_ids = [
            id_elem.text
            for id_elem in root.findall(".//Link/Id")
        ][:max_results]

        return {
            "source_pmid": pmid,
            "related_count": len(related_ids),
            "related_pmids": related_ids
        }


def main():
    parser = argparse.ArgumentParser(
        description="PubMed 文献検索・取得ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    subparsers = parser.add_subparsers(dest="command", help="コマンド")

    # search コマンド
    search_parser = subparsers.add_parser("search", help="キーワード検索")
    search_parser.add_argument("query", help="検索クエリ")
    search_parser.add_argument(
        "-n", "--max-results",
        type=int,
        default=20,
        help="最大結果数 (デフォルト: 20)"
    )
    search_parser.add_argument(
        "-s", "--sort",
        choices=["relevance", "pub_date", "Author"],
        default="relevance",
        help="ソート順"
    )

    # fetch コマンド
    fetch_parser = subparsers.add_parser("fetch", help="PMID から詳細取得")
    fetch_parser.add_argument(
        "pmids",
        help="PMID (カンマ区切りで複数指定可能)"
    )

    # related コマンド
    related_parser = subparsers.add_parser("related", help="関連論文を検索")
    related_parser.add_argument("pmid", help="基準となる PMID")
    related_parser.add_argument(
        "-n", "--max-results",
        type=int,
        default=10,
        help="最大結果数 (デフォルト: 10)"
    )

    # 共通オプション
    parser.add_argument("--email", help="NCBI 登録メールアドレス（推奨）")
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
        help="出力形式"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # クライアント初期化（レート制限: 秒間3リクエスト）
    client = PubMedClient(email=args.email)

    try:
        if args.command == "search":
            result = client.search(args.query, args.max_results, args.sort)

            if args.format == "json":
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(f"検索クエリ: {result['query']}")
                print(f"総件数: {result['count']}")
                print(f"取得件数: {result['returned']}")
                print(f"\nPMID リスト:")
                for pmid in result['pmids']:
                    print(f"  - {pmid}")

        elif args.command == "fetch":
            pmids = args.pmids.split(",")
            articles = client.fetch(pmids)

            if args.format == "json":
                print(json.dumps(articles, ensure_ascii=False, indent=2))
            else:
                for article in articles:
                    print(f"\n{'='*80}")
                    print(f"PMID: {article['pmid']}")
                    print(f"タイトル: {article['title']}")
                    print(f"著者: {', '.join(article['authors'][:3])}" +
                          (" et al." if len(article['authors']) > 3 else ""))
                    print(f"雑誌: {article['journal']}")
                    print(f"出版: {article['year']} {article['month']}")
                    if article['doi']:
                        print(f"DOI: {article['doi']}")
                    print(f"URL: {article['url']}")
                    if article['abstract']:
                        print(f"\n抄録:\n{article['abstract']}")

        elif args.command == "related":
            result = client.get_related(args.pmid, args.max_results)

            if args.format == "json":
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(f"基準 PMID: {result['source_pmid']}")
                print(f"関連論文数: {result['related_count']}")
                print(f"\n関連 PMID リスト:")
                for pmid in result['related_pmids']:
                    print(f"  - {pmid}")

    except requests.exceptions.RequestException as e:
        print(f"API エラー: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
