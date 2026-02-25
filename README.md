# Ubie OSS Claude Code Plugins

Ubie OSS が提供する Claude Code プラグイン集です。医療・ヘルスケア領域をはじめとする業務支援スキルをモノレポ構成で管理しています。

## Plugins

| Plugin                                            | Description                                                                                 |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| [hello-world](./plugins/hello-world/)             | Claude Code の全拡張ポイント（Skills, Agents, Hooks, MCP, LSP）を網羅したサンプルプラグイン |
| [healthcare-skills](./plugins/healthcare-skills/) | 医療従事者向けプラグイン。PubMed 文献検索など、医療業務に役立つスキル・ツールを収録         |

## Repository Layout

```text
.
├── plugins/
│   ├── hello-world/             # サンプルプラグイン
│   │   ├── .claude-plugin/      # プラグインメタデータ (plugin.json)
│   │   ├── agents/              # サブエージェント定義
│   │   ├── skills/              # スキル定義 (SKILL.md)
│   │   ├── hooks/               # フック設定
│   │   ├── .mcp.json            # MCP サーバー設定
│   │   └── .lsp.json            # LSP サーバー設定
│   └── healthcare-skills/       # 医療向けプラグイン
│       ├── .claude-plugin/      # プラグインメタデータ (plugin.json)
│       └── skills/              # スキル定義 (pubmed 検索など)
├── integration_tests/           # 統合テスト
├── .github/workflows/           # GitHub Actions (Lint, Integration Tests)
├── Makefile                     # タスクランナー
└── README.md
```

## Development

### Adding a New Plugin

`plugins/` 配下に新しいディレクトリを作成し、[Standard Plugin Layout](https://code.claude.com/docs/en/plugins-reference#standard-plugin-layout) に従って構成します。

- `plugins/<name>/.claude-plugin/plugin.json`: マニフェスト（必須）
- `plugins/<name>/skills/`: スキル定義
- `plugins/<name>/agents/`: サブエージェント定義
- `plugins/<name>/hooks/`: フック設定
- `plugins/<name>/.mcp.json`: MCP サーバー設定
- `plugins/<name>/.lsp.json`: LSP サーバー設定

### Local Checks

```bash
make lint                    # Lint (trunk check)
make format                  # Format (trunk fmt)
make test-integration-docker # 統合テスト (Docker)
```

### Testing

統合テストランナー (`./integration_tests/run.sh`) は `plugins/` 配下の `.claude-plugin/plugin.json` を持つディレクトリを自動検出します。

```bash
./integration_tests/run.sh              # 全テスト実行
./integration_tests/run.sh --verbose    # 詳細出力
./integration_tests/run.sh --skip-loading  # ロードテストをスキップ
```

## CI/CD

- **Trunk Check**: PR ごとに Lint・静的解析を実行
- **Integration Tests**: `plugins/` 配下の全プラグインを自動検証

## License

Apache License 2.0. See [LICENSE](./LICENSE).
