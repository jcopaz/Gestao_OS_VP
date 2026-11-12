"""Dados da gerência desta instância do SGO (Vale do Paraíba).

ÚNICO lugar com nomes de coordenação, prefixos/centros SAP, sedes, pátios e limites do
mapa. app.py e api.py importam daqui -- não reintroduzir valores fixos no código.
Python puro (sem streamlit/pandas) porque o api.py (Render) também importa.

PLACEHOLDERS até o Vale devolver o kit (SGO_VP_Kit_de_Dados.xlsx). Com os placeholders o
app sobe, mas tudo "falha fechado": upload de OS descarta linhas (prefixo vazio), exportação
SAP sai vazia com aviso, roteirização fica sem pátios. NÃO cadastrar usuários/OS reais com
os nomes provisórios: o nome da coordenação é gravado no banco.
"""
import unicodedata

NOME_GERENCIA = "Vale do Paraíba"

# Sem default de propósito: a URL vem do secret OFFLINE_API_URL (Streamlit).
API_URL_PADRAO = ""

# Caixa onde pontos de GPS são aceitos/recortados no mapa (antes fixo em max_lon=-44.00,
# que cortava o Vale). Cobre SP, RJ e MG da malha MRS.
LIMITES_MAPA = {"min_lat": -25.50, "max_lat": -19.50, "min_lon": -53.50, "max_lon": -43.00}

# A ordem aqui é a ordem em todas as telas, gráficos e relatórios.
COORDENACOES = [
    {
        "nome": "Coordenação 1", "sigla": "VP1",
        "prefixos_depto": [],          # ex.: ["E.SP.XXX"] -- início do "Codigo departamento" das OS
        "centro_trabalho": None,       # ex.: "E.SP.XXX" -- None = fora da exportação SAP (com aviso)
        "centro": None,                # ex.: "CXXX"
        "sede": "Sede VP1", "sede_coord": [-23.18, -45.88],   # PLACEHOLDER
        "aliases": [],                 # outros textos que devem virar esta coordenação
    },
    {
        "nome": "Coordenação 2", "sigla": "VP2",
        "prefixos_depto": [], "centro_trabalho": None, "centro": None,
        "sede": "Sede VP2", "sede_coord": [-22.90, -45.20],   # PLACEHOLDER
        "aliases": [],
    },
    {
        "nome": "Coordenação 3", "sigla": "VP3",
        "prefixos_depto": [], "centro_trabalho": None, "centro": None,
        "sede": "Sede VP3", "sede_coord": [-22.52, -44.10],   # PLACEHOLDER
        "aliases": [],
    },
]

# Pátios: código de 3 letras (como aparece no nome do ativo) -> [lat, lon].
PATIOS: dict[str, list[float]] = {}


def _chave(txt) -> str:
    """Maiúsculas, sem acento, espaços colapsados."""
    t = unicodedata.normalize("NFKD", " ".join(str(txt or "").split()).upper())
    return "".join(ch for ch in t if not unicodedata.combining(ch))


# --- derivados (não editar) -------------------------------------------------
NOMES = [c["nome"] for c in COORDENACOES]
ESCOPOS = NOMES + ["Todas"]
COORD_PADRAO = NOMES[0]
SEDES = [c["sede"] for c in COORDENACOES]
COORDENADAS_FIXAS = {**PATIOS, **{c["sede"]: c["sede_coord"] for c in COORDENACOES}}
MAPA_CENTRO_SAP = {
    c["nome"]: {"centro_trabalho": c["centro_trabalho"], "centro": c["centro"]}
    for c in COORDENACOES if c["centro_trabalho"] and c["centro"]
}

MAPA_NORM_COORD: dict[str, str] = {}
for _c in COORDENACOES:
    for _apelido in [_c["nome"], _c["sigla"], _c["sede"], *_c["prefixos_depto"], _c["centro_trabalho"], *_c["aliases"]]:
        if _apelido:
            MAPA_NORM_COORD[str(_apelido).strip().upper()] = _c["nome"]
            MAPA_NORM_COORD[_chave(_apelido)] = _c["nome"]

# (prefixo normalizado, nome) do mais longo para o mais curto -- startswith, nunca substring.
# O nome da coordenação só vale como prefixo quando ela já tem prefixo SAP configurado
# (a IW47 antiga aceitava "PARANAPIACABA..."); placeholder sem prefixo falha fechado.
_PREFIXOS = sorted(
    {(_chave(p), c["nome"]) for c in COORDENACOES
     for p in [*c["prefixos_depto"], c["centro_trabalho"], c["nome"] if c["prefixos_depto"] else None] if p},
    key=lambda x: len(x[0]), reverse=True,
)


def normalizar_coord(txt) -> str:
    """Nome oficial da coordenação para um texto/apelido; se não reconhecer, o texto com strip."""
    s = str(txt or "").strip()
    return MAPA_NORM_COORD.get(s.upper()) or MAPA_NORM_COORD.get(_chave(s)) or s


def coord_por_departamento(cod):
    """Coordenação pelo início do Código Departamento / Centro de Trabalho; None se nenhuma."""
    k = _chave(cod)
    if not k:
        return None
    for prefixo, nome in _PREFIXOS:
        if k.startswith(prefixo):
            return nome
    return None


def sedes(escopo) -> list[str]:
    """Sedes válidas para um escopo ("Todas"/desconhecido = todas)."""
    for c in COORDENACOES:
        if c["nome"] == escopo:
            return [c["sede"]]
    return list(SEDES)


def base_padrao(valor):
    """(lat, lon, nome_exibicao) da base do usuário: aceita nome, sigla, 'Sede X' ou pátio.
    'Todas'/desconhecido cai na sede da primeira coordenação."""
    k = _chave(valor)
    for c in COORDENACOES:
        if k in (_chave(c["nome"]), _chave(c["sigla"]), _chave(c["sede"])):
            return c["sede_coord"][0], c["sede_coord"][1], c["sede"]
    if k in PATIOS:
        return PATIOS[k][0], PATIOS[k][1], k
    c0 = COORDENACOES[0]
    return c0["sede_coord"][0], c0["sede_coord"][1], f"{c0['sede']} (padrão)"


# --- sanidade no import -----------------------------------------------------
assert COORDENACOES, "gerencia.py: cadastre ao menos uma coordenação"
assert len(set(NOMES)) == len(NOMES), "gerencia.py: nomes de coordenação repetidos"
assert len({c["sigla"] for c in COORDENACOES}) == len(COORDENACOES), "gerencia.py: siglas repetidas"
assert "Todas" not in NOMES, "gerencia.py: 'Todas' é reservado"
for _c in COORDENACOES:
    assert len(_c["sede_coord"]) == 2 and all(isinstance(v, float) for v in _c["sede_coord"]), \
        f"gerencia.py: sede_coord inválida em {_c['nome']}"
for _p in PATIOS:
    assert not _p.startswith("Sede") and _p == _p.upper(), f"gerencia.py: chave de pátio inválida: {_p}"
