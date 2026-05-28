[🇺🇸 English](#english) | [🇯🇵 日本語](#日本語)

---

<a name="日本語"></a>
# RagNeuron

過去の技術支援レポートから回答を検索するRAG（Retrieval Augmented Generation）システムです。自然言語で質問すると、過去の修理事例から最適な回答が得られます。

**ML/AIの知識は不要です！** このガイドでは、すべての手順を詳しく説明します。

---

## これは何ですか？

過去の修理記録データベース（日本語など）を持っていても、手動で探すのは大変ですよね。代わりに这样的な質問ができると便利です：

- "カット機が応答しない、サーボエラーが表示される"
- "レーザーヘッドが動作しない"
- "X軸が動かない"

RagNeuronは最も類似した過去の事例を見つけ、AIが親切な回答を生成します。

---

## 前提条件

始める前に、3つ必要です：

### 1. Python（ほとんどのコンピュータにインストール済み）

確認方法：
```bash
python --version
```

インストールされていない場合：[python.org](https://www.python.org/downloads/) からダウンロード

### 2. Docker（ベクトルデータベース用）

**Windows：**
1. [docker.com](https://www.docker.com/get-started/) からDocker Desktopをダウンロード
2. インストール
3. Docker Desktopを起動

**macOS：**
```bash
brew install --cask docker
```

**Linux（Ubuntu）：**
```bash
sudo apt update
# Option A: Docker Compose plugin (recommended)
sudo apt install docker.io docker-compose-plugin
# Option B: Legacy standalone docker-compose
sudo apt install docker.io docker-compose
sudo systemctl start docker
```

Dockerが動いているか確認：
```bash
docker --version
```

### 3. LM Studio（AI回答用）

[lmstudio.ai](https://lmstudio.ai/) からダウンロード

1. LM Studioをダウンロードしてインストール
2. LM Studioを開く
3. モデルをダウンロード（おすすめ：Qwen3.5-2Bなど）
4. 「Start Server」をクリック（通常はポート1234）

---

## インストール

### ステップ1：コードを取得

**オプションA：ZIPダウンロード**
1. GitHubリポジトリに行く
2. 緑色の「Code」ボタンをクリック
3. 「Download ZIP」をクリック
4. フォルダに解凍

**オプションB：Gitを使用**
```bash
git clone https://github.com/nakul-nsksystem/RagNeuron.git
cd RagNeuron
```

### ステップ2：uvをインストール

uvは高速なPythonパッケージマネージャです。

**macOS / Linux：**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows：**
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

またはpipを使用：
```bash
pip install uv
```

### ステップ3：Pythonの依存関係をインストール

```bash
cd RagNeuron
uv sync
```

これにより、自動的に仮想環境が作成され、すべてのパッケージがインストールされます。

---

## クイックスタート（コマンド1つ）

すべてインストールした後、実行：

```bash
# Linux/macOS（Docker Composeプラグイン）
./run.sh

# Linux/macOS（レガシーdocker-compose）
./run-legacy.sh

# Windows（Docker Composeプラグイン）
run.bat

# Windows（レガシーdocker-compose）
run-legacy.bat
```

**どちらのスクリプトを使うべき？**
- `run.sh` / `run.bat` → `docker compose`（サブコマンド、Compose v2+）
- `run-legacy.sh` / `run-legacy.bat` → `docker-compose`（スタンドアロンバイナリ）

`docker compose` が使えない場合は `run-legacy` を使用してください。

スクリプトが自動的に行うこと：
1. GPUがあるか検出
2. モードを選択
3. すべてを起動

---

## 手動セットアップ（手順を踏みたい場合）

### Qdrantを起動（ベクトルデータベース）

```bash
# Docker Composeプラグインの場合
docker compose up -d qdrant
# レガシーdocker-composeの場合
docker-compose up -d qdrant
```

起動まで3秒待ちます。

### データを追加

JSONデータファイルを `data/tech_reports_rag.json` に配置

**必須フォーマット：**
```json
[
  {
    "id": 0,
    "text": "検索用テキスト（問題の説明）",
    "metadata": {
      "report_id": 49,
      "report_cd": "0308070101",
      "work_symptom": "問題の症状",
      "work_detail": "解決策の詳細",
      "device": "デバイス名",
      "error_code": "エラーコード",
      "total_fee": 0
    }
  }
]
```

**フィールド説明：**

| フィールド | 必須 | 説明 | 例 |
|-----------|------|------|-----|
| `id` | ○ | 一意のID | 0, 1, 2... |
| `text` | ○ | 検索対象のテキスト | "カット機が動かない [Device: FC1309]" |
| `metadata.report_id` | ○ | レポートID | 49 |
| `metadata.report_cd` | ○ | レポートコード | "0308070101" |
| `metadata.work_symptom` | ○ | 問題の症状 | "サーボエラー" |
| `metadata.work_detail` | ○ | 解決策 | "MPU基板交換" |
| `metadata.device` | - | デバイス名 | "Kongsberg XL44" |
| `metadata.error_code` | - | エラーコード | "M001032" |
| `metadata.total_fee` | - | 費用 | 20475 |

**実際のデータ例：**
```json
[
  {
    "id": 0,
    "text": "カット機とPCが繋がらない。ソフトが落ちてしまう。 [Device: FC1309]",
    "metadata": {
      "report_id": 49,
      "report_cd": "0308070101",
      "work_symptom": "カット機とPCが繋がらない。ソフトが落ちてしまう。",
      "work_detail": "PCの不具合のため交換を薦める。",
      "device": "FC1309",
      "error_code": "",
      "total_fee": 0
    }
  },
  {
    "id": 1,
    "text": "バイブレーションツールDCケーブル破損 [Device: KongsbergXL22]",
    "metadata": {
      "report_id": 50,
      "report_cd": "0408082502",
      "work_symptom": "バイブレーションツールDCケーブル破損",
      "work_detail": "DCケーブル交換",
      "device": "KongsbergXL22",
      "error_code": "",
      "total_fee": 20475
    }
  }
]
```

### データを取り込み

```bash
uv run python -m src.ingest
```

データサイズとハードウェアにより、1〜10分かかります。

### APIを起動

```bash
uv run uvicorn src.main:app --host 0.0.0.0 --port 8769
```

### ブラウザで開く

- API：http://localhost:8769
- ドキュメント（ここでクエリを試せます）：http://localhost:8769/docs
- Qdrantダッシュボード：http://localhost:6333

---

## データの準備

### CSVからJSONへの変換

CSVファイルをお持ちの場合、以下のスクリプトで変換：

```python
import csv
import json

data = []
with open('your_data.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        data.append({
            "id": i,
            "text": f"{row['問題']} [Device: {row['デバイス']}]",
            "metadata": {
                "report_id": i,
                "report_cd": row.get('コード', ''),
                "work_symptom": row['問題'],
                "work_detail": row['解決策'],
                "device": row.get('デバイス', ''),
                "error_code": row.get('エラーコード', ''),
                "total_fee": int(row.get('費用', 0))
            }
        })

with open('data/tech_reports_rag.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

### SQLデータベースからの変換

SQLダンプをお持ちの場合：

1. `scripts/prepare_data.py` を使用
2. または、SQLからJSONにエクスポートしてから上記の形式に変換

### データのポイント

- `text` フィールドには検索したい内容を含める
- `[Device: 名前]` のようにデバイス名を追加すると検精度が上がる
- 日本語、英語、どちらでもOK
- エラーコードがあるとより正確な検索が可能

---

## 使用例

### Curlでテスト

```bash
curl -X POST http://localhost:8769/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query": "カット機 動かない", "top_k": 5}'
```

### ドキュメントインターフェースの使用

1. ブラウザで http://localhost:8769/docs を開く
2. `/POST /rag/query` をクリック
3. 「Try it out」をクリック
4. 質問とtop_k値を入力
5. 「Execute」をクリック

### 質問例

日本語：
- "カット機が動かない"
- "レーザーヘッドが動作しない"
- "X軸エラー"
- "サーボモーターの故障"

英語：
- "Cutting machine not responding"
- "Laser head error"
- "Servo motor failure"

---

## デプロイメントモード

### モード1：ハイブリッド（開発向け）

- **取り込み**：コンピュータで実行（GPUがあれば）
- **データベース**：Docker内のQdrant
- **API**：ローカルで実行

NVIDIA GPUがある場合に最適。

```bash
./run.sh 1         # Linux/macOS（プラグイン）
./run-legacy.sh 1  # Linux/macOS（レガシー）
run.bat 1          # Windows（プラグイン）
run-legacy.bat 1   # Windows（レガシー）
```

### モード2：フルDocker（デプロイメント向け）

すべてDockerコンテナで実行。

```bash
./run.sh 2         # Linux/macOS（プラグイン）
./run-legacy.sh 2  # Linux/macOS（レガシー）
run.bat 2          # Windows（プラグイン）
run-legacy.bat 2   # Windows（レガシー）
```

---

## 設定

例示ファイルをコピーして編集：

```bash
cp .env.example .env
```

設定項目：

| 設定 | 説明 | デフォルト |
|------|------|-----------|
| `LLM_BASE_URL` | LM Studioのアドレス | http://localhost:1234/v1 |
| `LLM_MODEL` | LM Studioのモデル名 | qwen3.5-2b |
| `EMBEDDING_DEVICE` | "cuda"（GPU用）または"cpu" | cuda |
| `QDRANT_URL` | Qdrantのアドレス | http://localhost:6333 |
| `API_PORT` | APIのポート | 8769 |

---

## 埋め込みモデル

ハードウェアに応じて最適なモデルを自動選択：

| ハードウェア | モデル | 次元 | 速度 |
|------------|--------|------|------|
| NVIDIA GPU | BAAI/bge-m3 | 1024 | 高速 |
| CPUのみ | intfloat/multilingual-e5-small | 384 | より高速 |

GPUがあればBGE-M3が使用され、品質が向上。なければ、日本語対応のより小さい高速モデルに切替。

---

## トラブルシューティング

### "docker: command not found"

Dockerがインストールされていません。[前提条件](#前提条件) セクションを参照。

### "LM Studio connection error"

1. LM Studioが実行されているか確認
2. LM Studioで「Start Server」をクリック
3. `.env` のURLが正しいか確認（デフォルト：http://localhost:1234）

### "No relevant information found"

- 別のキーワードを試す
- 取り込みを実行したか確認（`uv run python -m src.ingest`）
- データが `data/tech_reports_rag.json` にあるか確認

### Qdrantエラー

ベクトルデータベースをリセット：
```bash
rm -rf vectors/qdrant-data
uv run python -m src.ingest
```

### メモリ不足

CPUで実行中、メモリが不足している場合：
1. `src/ingest.py` のバッチサイズを削減
2. またはRAMを追加

---

## APIエンドポイント

| エンドポイント | メソッド | 説明 |
|--------------|---------|------|
| `/rag/query` | POST | 質問する（AI使用） |
| `/rag/search` | POST | 検索のみ（AIなし） |
| `/rag/ingest` | POST | データの再取り込み |
| `/health` | GET | 実行中か確認 |
| `/` | GET | API情報 |

---

## プロジェクト構成

```
RagNeuron/
├── src/
│   ├── config.py        # 設定
│   ├── ingest.py        # データ取り込み
│   ├── rag.py          # 検索ロジック
│   └── main.py         # APIサーバー
├── scripts/
│   └── prepare_data.py  # データ準備
├── data/               # データ配置場所
├── vectors/            # ベクトルデータベース
├── docker-compose.yml  # Dockerサービス
├── Dockerfile         # Dockerイメージ
├── run.sh             # Linux/macOSランチャー（Docker Compose）
├── run.bat            # Windowsランチャー（Docker Compose）
├── run-legacy.sh      # Linux/macOSランチャー（レガシーdocker-compose）
├── run-legacy.bat     # Windowsランチャー（レガシーdocker-compose）
└── pyproject.toml     # Pythonパッケージ
```

---

## 技術スタック

- **埋め込み**：BAAI/bge-m3 または multilingual-e5-small
- **ベクトルデータベース**：Qdrant
- **LLM**：LM Studio（またはOpenAI）経由でローカル
- **API**：FastAPI
- **パッケージマネージャ**：uv

---

## ライセンス

MIT - 自由に使用・改変・配布可能。

---

## サポート

GitHubでIssueを作成してください。

---
---

<a name="english"></a>
# RagNeuron

A RAG (Retrieval Augmented Generation) system for searching technical support reports. Ask questions in plain language and get answers from past repair cases.

**No ML/AI background needed!** This guide walks you through every step.

---

## What Does This Do?

You have a database of past repair records (in any language, like Japanese). Instead of manually searching through them, you can ask questions like:

- "My cutting machine shows servo error, what should I do?"
- "The laser head is not responding"
- "X-axis not moving"

RagNeuron finds the most similar past cases and uses AI to give you a helpful answer.

---

## Prerequisites

Before starting, you need 3 things:

### 1. Python (already on most computers)

Check if you have it:
```bash
python --version
```

If not, download from [python.org](https://www.python.org/downloads/)

### 2. Docker (for the vector database)

**Windows:**
1. Download Docker Desktop from [docker.com](https://www.docker.com/get-started/)
2. Install it
3. Start Docker Desktop

**macOS:**
```bash
brew install --cask docker
```

**Linux (Ubuntu):**
```bash
sudo apt update
# Option A: Docker Compose plugin (recommended)
sudo apt install docker.io docker-compose-plugin
# Option B: Legacy standalone docker-compose
sudo apt install docker.io docker-compose
sudo systemctl start docker
```

Verify Docker is running:
```bash
docker --version
```

### 3. LM Studio (for AI answers)

Download from [lmstudio.ai](https://lmstudio.ai/)

1. Download and install LM Studio
2. Open LM Studio
3. Download a model (recommended: Qwen3.5-2B or similar)
4. Click "Start Server" (usually at port 1234)

---

## Installation

### Step 1: Get the Code

**Option A: Download ZIP**
1. Go to the GitHub repo
2. Click the green "Code" button
3. Click "Download ZIP"
4. Extract to a folder

**Option B: Using Git**
```bash
git clone https://github.com/nakul-nsksystem/RagNeuron.git
cd RagNeuron
```

### Step 2: Install uv

uv is a fast Python package manager.

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Or use pip:
```bash
pip install uv
```

### Step 3: Install Python Dependencies

```bash
cd RagNeuron
uv sync
```

This automatically creates a virtual environment and installs all packages.

---

## Quick Start (One Command)

After installing everything, run:

```bash
# Linux/macOS (Docker Compose plugin)
./run.sh

# Linux/macOS (legacy docker-compose)
./run-legacy.sh

# Windows (Docker Compose plugin)
run.bat

# Windows (legacy docker-compose)
run-legacy.bat
```

**Which script to use?**
- `run.sh` / `run.bat` → `docker compose` (subcommand, Compose v2+)
- `run-legacy.sh` / `run-legacy.bat` → `docker-compose` (standalone binary)

Use the `-legacy` variant if you get `unknown shorthand flag: 'd'` or `'compose' is not a docker command` errors.

The script will:
1. Detect if you have a GPU
2. Ask which mode you want
3. Start everything for you

---

## Manual Setup (If You Prefer)

### Start Qdrant (Vector Database)

```bash
# Docker Compose plugin
docker compose up -d qdrant
# Legacy docker-compose
docker-compose up -d qdrant
```

Wait 3 seconds for it to start.

### Add Your Data

Place your JSON data file as `data/tech_reports_rag.json`

**Required Format:**
```json
[
  {
    "id": 0,
    "text": "Search text (problem description)",
    "metadata": {
      "report_id": 49,
      "report_cd": "0308070101",
      "work_symptom": "Problem symptoms",
      "work_detail": "Solution details",
      "device": "Device name",
      "error_code": "Error code",
      "total_fee": 0
    }
  }
]
```

**Field Descriptions:**

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| `id` | Yes | Unique ID | 0, 1, 2... |
| `text` | Yes | Text to search | "Cutting machine not responding [Device: FC1309]" |
| `metadata.report_id` | Yes | Report ID | 49 |
| `metadata.report_cd` | Yes | Report code | "0308070101" |
| `metadata.work_symptom` | Yes | Problem symptoms | "Servo error" |
| `metadata.work_detail` | Yes | Solution | "Replace MPU board" |
| `metadata.device` | No | Device name | "Kongsberg XL44" |
| `metadata.error_code` | No | Error code | "M001032" |
| `metadata.total_fee` | No | Cost | 20475 |

**Real Data Example:**
```json
[
  {
    "id": 0,
    "text": "Cutting machine and PC not connecting. Software crashes. [Device: FC1309]",
    "metadata": {
      "report_id": 49,
      "report_cd": "0308070101",
      "work_symptom": "Cutting machine and PC not connecting. Software crashes.",
      "work_detail": "Recommend PC replacement due to malfunction.",
      "device": "FC1309",
      "error_code": "",
      "total_fee": 0
    }
  },
  {
    "id": 1,
    "text": "Vibration tool DC cable damaged [Device: KongsbergXL22]",
    "metadata": {
      "report_id": 50,
      "report_cd": "0408082502",
      "work_symptom": "Vibration tool DC cable damaged",
      "work_detail": "Replace DC cable",
      "device": "KongsbergXL22",
      "error_code": "",
      "total_fee": 20475
    }
  }
]
```

### Ingest Your Data

```bash
uv run python -m src.ingest
```

This takes 1-10 minutes depending on data size and your hardware.

### Start the API

```bash
uv run uvicorn src.main:app --host 0.0.0.0 --port 8769
```

### Open in Browser

- API: http://localhost:8769
- Docs (try queries here): http://localhost:8769/docs
- Qdrant Dashboard: http://localhost:6333

---

## Preparing Your Data

### Converting CSV to JSON

If you have a CSV file, use this script to convert:

```python
import csv
import json

data = []
with open('your_data.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        data.append({
            "id": i,
            "text": f"{row['problem']} [Device: {row['device']}]",
            "metadata": {
                "report_id": i,
                "report_cd": row.get('code', ''),
                "work_symptom": row['problem'],
                "work_detail": row['solution'],
                "device": row.get('device', ''),
                "error_code": row.get('error_code', ''),
                "total_fee": int(row.get('cost', 0))
            }
        })

with open('data/tech_reports_rag.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

### Converting from SQL Database

If you have SQL dumps:

1. Use `scripts/prepare_data.py`
2. Or export SQL to JSON and convert to the format above

### Data Tips

- Include searchable content in the `text` field
- Adding `[Device: name]` improves search accuracy
- Works with Japanese, English, or any language
- Error codes help with more precise searches

---

## Usage Examples

### Test with Curl

```bash
curl -X POST http://localhost:8769/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query": "cutting machine not responding", "top_k": 5}'
```

### Using the Docs Interface

1. Open http://localhost:8769/docs in your browser
2. Click on `/POST /rag/query`
3. Click "Try it out"
4. Enter your question and top_k value
5. Click "Execute"

### Example Questions

In English:
- "Cutting machine not responding"
- "Laser head error"
- "Servo motor failure"

In Japanese:
- "カット機が動かない"
- "レーザーヘッドが動作しない"
- "X軸エラー"

---

## Deployment Modes

### Mode 1: Hybrid (Recommended for development)

- **Ingestion**: Runs on your computer (GPU if available)
- **Database**: Qdrant in Docker
- **API**: Runs locally

Best if you have an NVIDIA GPU.

```bash
./run.sh 1         # Linux/macOS (plugin)
./run-legacy.sh 1  # Linux/macOS (legacy)
run.bat 1          # Windows (plugin)
run-legacy.bat 1   # Windows (legacy)
```

### Mode 2: Full Docker (Recommended for deployment)

Everything runs in Docker containers.

```bash
./run.sh 2         # Linux/macOS (plugin)
./run-legacy.sh 2  # Linux/macOS (legacy)
run.bat 2          # Windows (plugin)
run-legacy.bat 2   # Windows (legacy)
```

---

## Configuration

Copy the example file and edit:

```bash
cp .env.example .env
```

Settings:

| Setting | Description | Default |
|---------|-------------|---------|
| `LLM_BASE_URL` | LM Studio address | http://localhost:1234/v1 |
| `LLM_MODEL` | Model name in LM Studio | qwen3.5-2b |
| `EMBEDDING_DEVICE` | "cuda" for GPU, "cpu" for CPU | cuda |
| `QDRANT_URL` | Qdrant address | http://localhost:6333 |
| `API_PORT` | API port | 8769 |

---

## Embedding Models

The system automatically selects the best model for your hardware:

| Hardware | Model | Dimensions | Speed |
|----------|-------|------------|-------|
| NVIDIA GPU | BAAI/bge-m3 | 1024 | Fast |
| CPU only | intfloat/multilingual-e5-small | 384 | Faster |

If you have a GPU, it uses BGE-M3 for better quality. If not, it switches to a smaller, faster model that still handles Japanese well.

---

## Troubleshooting

### "docker: command not found"

Docker is not installed. Follow the [Prerequisites](#prerequisites) section above.

### "LM Studio connection error"

1. Make sure LM Studio is running
2. Click "Start Server" in LM Studio
3. Check that the URL in `.env` matches (default: http://localhost:1234)

### "No relevant information found"

- Try different keywords
- Make sure you've run ingestion (`uv run python -m src.ingest`)
- Check that your data is in `data/tech_reports_rag.json`

### Qdrant errors

Reset the vector database:
```bash
rm -rf vectors/qdrant-data
uv run python -m src.ingest
```

### Out of memory

If running on CPU and memory is low:
1. Reduce batch size in `src/ingest.py`
2. Or add more RAM

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/rag/query` | POST | Ask a question (uses AI) |
| `/rag/search` | POST | Search only (no AI) |
| `/rag/ingest` | POST | Re-ingest your data |
| `/health` | GET | Check if running |
| `/` | GET | API info |

---

## Project Structure

```
RagNeuron/
├── src/
│   ├── config.py        # Settings
│   ├── ingest.py        # Import data
│   ├── rag.py          # Search logic
│   └── main.py         # API server
├── scripts/
│   └── prepare_data.py  # Data preparation
├── data/               # Your data goes here
├── vectors/            # Vector database
├── docker-compose.yml  # Docker services
├── Dockerfile         # Docker image
├── run.sh             # Linux/macOS launcher (Docker Compose plugin)
├── run.bat            # Windows launcher (Docker Compose plugin)
├── run-legacy.sh      # Linux/macOS launcher (legacy docker-compose)
├── run-legacy.bat     # Windows launcher (legacy docker-compose)
└── pyproject.toml     # Python packages
```

---

## Tech Stack

- **Embeddings**: BAAI/bge-m3 or multilingual-e5-small
- **Vector Database**: Qdrant
- **LLM**: Local via LM Studio (or OpenAI)
- **API**: FastAPI
- **Package Manager**: uv

---

## License

MIT - Do whatever you want with it.

---

## Support

Open an issue on GitHub if you need help.
