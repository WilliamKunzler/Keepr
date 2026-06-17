"""Script avulso para disparar os jobs de verificação fora do scheduler.

Útil pra validar manualmente o fluxo EventBus → InAppSubscriber → DB.
Não faz parte da aplicação — só roda quando invocado direto:

    python scripts/disparar_job.py validade
    python scripts/disparar_job.py garantia
"""
import sys
from pathlib import Path

# Permite rodar de dentro de scripts/ sem precisar setar PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from app.jobs.verificar_garantia import verificar_garantia
from app.jobs.verificar_validade import verificar_validade

JOBS = {"validade": verificar_validade, "garantia": verificar_garantia}


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in JOBS:
        print(f"uso: python scripts/disparar_job.py [{'|'.join(JOBS)}]")
        sys.exit(1)

    app = create_app()
    with app.app_context():
        JOBS[sys.argv[1]]()


if __name__ == "__main__":
    main()
