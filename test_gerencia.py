"""Teste da classificação configurável do gerencia.py (rodar: python test_gerencia.py)."""
import re
import types

import gerencia as G


def carregar(coordenacoes_py: str) -> types.ModuleType:
    """Cópia do gerencia.py com outra lista COORDENACOES (o arquivo real não é tocado)."""
    fonte = open(G.__file__, encoding="utf-8").read()
    fonte = re.sub(r"\nCOORDENACOES = \[.*?\n\]\n", "\nCOORDENACOES = " + coordenacoes_py + "\n", fonte, count=1, flags=re.S)
    mod = types.ModuleType("gerencia_teste")
    exec(compile(fonte, "gerencia_teste", "exec"), mod.__dict__)
    return mod


# 1) Placeholders (sem prefixo SAP): nada é classificado -- falha fechado.
for txt in ["", "x", "E.SP.IPA", G.NOMES[0], G.NOMES[0] + " - 123", G.COORDENACOES[0]["sigla"]]:
    assert G.coord_por_departamento(txt) is None, txt
assert G.MAPA_CENTRO_SAP == {}
assert G.normalizar_coord(G.NOMES[0].upper()) == G.NOMES[0]
assert G.sedes("Todas") == G.SEDES and len(G.base_padrao("Todas")) == 3

# 2) Três coordenações, prefixos sobrepostos, uma ainda sem prefixo.
M = carregar("""[
    {"nome": "Alfa", "sigla": "AAA", "prefixos_depto": ["E.RJ.AB"], "centro_trabalho": "E.RJ.AB", "centro": "CAB",
     "sede": "Sede AAA", "sede_coord": [-22.0, -44.0], "aliases": []},
    {"nome": "Beta", "sigla": "BBB", "prefixos_depto": ["E.RJ.ABC"], "centro_trabalho": "E.RJ.ABC", "centro": "CABC",
     "sede": "Sede BBB", "sede_coord": [-22.1, -44.1], "aliases": []},
    {"nome": "Gama", "sigla": "GGG", "prefixos_depto": [], "centro_trabalho": None, "centro": None,
     "sede": "Sede GGG", "sede_coord": [-22.2, -44.2], "aliases": []},
]""")
assert M.coord_por_departamento("E.RJ.ABC123") == "Beta"       # mais longo vence
assert M.coord_por_departamento(" e.rj.ab 9 ") == "Alfa"        # caixa/espaço
assert M.coord_por_departamento("XE.RJ.AB") is None             # só início, nunca substring
assert M.coord_por_departamento("ALFA - centro") == "Alfa"      # nome vale: Alfa tem prefixo
assert M.coord_por_departamento("Gama - centro") is None        # nome NÃO vale: Gama sem prefixo
assert set(M.MAPA_CENTRO_SAP) == {"Alfa", "Beta"}               # Gama fica fora da exportação SAP
assert M.ESCOPOS == ["Alfa", "Beta", "Gama", "Todas"]
assert M.sedes("Beta") == ["Sede BBB"] and M.base_padrao("GGG")[2] == "Sede GGG"

print("test_gerencia: OK")
