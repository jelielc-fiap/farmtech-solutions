from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Recomendacao:
    acao_irrigacao: str
    acao_ph: str
    acao_nutrientes: str
    risco_produtivo: str
    justificativa: str


def recomendar_manejo(
    umidade: float,
    ph: float,
    n_ok: int,
    p_ok: int,
    k_ok: int,
    chuva_probabilidade: float,
    rendimento_estimado: float,
    volume_irrigacao: float,
) -> Recomendacao:
    if umidade < 45 and chuva_probabilidade < 60:
        acao_irrigacao = f"Irrigar {volume_irrigacao:.0f} L/ha nas proximas 24 horas"
    elif umidade < 45 and chuva_probabilidade >= 60:
        acao_irrigacao = "Aguardar chuva e reavaliar a umidade em 12 horas"
    elif chuva_probabilidade >= 75:
        acao_irrigacao = "Suspender irrigacao preventiva"
    elif umidade < 55:
        acao_irrigacao = "Monitorar e deixar irrigacao preparada"
    else:
        acao_irrigacao = "Sem irrigacao necessaria no momento"

    if ph < 5.5:
        acao_ph = "Planejar correcao de acidez com calagem"
    elif ph > 7.0:
        acao_ph = "Revisar manejo para reduzir alcalinidade"
    else:
        acao_ph = "pH dentro da faixa agronomica adequada"

    faltantes = [nome for nome, ok in [("N", n_ok), ("P", p_ok), ("K", k_ok)] if int(ok) == 0]
    if faltantes:
        acao_nutrientes = "Repor nutrientes em atencao: " + ", ".join(faltantes)
    else:
        acao_nutrientes = "Manter plano atual de fertilizacao"

    if rendimento_estimado < 3.2:
        risco_produtivo = "Alto"
    elif rendimento_estimado < 4.2:
        risco_produtivo = "Moderado"
    else:
        risco_produtivo = "Baixo"

    justificativa = (
        f"Decisao baseada em umidade de {umidade:.1f}%, pH {ph:.2f}, "
        f"chuva prevista de {chuva_probabilidade:.0f}% e rendimento estimado "
        f"de {rendimento_estimado:.2f} t/ha."
    )
    return Recomendacao(
        acao_irrigacao=acao_irrigacao,
        acao_ph=acao_ph,
        acao_nutrientes=acao_nutrientes,
        risco_produtivo=risco_produtivo,
        justificativa=justificativa,
    )
