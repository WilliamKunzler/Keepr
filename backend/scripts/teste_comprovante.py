"""Smoke test end-to-end do fluxo de comprovantes com OCR real.

1. Gera imagem PNG com texto simulando uma NF
2. POST /comprovantes/ (upload + OCR + identificação)
3. POST /comprovantes/<id>/confirmar com produtos revisados
4. GET /comprovantes/ + DELETE

Roda fora da app — apenas usa requests + PIL.
"""
import io
import json
import sys
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

BASE = "http://localhost:5000"

NF_TEXTO = [
    "SUPERMERCADO KEEPR",
    "CNPJ 12.345.678/0001-90",
    "Data: 09/06/2026",
    "",
    "LEITE INTEGRAL 1L    R$ 6,50",
    "QUEIJO MINAS 500G    R$ 28,75",
    "CAFE TORRADO 500G    R$ 15,90",
    "",
    "TOTAL              R$ 51,15",
    "Forma de pagamento: dinheiro",
]


def gerar_imagem_nf() -> bytes:
    img = Image.new("RGB", (520, 360), color="white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except OSError:
        font = ImageFont.load_default()
    y = 20
    for linha in NF_TEXTO:
        draw.text((20, y), linha, fill="black", font=font)
        y += 28
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def call(method, path, **kw):
    r = requests.request(method, f"{BASE}{path}", timeout=60, **kw)
    try:
        return r.status_code, r.json()
    except ValueError:
        return r.status_code, r.text


def main() -> None:
    # login admin
    code, body = call("POST", "/auth/login", json={
        "email": "rigo+test@keepr.local", "senha": "secret123"
    })
    assert code == 200, body
    token = body["access_token"]
    auth = {"Authorization": f"Bearer {token}"}
    print("login ok")

    # gerar e upload
    img = gerar_imagem_nf()
    Path("ultima_nf_teste.png").write_bytes(img)  # debug

    code, body = call("POST", "/comprovantes/", headers=auth, files={
        "arquivo": ("nf.png", img, "image/png")
    })
    print(f"\n=== POST /comprovantes/ -> {code} ===")
    print(json.dumps(body, indent=2, ensure_ascii=False))
    if code != 201:
        sys.exit(1)
    comp_id = body["comprovante"]["id"]
    itens = body["comprovante"]["itens_identificados"]
    valor = body["comprovante"]["valor_total"]
    texto = body["comprovante"]["texto_extraido"] or ""
    print(f"\n-> itens identificados: {len(itens)}")
    print(f"-> valor_total detectado: {valor}")
    print(f"-> tamanho texto OCR: {len(texto)} chars")

    # confirmar com 2 produtos (1 de validade + 1 de garantia)
    payload = {
        "produtos": [
            {
                "tipo": "validade",
                "nome": "Leite Integral 1L",
                "data_validade": "2026-07-15",
            },
            {
                "tipo": "garantia",
                "nome": "Cafeteira",
                "data_compra": "2026-06-09",
                "garantia_meses": 12,
            },
        ]
    }
    code, body = call("POST", f"/comprovantes/{comp_id}/confirmar", headers=auth, json=payload)
    print(f"\n=== POST /comprovantes/{comp_id}/confirmar -> {code} ===")
    print(json.dumps(body, indent=2, ensure_ascii=False))
    assert code == 201, body
    assert body["comprovante"]["confirmado"] is True
    assert len(body["produtos"]) == 2

    # GET lista
    code, body = call("GET", "/comprovantes/", headers=auth)
    print(f"\n=== GET /comprovantes/ -> {code} (total={len(body['comprovantes'])}) ===")

    # Re-confirmar deve dar 409
    code, body = call("POST", f"/comprovantes/{comp_id}/confirmar", headers=auth, json=payload)
    print(f"\n=== POST confirmar duplicado -> {code} (esperado 409) ===")
    assert code == 409

    # DELETE
    code, _ = call("DELETE", f"/comprovantes/{comp_id}", headers=auth)
    print(f"\n=== DELETE /comprovantes/{comp_id} -> {code} (esperado 204) ===")
    assert code == 204

    # produto deve ter comprovante_id=None agora
    code, body = call("GET", "/produtos/", headers=auth)
    pendurados = [p for p in body["produtos"] if "Cafeteira" in p["nome"] or "Leite Integral 1L" in p["nome"]]
    print(f"\n-> produtos restantes apos DELETE comprovante: {len(pendurados)}")
    for p in pendurados:
        print(f"   id={p['id']} nome={p['nome']!r}")

    print("\nOK — fluxo completo verde")


if __name__ == "__main__":
    main()
