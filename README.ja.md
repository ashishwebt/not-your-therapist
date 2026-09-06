# Not Your Therapist 🧠

[English](./README.md)

> **明確に「あなたのセラピストではない」AIセラピスト風チャットボット。**

Not Your Therapist は、**React、FastAPI、LangChain、LangGraph、Ollama** を使って構築された、小規模なフルスタック実験プロジェクトです。

ローカル環境で実行できる会話型AIの実験を目的としており、医療サービスやメンタルヘルスサービスではありません。

## ⚠️ 免責事項

**Not Your Therapist は、セラピスト、医師、心理学者、カウンセラー、または医療サービスではありません。**

診断、治療、危機的状況への対応、または専門的なメンタルヘルスに関する判断のために使用しないでください。

緊急事態にある場合、または自分自身が差し迫った危険にさらされていると感じている場合は、地域の緊急サービスまたは資格を持つ専門家に連絡してください。

## Architecture

```text
┌──────────────────────┐
│      React + Vite    │
│      フロントエンド  │
└──────────┬───────────┘
           │ HTTP / SSE
           ▼
┌──────────────────────┐
│       FastAPI        │
│       バックエンド   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ LangChain / LangGraph│
│    エージェント      │
│      サービス        │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│       Ollama         │
│   ローカルLLMランタイム │
└──────────────────────┘
           │
           ▼
┌──────────────────────┐
│ SQLite / チェックポイント │
└──────────────────────┘
```

## Technology

* **フロントエンド:** React 19 + Vite
* **バックエンド:** Python 3.11+ + FastAPI
* **AIオーケストレーション:** LangChain + LangGraph
* **LLMランタイム:** Ollama
* **永続化:** SQLite + SQLAlchemy / aiosqlite
* **ストリーミング:** Server-Sent Events (SSE)
* **テスト:** pytest + pytest-asyncio

バックエンドプロジェクトでは、FastAPI、LangChain、LangGraph のチェックポイント機能、LangChain-Ollama、SQLAlchemy、SQLite関連の依存関係、および Uvicorn が定義されています。

## Project Structure

```text
not-your-therapist/
├── backend/
│   ├── app/
│   │   ├── agent_services/
│   │   ├── repository/
│   │   ├── dependencies.py
│   │   ├── routes.py
│   │   ├── schemas.py
│   │   └── sse_helper.py
│   ├── tests/
│   ├── main.py
│   ├── pyproject.toml
│   └── .env.example
│
└── not-your-therapist/
    ├── src/
    ├── package.json
    └── vite.config.*
```

## Prerequisites

* Python **3.11+**
* Node.js と npm
* Ollama
* 使用するマシンに適した Ollama モデル

## Getting Started

### 1. Clone

```bash
git clone https://github.com/ashishwebt/not-your-therapist.git
cd not-your-therapist
```

### 2. Ollama を起動する

Ollama をインストールして起動し、使用したいモデルを pull します。

例:

```bash
ollama pull llama3.2
```

この例とは異なるモデルがアプリケーションで設定されている場合は、アプリケーションで設定されているモデルを使用してください。

### 3. バックエンドを設定する

```bash
cd backend
cp .env.example .env
```

Windows PowerShell の場合:

```powershell
Copy-Item .env.example .env
```

付属の設定では、以下を使用します。

```env
OLLAMA_BASE_URL=http://localhost:11434
DATABASE_URL=sqlite:///./chat.db
ENVIRONMENT=development
```

### 4. 依存関係をインストールする

バックエンドには `uv.lock` が含まれているため、開発時には `uv` の使用を推奨します。

```bash
uv sync
```

### 5. API を起動する

`backend/` から実行します。

```bash
uv run uvicorn main:app --reload
```

API は以下で利用できるようになります。

```text
http://localhost:8000
```

インタラクティブな API ドキュメント:

```text
http://localhost:8000/docs
```

### 6. フロントエンドを起動する

別のターミナルで:

```bash
cd not-your-therapist
npm install
npm run dev
```

Vite に表示された URL を開いてください。通常は以下です。

```text
http://localhost:5173
```

## Testing

バックエンドのテストを実行します。

```bash
cd backend
uv run pytest
```

このリポジトリには、repository、routes、schemas を対象としたテストが含まれています。

## Frontend Build

```bash
cd not-your-therapist
npm run build
```

本番用ビルドをプレビューするには:

```bash
npm run preview
```

## Configuration

| 変数                | 説明              | デフォルト                    |
| ----------------- | --------------- | ------------------------ |
| `OLLAMA_BASE_URL` | Ollama サーバーのURL | `http://localhost:11434` |
| `DATABASE_URL`    | データベース接続        | `sqlite:///./chat.db`    |
| `ENVIRONMENT`     | アプリケーション環境      | `development`            |

## Why the Name?

AIチャットボットを **「Your Therapist」** と呼ぶのは、驚くほどひどいプロダクト上の意思決定だからです。

そこで、このプロジェクトは真実をそのまま伝えることにしました。

**これは、あなたのセラピストではありません。**

## Development Status

これは実験的なプロジェクトです。

プロジェクトの発展に伴い、アーキテクチャ、エージェントの動作、UI、API は変更される可能性があります。

コントリビューションやアイデアを歓迎します。

## License

ライセンスに関する情報は [LICENSE](LICENSE) を参照してください。
