"""Turno por LETRA da escala (A/B/C/D/Administrativo) -- constantes e lookup puro.

O turno de uma OS concluída é a letra que o EXECUTOR PRINCIPAL ("Concluído por",
matrícula) tinha NA DATA da baixa, segundo a tabela turno_historico (vigente_desde).
Sem streamlit/banco aqui para poder testar com `python test_turnos.py`.
"""
from datetime import date

import pandas as pd

TURNOS = ["Turno A", "Turno B", "Turno C", "Turno D", "Administrativo"]
TURNO_SEM = "Sem turno"                    # concluída, executor sem letra cadastrada
TURNO_PENDENTE = "Pendente (Sem Turno)"    # OS ainda não concluída (filtro da sidebar)
TURNOS_EIXO = TURNOS + [TURNO_SEM]         # eixo dos gráficos
COR_TURNO = {
    "Turno A": "#F59E0B", "Turno B": "#4F46E5", "Turno C": "#10B981", "Turno D": "#EC4899",
    "Administrativo": "#3B82F6", "Sem turno": "#94A3B8",
}
TURNO_CURTO = {"Turno A": "A", "Turno B": "B", "Turno C": "C", "Turno D": "D",
               "Administrativo": "Adm", "Sem turno": "S/T"}
# 1º registro de cada matrícula vale "desde sempre" (OS antigas contam para a letra atual).
DATA_DESDE_SEMPRE = date(2000, 1, 1)


def normalizar_turno(valor):
    """'A'/'turno a' -> 'Turno A'; 'adm...' -> 'Administrativo'; vazio -> ''; inválido -> None."""
    s = " ".join(str(valor if valor is not None else "").split()).upper()
    if s in ("", "NAN", "NONE"):
        return ""
    if s.startswith("ADM"):
        return "Administrativo"
    if s.startswith("TURNO "):
        s = s[6:]
    return f"Turno {s}" if s in ("A", "B", "C", "D") else None


def atribuir_turno(executor, dt_realizado, df_hist) -> pd.Series:
    """Letra vigente do executor na data de cada baixa.

    NaT -> None (OS não concluída); executor sem histórico -> TURNO_SEM.
    df_hist: colunas username, turno, vigente_desde.
    """
    executor = pd.Series(executor)
    idx = executor.index
    executor = executor.reset_index(drop=True)
    dt = pd.to_datetime(pd.Series(dt_realizado).reset_index(drop=True), errors="coerce")
    res = pd.Series([TURNO_SEM if pd.notna(d) else None for d in dt], dtype=object)
    if df_hist is None or len(df_hist) == 0 or not dt.notna().any():
        res.index = idx
        return res

    esq = pd.DataFrame({
        "pos": range(len(dt)),
        "username": executor.fillna("").astype(str).str.strip().str.upper(),
        "data": dt.dt.normalize().astype("datetime64[ns]"),
    }).dropna(subset=["data"]).sort_values("data")
    dir_ = pd.DataFrame({
        "username": df_hist["username"].fillna("").astype(str).str.strip().str.upper(),
        "data": pd.to_datetime(df_hist["vigente_desde"], errors="coerce").astype("datetime64[ns]"),
        "turno": df_hist["turno"].astype(str),
    }).dropna(subset=["data"]).sort_values("data")

    m = pd.merge_asof(esq, dir_, on="data", by="username", direction="backward")
    res.iloc[m["pos"].to_numpy()] = m["turno"].fillna(TURNO_SEM).to_numpy()
    res.index = idx
    return res
