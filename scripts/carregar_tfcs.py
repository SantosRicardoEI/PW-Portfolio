"""Carrega data/tfcs.json na base de dados através do ORM Django."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "tfcs.json"

sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

import django  # noqa: E402

django.setup()

from django.db import transaction  # noqa: E402

from portfolio.models import (  # noqa: E402
    Aluno,
    AreaTFC,
    Docente,
    Licenciatura,
    PalavraChaveTFC,
    Tecnologia,
    TFC,
)


COURSES = {
    "Licenciatura em Engenharia Informática": {
        "sigla": "LEI",
        "codigo": "260",
    },
    "Licenciatura em Informática de Gestão": {
        "sigla": "LIG",
        "codigo": "12",
    },
    "Licenciatura em Ciência de Dados": {
        "sigla": "LCID",
        "codigo": "6634",
    },
    "Licenciatura em Computação e Matemática Aplicada": {
        "sigla": "LICMA",
        "codigo": "6638",
    },
}

REQUIRED_FIELDS = {
    "tipo",
    "estado",
    "titulo",
    "alunos",
    "orientadores",
    "parceria",
    "cursos",
    "ano",
    "email",
    "relatorio_url",
    "imagem_url",
    "video_url",
    "resumo",
    "palavras_chave",
    "areas",
    "tecnologias",
}

LIST_FIELDS = (
    "alunos",
    "orientadores",
    "cursos",
    "palavras_chave",
    "areas",
    "tecnologias",
)

STRING_FIELDS = ("titulo", "email", "imagem_url", "resumo")
OPTIONAL_STRING_FIELDS = ("parceria", "relatorio_url", "video_url")


def load_json() -> list[dict[str, Any]]:
    try:
        data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"Ficheiro não encontrado: {DATA_PATH}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"JSON inválido: {error}") from error

    if not isinstance(data, list):
        raise ValueError("A raiz do JSON deve ser uma lista de TFCs.")

    for index, item in enumerate(data, start=1):
        validate_item(item, index)

    return data


def validate_item(item: Any, index: int) -> None:
    label = f"Registo {index}"
    if not isinstance(item, dict):
        raise ValueError(f"{label}: deve ser um objeto JSON.")

    missing = REQUIRED_FIELDS - item.keys()
    if missing:
        raise ValueError(f"{label}: faltam os campos {', '.join(sorted(missing))}.")

    if item["tipo"] != "TFC":
        raise ValueError(f"{label}: o campo tipo deve ter o valor 'TFC'.")
    if item["estado"] not in TFC.Estado.values:
        raise ValueError(f"{label}: estado desconhecido: {item['estado']!r}.")
    if type(item["ano"]) is not int or item["ano"] < 2000:
        raise ValueError(f"{label}: ano inválido.")

    for field in STRING_FIELDS:
        if not isinstance(item[field], str) or not item[field].strip():
            raise ValueError(f"{label}: {field} deve ser texto não vazio.")

    for field in OPTIONAL_STRING_FIELDS:
        if item[field] is not None and not isinstance(item[field], str):
            raise ValueError(f"{label}: {field} deve ser texto ou null.")

    for field in LIST_FIELDS:
        values = item[field]
        if not isinstance(values, list) or not values:
            raise ValueError(f"{label}: {field} deve ser uma lista não vazia.")
        if not all(isinstance(value, str) and value.strip() for value in values):
            raise ValueError(f"{label}: {field} contém um valor inválido.")

    unknown_courses = set(item["cursos"]) - COURSES.keys()
    if unknown_courses:
        raise ValueError(
            f"{label}: licenciaturas desconhecidas: {', '.join(sorted(unknown_courses))}."
        )


def get_named_object(model, name: str):
    """Reutiliza designações ignorando apenas diferenças de capitalização."""

    name = name.strip()
    instance = model.objects.filter(nome__iexact=name).first()
    if instance is not None:
        return instance
    return model.objects.create(nome=name)


def parse_student(value: str) -> tuple[str, str | None]:
    value = value.strip()

    match = re.fullmatch(r"(.*?)\s*\(\s*A?(\d+)\s*\)", value, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip(), match.group(2)

    match = re.fullmatch(r"(.*?),\s*A?(\d+)", value, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip(), match.group(2)

    match = re.fullmatch(r"A?(\d+)-(.+)", value, flags=re.IGNORECASE)
    if match:
        return match.group(2).strip(), match.group(1)

    match = re.fullmatch(r"A?(\d+)", value, flags=re.IGNORECASE)
    if match:
        return "", match.group(1)

    return value, None


def get_student(value: str) -> Aluno:
    name, number = parse_student(value)

    if number:
        student = Aluno.objects.filter(numero=number).first()
        if student is None:
            return Aluno.objects.create(nome=name, numero=number)
        if not student.nome and name:
            student.nome = name
            student.save(update_fields=["nome"])
        return student

    student = Aluno.objects.filter(nome__iexact=name, numero__isnull=True).first()
    if student is not None:
        return student
    return Aluno.objects.create(nome=name)


def get_course(name: str) -> Licenciatura:
    details = COURSES[name]
    course = Licenciatura.objects.filter(codigo=details["codigo"]).first()
    if course is not None:
        return course

    course = Licenciatura.objects.filter(nome__iexact=name).first()
    if course is not None:
        return course

    return Licenciatura.objects.create(
        nome=name,
        sigla=details["sigla"],
        codigo=details["codigo"],
    )


def import_tfcs(data: list[dict[str, Any]]) -> tuple[int, int]:
    created_count = 0
    updated_count = 0

    with transaction.atomic():
        for item in data:
            tfc, created = TFC.objects.update_or_create(
                titulo=item["titulo"].strip(),
                ano=item["ano"],
                email=item["email"].strip(),
                defaults={
                    "estado": item["estado"],
                    "resumo": item["resumo"].strip(),
                    "parceria": (item["parceria"] or "").strip(),
                    "relatorio_url": item["relatorio_url"] or "",
                    "imagem_url": item["imagem_url"],
                    "video_url": item["video_url"] or "",
                },
            )
            tfc.full_clean()
            tfc.save()

            tfc.alunos.set(get_student(value) for value in item["alunos"])
            tfc.orientadores.set(
                get_named_object(Docente, value) for value in item["orientadores"]
            )
            tfc.licenciaturas.set(get_course(value) for value in item["cursos"])
            tfc.areas.set(get_named_object(AreaTFC, value) for value in item["areas"])
            tfc.palavras_chave.set(
                get_named_object(PalavraChaveTFC, value)
                for value in item["palavras_chave"]
            )
            tfc.tecnologias.set(
                get_named_object(Tecnologia, value) for value in item["tecnologias"]
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

    return created_count, updated_count


def print_summary(created: int, updated: int) -> None:
    print(f"TFCs criados: {created}")
    print(f"TFCs atualizados: {updated}")
    print(f"Total de TFCs na base de dados: {TFC.objects.count()}")
    print(f"Alunos: {Aluno.objects.count()}")
    print(f"Docentes: {Docente.objects.count()}")
    print(f"Licenciaturas: {Licenciatura.objects.count()}")
    print(f"Áreas: {AreaTFC.objects.count()}")
    print(f"Palavras-chave: {PalavraChaveTFC.objects.count()}")
    print(f"Tecnologias: {Tecnologia.objects.count()}")


def main() -> None:
    data = load_json()
    created, updated = import_tfcs(data)
    print_summary(created, updated)


if __name__ == "__main__":
    main()
