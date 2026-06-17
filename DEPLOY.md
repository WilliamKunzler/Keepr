# Deploy do Keepr

Guia para colocar o sistema **online** com **PostgreSQL** (requisito do Trabalho III —
SQLite não é aceito). Arquitetura de hospedagem (todos com plano gratuito):

| Camada | Plataforma | Arquivo de config |
|---|---|---|
| Banco | Neon ou Supabase (PostgreSQL) | — |
| Backend (API Flask) | Render | `render.yaml`, `backend/Procfile` |
| Frontend (React/Vite) | Vercel | `frontend/vercel.json` |

---

## 1. Banco de dados (PostgreSQL na nuvem)

Escolha **uma** opção:

- **Neon** (https://neon.tech) → crie um projeto → copie a *connection string*
  (formato `postgresql://user:senha@host/db`).
- **Supabase** (https://supabase.com) → New project → Settings → Database →
  *Connection string* (modo "URI").
- **Render** → o `render.yaml` já cria um Postgres gerenciado (`keepr-db`) automaticamente;
  nesse caso pode pular esta etapa.

Guarde a URL — ela vira a variável `DATABASE_URL`.

> O `db.create_all()` cria as tabelas no primeiro boot — não há migrations a rodar.

---

## 2. Backend na Render

### Opção A — Blueprint (recomendado, usa o `render.yaml`)
1. https://dashboard.render.com → **New → Blueprint**.
2. Conecte o repositório `RIGOandre/keepr`.
3. A Render lê o `render.yaml`, cria o serviço **keepr-api** + o banco **keepr-db**
   e injeta `DATABASE_URL`, `SECRET_KEY` e `JWT_SECRET_KEY` automaticamente.
4. Após o deploy, anote a URL pública (ex.: `https://keepr-api.onrender.com`).

### Opção B — Web Service manual
1. **New → Web Service** → conecte o repo.
2. **Root Directory:** `backend`
3. **Build Command:** `pip install -r requirements.txt`
4. **Start Command:** `gunicorn run:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
5. **Environment** (aba Environment):
   - `DATABASE_URL` = a URL do passo 1
   - `SECRET_KEY` = (qualquer string aleatória longa)
   - `JWT_SECRET_KEY` = (outra string aleatória)
   - `OCR_PROVIDER` = `ocrspace`
   - `OCRSPACE_API_KEY` = `helloworld` (ou uma key própria de ocr.space)
   - `CORS_ORIGINS` = a URL do frontend na Vercel (preencher após o passo 3)

> Teste: `GET https://keepr-api.onrender.com/health` deve responder `{"status":"ok"}`.

---

## 3. Frontend na Vercel

1. https://vercel.com → **Add New → Project** → importe o repo.
2. **Root Directory:** `frontend`
3. A Vercel detecta Vite automaticamente (`vercel.json` já define build/output/rewrites).
4. **Environment Variables:**
   - `VITE_API_URL` = a URL do backend na Render (ex.: `https://keepr-api.onrender.com`)
5. Deploy → anote a URL (ex.: `https://keepr.vercel.app`).

---

## 4. Fechar o CORS

Volte na Render e ajuste a env `CORS_ORIGINS` do backend para o domínio real do frontend:

```
CORS_ORIGINS=https://keepr.vercel.app
```

Salve (a Render reinicia o serviço). Pronto — frontend e backend conversando.

---

## 5. Rodar localmente com PostgreSQL

```bash
# 1. Banco local (uma vez)
createdb keepr            # ou: psql -U postgres -c "CREATE DATABASE keepr;"

# 2. backend/.env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/keepr
OCR_PROVIDER=ocrspace
OCRSPACE_API_KEY=helloworld

# 3. Backend
cd backend
python -m venv venv && venv\Scripts\activate     # Windows
pip install -r requirements.txt
python run.py                                     # http://localhost:5000

# 4. Frontend (outro terminal)
cd frontend
npm install
npm run dev                                        # http://localhost:5173
```

---

## Notas

- O `gunicorn` é o servidor de produção (Linux); localmente no Windows continue usando
  `python run.py`.
- O `uploads/` da Render é **efêmero** (some a cada redeploy). Para uso acadêmico tudo bem;
  para persistência real usar um bucket (S3/Supabase Storage).
- Plano free da Render **hiberna** após inatividade — a primeira requisição pode demorar
  alguns segundos. Mantenha o serviço ativo perto da apresentação.
- A normalização `postgres://` → `postgresql://` já está no `config.py`, então qualquer
  provedor funciona.
