"""Descarrega da API pública os dados de LEI e das respetivas UCs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import requests


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data" / "curso_260"
COURSE_CODE = 260
SCHOOL_YEAR = "202526"
LANGUAGES = ("PT", "ENG")
TIMEOUT = 120

COURSE_URL = (
    "https://secure.ensinolusofona.pt/dados-publicos-academicos/"
    "resources/GetCourseDetail"
)
UC_URL = (
    "https://secure.ensinolusofona.pt/dados-publicos-academicos/"
    "resources/GetSIGESCurricularUnitDetails"
)


def request_json(
    session: requests.Session,
    url: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    response = session.post(url, json=payload, timeout=TIMEOUT)
    response.raise_for_status()
    data = response.json()

    if not isinstance(data, dict):
        raise ValueError(f"A API devolveu um formato inesperado para {url}.")
    if str(data.get("errorCode")) != "0":
        raise ValueError(
            f"A API devolveu o erro {data.get('errorCode')!r} para {payload!r}."
        )
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def download_language(session: requests.Session, language: str) -> int:
    course = request_json(
        session,
        COURSE_URL,
        {
            "language": language,
            "courseCode": COURSE_CODE,
            "schoolYear": SCHOOL_YEAR,
        },
    )

    plan = course.get("courseFlatPlan")
    if not isinstance(plan, list) or not plan:
        raise ValueError(f"O plano curricular {language} está vazio ou é inválido.")

    language_dir = DATA_ROOT / language
    write_json(language_dir / "curso.json", course)

    for unit in plan:
        readable_code = unit.get("curricularIUnitReadableCode")
        if not isinstance(readable_code, str) or not readable_code:
            raise ValueError("Foi encontrada uma UC sem código legível.")

        detail = request_json(
            session,
            UC_URL,
            {
                "language": language,
                "curricularIUnitReadableCode": readable_code,
            },
        )
        write_json(language_dir / "ucs" / f"{readable_code}.json", detail)

    return len(plan)


def main() -> None:
    session = requests.Session()
    session.headers.update(
        {
            "content-type": "application/json",
            "User-Agent": "PortfolioAcademico/1.0 (consulta de dados publicos)",
        }
    )

    for language in LANGUAGES:
        total = download_language(session, language)
        print(f"{language}: curso e {total} UCs guardados em {DATA_ROOT / language}")


if __name__ == "__main__":
    main()
