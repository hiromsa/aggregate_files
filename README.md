# 🚀 最終統合プロジェクト情報集約ツール

ローカルディレクトリまたはWeb URLから情報を抽出し、単一のMarkdownファイルに集約するPythonツールとStreamlit GUI。

## 📋 機能概要

- **ローカルファイル処理**: 指定されたディレクトリを再帰的にスキャンし、各種ファイルからテキストを抽出
- **Webクローリング**: 指定されたURLから始まり、同じドメイン内のページを再帰的にクロール
- **多様なファイル形式対応**: PDF、Excel、Word、各種テキストファイルに対応
- **未対応形式の警告**: .xlsや.docなどの未対応形式を検出した場合に警告を記録

## 🛠️ インストール方法

1. リポジトリをクローンまたはダウンロードします。
2. 依存関係をインストールします：

```bash
pip install -r requirements.txt
```

## 🚀 使用方法

### GUIを使用する場合

```bash
streamlit run app.py
```

ブラウザが開き、GUIインターフェースが表示されます。

### コマンドラインを使用する場合

```bash
python aggregate_files.py [入力ソース] [出力ファイル]
```

#### 例:

- ローカルディレクトリを処理:
```bash
python aggregate_files.py ./my_project ./output.md
```

- Webサイトをクロール:
```bash
python aggregate_files.py https://example.com ./web_content.md
```

## 📁 対応ファイル形式

### テキストファイル
- `.txt`, `.md`, `.py`, `.js`, `.html`, `.css`, `.json`, `.xml`, `.yaml`, `.yml`, `.csv`, `.sql`

### バイナリファイル（テキスト抽出対応）
- **PDF** (`.pdf`) - `pdfplumber`を使用してテキスト抽出
- **Excel** (`.xlsx`) - `openpyxl`を使用して全シートのデータを抽出
- **Word** (`.docx`) - `python-docx`を使用して段落テキストを抽出

### 未対応形式（警告のみ）
- `.xls`, `.doc` - 検出時に警告メッセージを出力

## ⚙️ 設定

### スキップされるファイル/ディレクトリ
- `bin`, `obj`, `.git`, `.vs`, `__pycache__`, `node_modules`
- `.exe`, `.dll`, `.pdb`, `.zip`, `.tar.gz`, `.log`
- `.jpg`, `.jpeg`, `.png`, `.ico`, `.css`, `.js`

### Webクローリング制限
- 同じドメイン内に制限
- リクエスト間に1秒の遅延を設定（サーバー負荷軽減）

## 📝 出力形式

出力はMarkdown形式で、各ファイル/URLの内容は以下の形式で記録されます：

```markdown
# File: path/to/file.ext
```language
ファイルの内容
```

# URL: https://example.com/page
```text
Webページの内容
```

## 🐛 トラブルシューティング

### インストール時のエラー
- Python 3.xがインストールされているか確認してください
- pipが最新バージョンであることを確認してください：`pip install --upgrade pip`

### 実行時のエラー
- 入力パスが正しいか確認してください
- 出力ディレクトリへの書き込み権限があるか確認してください
- Webクローリングの場合、対象サイトのrobots.txtを尊重してください

### ファイル抽出の問題
- パスワード保護されたPDFやExcelファイルはサポートされていません
- 破損したファイルはエラーとして記録されます

## 📄 ライセンス

このプロジェクトはMITライセンスの下で提供されています。

## 🤝 貢献

バグ報告や機能要望はIssueを通じてお送りください。