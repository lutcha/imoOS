"""
MBE (Multibanco) reference generator — ImoOS Cabo Verde.

Referência Multibanco: ENTIDADE (5 dígitos) + REFERÊNCIA (9 dígitos) + VALOR

This implementation produces a deterministic reference:
    same (contract_id, item_order, amount_cve) → same reference.

In production, integrate with a real MBE gateway (ex: ifthenpay, euPago).
The gateway will validate references against the registered entity and
settle payments directly into the promotora's bank account.
"""

import hashlib


def generate_mbe_reference(contract_id: str, item_order: int, amount_cve: int) -> str:
    """
    Gera referência MBE determinista com 9 dígitos numéricos.

    Args:
        contract_id: UUID string do contrato.
        item_order: Posição do item no plano (0-indexed).
        amount_cve: Valor inteiro em CVE (centavos truncados).

    Returns:
        String de 9 dígitos, com zeros à esquerda se necessário.
    """
    seed = f"{contract_id}:{item_order}:{amount_cve}"
    digest = hashlib.sha256(seed.encode()).hexdigest()
    # Derive 9 numeric digits from the first 8 hex chars
    return str(int(digest[:8], 16) % 10 ** 9).zfill(9)
