from typing import Any

from app.extensions import db
from app.models.notificacao import Notificacao


def _ja_notificado(usuario_id: int, produto_id: int, tipo: str) -> bool:
    """Retorna True se já existe uma notificação não-lida desse tipo para o produto.

    Evita criar duplicatas enquanto o produto permanece em risco.
    Quando o usuário marca como lida, a próxima rodada do job pode notificar de novo
    (caso o produto ainda esteja em risco), o que é o comportamento desejado.
    """
    return (
        db.session.query(Notificacao)
        .filter_by(usuario_id=usuario_id, produto_id=produto_id, tipo=tipo, lida=False)
        .first()
        is not None
    )


class InAppSubscriber:
    _eventos = {
        "produto_vencendo": (
            "validade_proxima",
            lambda nome, dias: (
                f"{nome} vence em {dias} dia(s)."
                if dias is not None
                else f"{nome} está próximo do vencimento."
            ),
        ),
        "produto_vencido": (
            "validade_expirada",
            lambda nome, _dias: f"{nome} venceu.",
        ),
        "garantia_vencendo": (
            "garantia_proxima",
            lambda nome, dias: (
                f"Garantia de {nome} expira em {dias} dia(s)."
                if dias is not None
                else f"Garantia de {nome} está próxima do fim."
            ),
        ),
        "garantia_vencida": (
            "garantia_expirada",
            lambda nome, _dias: f"Garantia de {nome} expirou.",
        ),
    }

    def notify(self, event_name: str, payload: dict[str, Any]) -> None:
        produto = payload.get("produto")
        if produto is None or not getattr(produto, "usuario_id", None):
            return

        config = self._eventos.get(event_name)
        if config is None:
            return
        tipo, montar_mensagem = config

        if _ja_notificado(produto.usuario_id, produto.id, tipo):
            return

        notificacao = Notificacao(
            mensagem=montar_mensagem(produto.nome, payload.get("dias")),
            tipo=tipo,
            usuario_id=produto.usuario_id,
            produto_id=produto.id,
        )
        db.session.add(notificacao)
        db.session.commit()


class EmailSubscriber:
    """Envia email via Resend, com a mesma deduplicação do InAppSubscriber.

    Usa o tipo prefixado com "email_" para rastrear separadamente do in-app,
    permitindo que o usuário receba email mesmo sem ter aberto o app.
    """

    _eventos = {
        "produto_vencendo": (
            "email_validade_proxima",
            lambda nome, dias: (
                f"⚠️ {nome} vence em {dias} dia(s).",
                f"O produto <strong>{nome}</strong> está próximo do vencimento "
                f"(<strong>{dias} dia(s)</strong> restantes).<br><br>"
                "Acesse o Keepr para tomar uma providência.",
            ),
        ),
        "garantia_vencendo": (
            "email_garantia_proxima",
            lambda nome, dias: (
                f"🔧 Garantia de {nome} expira em {dias} dia(s).",
                f"A garantia de <strong>{nome}</strong> expira em "
                f"<strong>{dias} dia(s)</strong>.<br><br>"
                "Acesse o Keepr para verificar a documentação ou acionar a garantia.",
            ),
        ),
    }

    def notify(self, event_name: str, payload: dict[str, Any]) -> None:
        import resend
        from flask import current_app

        config = self._eventos.get(event_name)
        if config is None:
            return

        produto = payload.get("produto")
        if produto is None or not getattr(produto, "usuario_id", None):
            return

        tipo_email, montar = config
        dias = payload.get("dias")

        if _ja_notificado(produto.usuario_id, produto.id, tipo_email):
            return

        from app.models.usuario import Usuario
        usuario = db.session.get(Usuario, produto.usuario_id)
        if usuario is None:
            return

        api_key = current_app.config.get("RESEND_API_KEY", "")
        email_from = current_app.config.get("EMAIL_FROM", "Keepr <onboarding@resend.dev>")
        if not api_key:
            print("[EmailSubscriber] RESEND_API_KEY não configurada — email não enviado")
            return

        assunto, corpo_html = montar(produto.nome, dias)

        resend.api_key = api_key
        email_to = current_app.config.get("EMAIL_TO_OVERRIDE") or usuario.email
        try:
            resend.Emails.send({
                "from": email_from,
                "to": [email_to],
                "subject": assunto,
                "html": _html_email(assunto, corpo_html, usuario.nome),
            })
            print(f"[EmailSubscriber] email enviado para {usuario.email} — {assunto}")
        except Exception as exc:
            print(f"[EmailSubscriber] erro ao enviar email: {exc}")
            return

        notif_controle = Notificacao(
            mensagem=assunto,
            tipo=tipo_email,
            usuario_id=produto.usuario_id,
            produto_id=produto.id,
            lida=False,
        )
        db.session.add(notif_controle)
        db.session.commit()


def _html_email(assunto: str, corpo: str, nome_usuario: str) -> str:
    return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"></head>
<body style="font-family: sans-serif; background: #f9f7f4; margin: 0; padding: 32px;">
  <div style="max-width: 480px; margin: 0 auto; background: #ffffff;
              border-radius: 12px; border: 1px solid #e8e2da; overflow: hidden;">
    <div style="background: #1a1a1a; padding: 20px 28px;">
      <span style="color: #ffffff; font-size: 18px; font-weight: 700; letter-spacing: -0.5px;">
        Keepr
      </span>
    </div>
    <div style="padding: 28px;">
      <p style="color: #555; font-size: 14px; margin: 0 0 16px;">
        Olá, <strong>{nome_usuario}</strong>
      </p>
      <p style="color: #1a1a1a; font-size: 15px; line-height: 1.6; margin: 0 0 24px;">
        {corpo}
      </p>
      <a href="http://localhost:5173"
         style="display: inline-block; background: #1a1a1a; color: #ffffff;
                text-decoration: none; padding: 10px 20px; border-radius: 8px;
                font-size: 14px; font-weight: 600;">
        Abrir Keepr
      </a>
    </div>
    <div style="padding: 16px 28px; border-top: 1px solid #e8e2da;">
      <p style="color: #aaa; font-size: 11px; margin: 0;">
        Nada vence esquecido · Keepr
      </p>
    </div>
  </div>
</body>
</html>
"""
