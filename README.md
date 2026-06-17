# Keepr

> Guarde notas. Acompanhe garantias. Nada vence esquecido.

Sistema de gestão de validade e garantia de produtos domésticos, com leitura
automática de comprovantes via OCR.

**Trabalho de Programação Orientada a Objetos II — IFC Campus Concórdia**

Autores: André Luiz Vicenzi Rigo · Kauan Lucas Toldo · William Kunzler · Yasmin Maria Zerbielli

---

## Extração no Windows

Se baixou este projeto como `keepr.zip`, abra o arquivo, e extraia a pasta `keepr/`
diretamente em `C:\Users\RIGO\` (ou onde preferir). Depois disso, abra o terminal
naquela pasta:

```cmd
cd C:\Users\RIGO\keepr
```

---

## Stack

**Backend**
- Flask + Flask-SQLAlchemy + Flask-JWT-Extended + Flask-APScheduler + Flask-CORS
- Pydantic (validação) · PostgreSQL · Tesseract (OCR via pytesseract)

**Frontend**
- React 18 + Vite + Tailwind CSS
- Axios · React Query · React Router
- yet-another-react-lightbox + react-zoom-pan-pinch (visualização de comprovantes)

**Padrões aplicados**
- SOLID (SRP, OCP, LSP, ISP, DIP) — distribuídos pelas camadas
- GoF: Factory Method (criação de subtipos de Produto), Facade (orquestração no service), Observer (notificações via EventBus)

---

## Pré-requisitos no SO

- Python 3.11+
- Node.js 18+ e npm
- PostgreSQL 14+ rodando localmente (ou Docker, ver abaixo)
- Tesseract OCR (`sudo apt install tesseract-ocr tesseract-ocr-por` no Ubuntu / `brew install tesseract tesseract-lang` no macOS)

---

## Postgres via Docker (alternativa)

Se não quiser instalar PostgreSQL na máquina, sobe um container com persistência:

```bash
docker run -d --name keepr-postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=keepr -p 5432:5432 -v keepr-pgdata:/var/lib/postgresql/data postgres:17
```

Isso já cria a database `keepr` no boot — pode pular o `CREATE DATABASE` do setup
do backend. Os dados ficam no volume nomeado `keepr-pgdata` e sobrevivem a
recriações do container.

Comandos úteis:

```bash
docker stop keepr-postgres     # pausar
docker start keepr-postgres    # retomar
docker logs -f keepr-postgres  # ver o que tá rolando
docker rm -f keepr-postgres && docker volume rm keepr-pgdata   # zerar tudo
```

---

## Setup do backend

```bash
cd backend

# Cria virtualenv
python -m venv venv
source venv/bin/activate          # Linux/Mac
# venv\Scripts\activate           # Windows

# Instala dependências
pip install -r requirements.txt

# Copia e ajusta variáveis de ambiente
cp .env.example .env
# edite .env com sua DATABASE_URL e secrets

# Cria o banco no PostgreSQL
sudo -u postgres psql -c "CREATE DATABASE keepr;"

# Roda
python run.py
```

O servidor sobe em `http://localhost:5000`. Na primeira execução o `db.create_all()` cria as tabelas e o scheduler agenda os jobs diários de verificação.

## Setup do frontend

```bash
cd frontend

# Instala dependências
npm install

# Roda em modo dev
npm run dev
```

A SPA sobe em `http://localhost:5173`. Ela já está configurada pra chamar o backend em `http://localhost:5000`.

---

## Estrutura de pastas

```
keepr/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # application factory
│   │   ├── config.py            # configurações por ambiente
│   │   ├── extensions.py        # db, jwt, scheduler
│   │   ├── blueprints/          # rotas agrupadas por recurso (camada API)
│   │   ├── models/              # SQLAlchemy + herança polimórfica
│   │   ├── schemas/             # Pydantic DTOs
│   │   ├── services/            # lógica de negócio (Facade, Observer, OCR)
│   │   ├── repositories/        # acesso a dados
│   │   ├── jobs/                # tarefas agendadas
│   │   └── uploads/             # comprovantes salvos
│   ├── tests/
│   ├── requirements.txt
│   ├── run.py
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── api/                 # axios + endpoints
    │   ├── components/          # componentes reutilizáveis
    │   ├── pages/               # telas
    │   ├── hooks/               # hooks customizados
    │   ├── contexts/            # AuthContext
    │   ├── App.jsx
    │   ├── main.jsx
    │   └── index.css            # @tailwind directives
    ├── index.html
    ├── package.json
    ├── tailwind.config.js
    ├── postcss.config.js
    └── vite.config.js
```

---

## Comandos úteis

```bash
# Backend
cd backend && python run.py              # roda servidor dev
cd backend && pytest                     # roda testes

# Frontend
cd frontend && npm run dev               # servidor dev (porta 5173)
cd frontend && npm run build             # build pra produção
cd frontend && npm run preview           # preview do build
```
