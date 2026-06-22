# Guia de Deploy — Keepr

Stack de hospedagem (todos com plano gratuito disponível):

| Camada | Plataforma | Custo |
|---|---|---|
| Banco de dados | **Neon** (PostgreSQL gerenciado) | Gratuito |
| Backend Flask | **Render** (Web Service) | Gratuito |
| Frontend React | **Vercel** | Gratuito |

> **Atenção — Vercel não serve para o backend Flask.**
> O Vercel executa funções serverless que morrem após cada requisição.
> O APScheduler (notificações automáticas diárias) precisa de um processo persistente,
> que só o Render Web Service oferece. Use Vercel apenas para o frontend.

---

## 1. Banco de dados — Neon

1. Acesse **neon.tech** → crie uma conta → **New Project**
2. Escolha a região mais próxima (ex: `us-east-1` ou `eu-central-1`)
3. Após criar, vá em **Dashboard → Connection string** e copie a URL no formato:
   ```
   postgresql://usuario:senha@ep-xxx.neon.tech/nomedb?sslmode=require
   ```
4. Guarde essa URL — ela será `DATABASE_URL` no Render.

> O `db.create_all()` cria todas as tabelas automaticamente no primeiro boot.
> Não há migrations para rodar.

---

## 2. Backend — Render

### Opção A — Blueprint automático (recomendado)

O repositório já tem `render.yaml` na raiz que configura tudo automaticamente.

1. Acesse **dashboard.render.com** → **New → Blueprint**
2. Conecte o repositório GitHub
3. O Render lê o `render.yaml` e cria o serviço `keepr-api`
4. Adicione manualmente as variáveis extras listadas abaixo
5. Clique em **Apply** e aguarde o build (~3 min)

### Opção B — Web Service manual

1. **New → Web Service** → conecte o repositório
2. Configure:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn run:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120`
3. Siga para as variáveis de ambiente abaixo

### Variáveis de ambiente no Render

No painel do serviço → **Environment**, adicione:

| Variável | Valor | Obrigatório |
|---|---|---|
| `DATABASE_URL` | URL do Neon (passo 1) | ✅ |
| `SECRET_KEY` | string aleatória longa (32+ chars) | ✅ |
| `JWT_SECRET_KEY` | outra string aleatória | ✅ |
| `OCR_PROVIDER` | `gemini` | ✅ |
| `GEMINI_API_KEY` | sua chave do Google AI Studio | ✅ |
| `GEMINI_MODEL` | `gemini-3.5-flash` | ✅ |
| `RESEND_API_KEY` | sua chave do Resend | ✅ |
| `EMAIL_FROM` | `Keepr <notificacoes@seudominio.com>` | ✅ |
| `EMAIL_TO_OVERRIDE` | seu email (enquanto sem domínio verificado no Resend) | ⚠️ |
| `CORS_ORIGINS` | `https://keepr.vercel.app` (preencher após passo 3) | ✅ |

> Gere strings aleatórias com:
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

Após o deploy, teste:
```
GET https://keepr-api.onrender.com/health
→ {"status": "ok"}
```

> **Sobre uploads de comprovantes:** o filesystem do Render free tier é efêmero —
> arquivos são perdidos a cada redeploy. Para o trabalho acadêmico é suficiente.
> Para produção real, migrar para Cloudflare R2 ou S3.

> **Sobre o APScheduler:** funciona normalmente no Render Web Service (processo persistente).
> Com uma instância (plano free), os jobs rodam uma vez ao dia sem duplicação.
> Se escalar para múltiplas instâncias, usar Render Cron Jobs separados no lugar.

---

## 3. Frontend — Vercel

1. Acesse **vercel.com** → **Add New → Project** → importe o repositório
2. Configure:
   - **Root Directory:** `frontend`
   - A Vercel detecta Vite automaticamente pelo `vercel.json`
3. Em **Environment Variables**, adicione:

| Variável | Valor |
|---|---|
| `VITE_API_URL` | URL do backend no Render (ex: `https://keepr-api.onrender.com`) |

4. Clique em **Deploy** e aguarde (~2 min)
5. Anote a URL gerada (ex: `https://keepr.vercel.app`)

> O `vite.config.js` usa `import.meta.env.VITE_API_URL` como `baseURL` do Axios em produção.
> Em desenvolvimento local a variável fica vazia e o proxy do Vite entra em ação automaticamente.
> Nenhuma alteração de código é necessária entre os ambientes.

---

## 4. Fechar o CORS

Com a URL do frontend em mãos, volte ao Render e atualize a variável:

```
CORS_ORIGINS=https://keepr.vercel.app
```

O Render reinicia o serviço automaticamente. Após isso frontend e backend conversam sem bloqueio.

---

## 5. Criar o primeiro administrador

Após o deploy, acesse o **Shell** do Render (painel do serviço → **Shell**) e rode:

```bash
python scripts/promover_admin.py email@exemplo.com
```

Ou registre um usuário normalmente pelo frontend e depois execute o script no Shell do Render.

---

## 6. Rodar localmente (referência rápida)

```bash
# 1. Criar banco local (uma vez)
psql -U postgres -c "CREATE DATABASE keepr;"

# 2. Criar backend/.env com o conteúdo:
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/keepr
SECRET_KEY=dev-secret
JWT_SECRET_KEY=dev-jwt-secret
OCR_PROVIDER=gemini
GEMINI_API_KEY=sua_chave_aqui
GEMINI_MODEL=gemini-3.5-flash
RESEND_API_KEY=sua_chave_resend
EMAIL_FROM=Keepr <onboarding@resend.dev>
EMAIL_TO_OVERRIDE=seuemail@gmail.com

# 3. Backend (porta 5001)
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python run.py

# 4. Frontend (outro terminal)
cd frontend
npm install
npm run dev                  # http://localhost:5173
```

---

## 7. Checklist de verificação pós-deploy

- [ ] `GET https://keepr-api.onrender.com/health` retorna `{"status": "ok"}`
- [ ] Login funciona pelo frontend na Vercel
- [ ] Cadastro de produto funciona
- [ ] Upload de comprovante retorna itens identificados pelo Gemini
- [ ] Notificações in-app aparecem no Dashboard
- [ ] Email de notificação chega ao clicar "Notificar Vencimentos" na tela de Usuários
- [ ] Relatório admin gera corretamente
- [ ] Jobs diários rodam às 08:00 e 08:05 (verificar logs do Render no dia seguinte)
