"""Teste do turno por letra (rodar: python test_turnos.py)."""
import pandas as pd

from turnos import TURNO_SEM, DATA_DESDE_SEMPRE, atribuir_turno, normalizar_turno

hist = pd.DataFrame({
    "username": ["30018110", "30018110", " 77 "],
    "turno": ["Turno B", "Turno C", "Administrativo"],
    "vigente_desde": [DATA_DESDE_SEMPRE, pd.Timestamp("2026-11-10").date(), DATA_DESDE_SEMPRE],
})
executor = pd.Series(["30018110", "30018110", "30018110", "30018110", "99999", "", "77", "30018110"],
                     index=[10, 11, 12, 13, 14, 15, 16, 17])  # índice não sequencial
dt = pd.Series(["2026-11-09 23:50", "2026-11-10 00:10", "2020-03-01 08:00", None,
                "2026-11-11 10:00", "2026-11-11 10:00", "2026-11-11 10:00", "2026-11-12 07:00"],
               index=executor.index)

r = atribuir_turno(executor, dt, hist)
assert list(r.index) == list(executor.index)
assert r[10] == "Turno B"           # véspera da troca -> letra antiga
assert r[11] == "Turno C"           # dia da troca -> letra nova
assert r[12] == "Turno B"           # baixa antiga -> 1ª letra (desde sempre)
assert pd.isna(r[13])               # não concluída
assert r[14] == TURNO_SEM           # matrícula sem histórico
assert r[15] == TURNO_SEM           # executor vazio
assert r[16] == "Administrativo"    # espaço/caixa diferentes casam
assert r[17] == "Turno C"

vazio = atribuir_turno(executor, dt, pd.DataFrame(columns=["username", "turno", "vigente_desde"]))
assert vazio[10] == TURNO_SEM and pd.isna(vazio[13])

assert normalizar_turno("a") == "Turno A"
assert normalizar_turno("Turno B") == "Turno B"
assert normalizar_turno(" adm ") == "Administrativo"
assert normalizar_turno("") == "" and normalizar_turno(None) == "" and normalizar_turno(float("nan")) == ""
assert normalizar_turno("X") is None and normalizar_turno("Turno E") is None

print("test_turnos: OK (pandas", pd.__version__ + ")")
