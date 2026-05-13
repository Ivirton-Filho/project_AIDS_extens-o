#!/usr/bin/env python3
"""
Baixa tabelas do TabNet AIDS Brasil para Mato Grosso (UF Residência),
com linha Município (Res) e colunas selecionadas, em formato texto pré-formatado/CSV.

Fonte: https://www2.aids.gov.br/cgi/deftohtm.exe?tabnet/br.def
Saída: pasta "extensão - dados/MT" organizada por ano.
"""

from __future__ import annotations

import csv
import html
import re
import sys
import time
import unicodedata
from pathlib import Path
from typing import Dict, Iterable, Tuple
from urllib.parse import urljoin

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_DIR = Path(__file__).resolve().parent
ROOT_OUTPUT_DIR = BASE_DIR / "extensão - dados"
STATE = "MT"
STATE_NAME = "Mato Grosso"
STATE_OUTPUT_DIR = ROOT_OUTPUT_DIR / STATE
LOG_FILE = STATE_OUTPUT_DIR / "download_log.csv"
TABNET_URL = "https://www2.aids.gov.br/cgi/tabcgi.exe?tabnet/br.def"
CSV_BASE_URL = "http://www2.aids.gov.br/cgi-bin"

# No formulário br.def, Mato Grosso aparece como VALUE="26" em SUF_Residência.
UF_RESIDENCIA_CODE = "26"

# Arquivos anuais do banco de AIDS: aids_15.dbf ... aids_25.dbf.
YEARS: Dict[str, str] = {
    "15": "2015",
    "16": "2016",
    "17": "2017",
    "18": "2018",
    "19": "2019",
    "20": "2020",
    "21": "2021",
    "22": "2022",
    "23": "2023",
    "24": "2024",
    "25": "2025",
}

# Valor enviado no campo Coluna -> rótulo limpo para nome de arquivo.
COLUMNS: Dict[str, str] = {
    "Ano_Diagnóstico": "Ano_Diagnostico",
    "Fx._Etária(13)": "Fx_Etaria_13",
    "Sexo": "Sexo",
    "Raça/cor": "Raca_cor",
    "Escolaridade": "Escolaridade",
}


def to_latin1_bytes(value: str) -> bytes:
    """Codifica texto em ISO-8859-1, codificação esperada pelo CGI antigo."""
    return value.encode("latin-1")


def safe_ascii_name(value: str) -> str:
    """Normaliza nomes para uso seguro em arquivos e pastas."""
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_text = re.sub(r"[^A-Za-z0-9._-]+", "_", ascii_text)
    return ascii_text.strip("_")


def build_payload(year_code: str, column_value: str) -> Dict[object, object]:
    """Monta o payload do formulário TabNet."""
    return {
        "Linha": to_latin1_bytes("Município_(Res)"),
        "Coluna": to_latin1_bytes(column_value),
        "Incremento": to_latin1_bytes("Freqüência"),
        "Arquivos": to_latin1_bytes(f"aids_{year_code}.dbf"),
        # Chave em bytes para preservar o acento exatamente como o CGI espera.
        b"SUF_Resid\xeancia": to_latin1_bytes(UF_RESIDENCIA_CODE),
        "formato": to_latin1_bytes("pre"),
        "mostre": to_latin1_bytes("Mostra"),
    }


def extract_csv_url(response_text: str) -> str | None:
    """Extrai a URL do CSV gerado pelo TabNet a partir do HTML de resposta."""
    decoded = html.unescape(response_text)
    patterns = [
        r'href=["\']?([^"\' >]+\.csv)',
        r'HREF=["\']?([^"\' >]+\.CSV)',
    ]
    for pattern in patterns:
        match = re.search(pattern, decoded, flags=re.IGNORECASE)
        if match:
            path = match.group(1)
            if path.startswith("http://") or path.startswith("https://"):
                return path
            return urljoin(CSV_BASE_URL + "/", path.lstrip("/"))
    return None


def looks_like_valid_csv(content: bytes) -> bool:
    """Faz validação simples para evitar salvar páginas de erro como CSV."""
    if not content or len(content) < 20:
        return False
    sample = content[:2000].decode("latin-1", errors="ignore").lower()
    if "<html" in sample or ("tabnet" in sample and "erro" in sample):
        return False
    return ";" in sample or "município" in sample or "municipio" in sample


def download_column(
    session: requests.Session,
    year_code: str,
    year_label: str,
    column_value: str,
    column_label: str,
    overwrite: bool = False,
) -> Tuple[bool, str]:
    """Baixa uma tabela e retorna status/mensagem."""
    year_dir = STATE_OUTPUT_DIR / f"{STATE}_{year_label}"
    year_dir.mkdir(parents=True, exist_ok=True)
    filename = year_dir / f"{STATE}_{year_label}_{safe_ascii_name(column_label)}.csv"

    if filename.exists() and filename.stat().st_size > 0 and not overwrite:
        return True, f"Já existia: {filename}"

    payload = build_payload(year_code, column_value)
    response = session.post(TABNET_URL, data=payload, timeout=60, verify=False)
    response.raise_for_status()

    csv_url = extract_csv_url(response.text)
    if not csv_url:
        debug_file = year_dir / f"DEBUG_{STATE}_{year_label}_{safe_ascii_name(column_label)}.html"
        debug_file.write_text(response.text, encoding="latin-1", errors="ignore")
        return False, f"CSV não encontrado; HTML salvo em {debug_file}"

    csv_response = session.get(csv_url, timeout=60, verify=False)
    csv_response.raise_for_status()

    if not looks_like_valid_csv(csv_response.content):
        debug_file = year_dir / f"DEBUG_{STATE}_{year_label}_{safe_ascii_name(column_label)}_csv_response.bin"
        debug_file.write_bytes(csv_response.content)
        return False, f"Resposta CSV inválida; conteúdo salvo em {debug_file}"

    filename.write_bytes(csv_response.content)
    return True, f"Baixado: {filename}"


def iter_jobs() -> Iterable[Tuple[str, str, str, str]]:
    for year_code, year_label in YEARS.items():
        for column_value, column_label in COLUMNS.items():
            yield year_code, year_label, column_value, column_label


def main() -> int:
    overwrite = "--overwrite" in sys.argv
    STATE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Referer": "https://www2.aids.gov.br/cgi/deftohtm.exe?tabnet/br.def",
    })

    rows = []
    total = len(YEARS) * len(COLUMNS)
    ok_count = 0

    for idx, (year_code, year_label, column_value, column_label) in enumerate(iter_jobs(), start=1):
        print(f"[{idx:02d}/{total}] {STATE} {year_label} | Coluna: {column_value}")
        try:
            ok, message = download_column(session, year_code, year_label, column_value, column_label, overwrite=overwrite)
        except Exception as exc:
            ok, message = False, f"Erro: {exc}"
        print("   ", message)
        rows.append({
            "ano": year_label,
            "arquivo_dbf": f"aids_{year_code}.dbf",
            "linha": "Município_(Res)",
            "coluna": column_value,
            "uf_residencia": STATE,
            "uf_residencia_nome": STATE_NAME,
            "uf_residencia_codigo_tabnet": UF_RESIDENCIA_CODE,
            "status": "ok" if ok else "falha",
            "mensagem": message,
        })
        ok_count += int(ok)
        time.sleep(0.8)

    with LOG_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nConcluído: {ok_count}/{total} downloads com status OK.")
    print(f"Pasta de saída: {STATE_OUTPUT_DIR}")
    print(f"Log: {LOG_FILE}")
    return 0 if ok_count == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
