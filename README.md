## MultiAgent 营销内容工厂（MVP）

本项目实现一套可编排、可审计、可扩展到 SaaS 的多 Agent 内容生产系统（MVP 先以“人工审核 + 导出发布包”为主）。

### 目录
- `backend/`：FastAPI API + 工作流编排 + Celery 任务执行 + RAG/知识沉淀
- `frontend/`：Web 控制台（MVP 简化版）

### 本地运行（无需 Docker）
#### 1) 后端
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

copy .env.example .env
python -m app.scripts.init_db
uvicorn app.main:app --reload --port 8000
```

打开 `http://127.0.0.1:8000/docs` 查看 API。

#### 2) Worker（可选，跑异步流水线）
> MVP 支持“同步执行”与“异步执行”两种模式；没有 Redis 也能跑同步模式。

```bash
cd backend
.venv\Scripts\activate
celery -A app.worker.celery_app worker -l INFO
```

### 环境变量
见 `backend/.env.example`。

