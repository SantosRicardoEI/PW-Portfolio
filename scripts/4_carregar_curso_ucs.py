"""Carrega no Django os dados portugueses de LEI e das respetivas UCs."""

from __future__ import annotations

import json
import os
import re
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data" / "curso_260" / "PT"
COURSE_PATH = DATA_ROOT / "curso.json"
SCHOOL_YEAR = "202526"
COURSE_CODE = "260"

sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

import django  # noqa: E402

django.setup()

from bs4 import BeautifulSoup  # noqa: E402
from django.db import transaction  # noqa: E402

from portfolio.models import (  # noqa: E402
    Docente,
    Licenciatura,
    TFC,
    UnidadeCurricular,
)


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"Ficheiro não encontrado: {path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"JSON inválido em {path}: {error}") from error

    if not isinstance(data, dict) or str(data.get("errorCode")) != "0":
        raise ValueError(f"Resposta inválida da API em {path}.")
    return data


def clean_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""

    value = value.replace("\r\n", "\n").replace("\r", "\n").replace("\xa0", " ")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in value.split("\n")]
    result: list[str] = []
    previous_blank = False
    for line in lines:
        is_blank = not line
        if is_blank and previous_blank:
            continue
        result.append(line)
        previous_blank = is_blank
    return "\n".join(result).strip()


def html_to_text(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        return ""
    soup = BeautifulSoup(value, "html.parser")
    return clean_text(soup.get_text("\n"))


def decimal_or_none(value: Any) -> Decimal | None:
    if value is None or value == "":
        return None
    return Decimal(str(value)).quantize(Decimal("0.1"))


def update_course(detail: dict[str, Any]) -> Licenciatura:
    course = Licenciatura.objects.get(codigo=COURSE_CODE)
    course.nome = clean_text(detail.get("dsGrauCursoLongo")) or course.nome
    course.descricao = clean_text(detail.get("presentation"))
    course.duracao_semestres = detail.get("semesters")
    course.ects = detail.get("courseECTS")
    course.website = clean_text(detail.get("courseUrl"))
    course.objetivos = clean_text(detail.get("objectives"))
    course.competencias = clean_text(detail.get("competences"))
    course.saidas_profissionais = clean_text(detail.get("careerOportunities"))
    course.condicoes_acesso = clean_text(detail.get("accessContidions"))
    course.grau = clean_text(detail.get("degree"))
    course.area_cientifica = clean_text(
        detail.get("areaScientificMkt") or detail.get("scientificArea")
    )
    course.modalidade = clean_text(detail.get("modEstudo"))
    course.acreditacao = clean_text(detail.get("creditationStatus"))
    course.full_clean()
    course.save()
    return course


def get_teacher(data: dict[str, Any]) -> Docente:
    name = clean_text(data.get("academicName") or data.get("fullName"))
    if not name:
        raise ValueError("Foi encontrado um docente sem nome.")

    employee_code = data.get("employeeCode")
    teacher = None
    if isinstance(employee_code, int):
        teacher = Docente.objects.filter(codigo_funcionario=employee_code).first()
    if teacher is None:
        teacher = Docente.objects.filter(nome__iexact=name).first()
    if teacher is None:
        teacher = Docente(nome=name)

    teacher.nome_completo = clean_text(data.get("fullName"))
    teacher.grau = clean_text(data.get("degree"))
    teacher.regime = clean_text(data.get("regimen"))
    teacher.orcid = clean_text(data.get("orcid"))
    teacher.ciencia_vitae = clean_text(data.get("cienciaVitae"))
    if isinstance(employee_code, int):
        teacher.codigo_funcionario = employee_code

    email = clean_text(data.get("email"))
    if email:
        teacher.email = email

    teacher.full_clean()
    teacher.save()
    return teacher


def validate_plan_unit(unit: Any) -> str:
    if not isinstance(unit, dict):
        raise ValueError("O plano curricular contém uma UC inválida.")

    readable_code = unit.get("curricularIUnitReadableCode")
    if not isinstance(readable_code, str) or not readable_code:
        raise ValueError("O plano curricular contém uma UC sem código.")

    if unit.get("semesterCode") not in UnidadeCurricular.Semestre.values:
        raise ValueError(
            f"Semestre desconhecido em {readable_code}: {unit.get('semesterCode')!r}."
        )
    return readable_code


def update_unit(
    course: Licenciatura,
    plan_unit: dict[str, Any],
    detail: dict[str, Any],
) -> tuple[UnidadeCurricular, bool]:
    readable_code = validate_plan_unit(plan_unit)

    if detail.get("curricularIUnitReadableCode") != readable_code:
        raise ValueError(f"O detalhe recebido não corresponde à UC {readable_code}.")

    unit, created = UnidadeCurricular.objects.update_or_create(
        licenciatura=course,
        codigo=readable_code,
        defaults={
            "nome": clean_text(
                detail.get("curricularUnitName") or plan_unit.get("curricularUnitName")
            ),
            "ano": detail.get("curricularYear") or plan_unit.get("curricularYear"),
            "semestre": plan_unit.get("semesterCode"),
            "ects": detail.get("ects") or plan_unit.get("ects"),
            "ano_letivo": SCHOOL_YEAR,
            "apresentacao": clean_text(detail.get("presentation")),
            "objetivos": clean_text(detail.get("objectives")),
            "competencias": clean_text(detail.get("competences")),
            "programa": clean_text(detail.get("programme")),
            "metodologia": clean_text(detail.get("methodology")),
            "avaliacao": html_to_text(detail.get("avaliacao")),
            "bibliografia": clean_text(detail.get("bibliography")),
            "natureza": clean_text(detail.get("nature")),
            "idioma": clean_text(detail.get("language")),
            "horas_contacto": decimal_or_none(plan_unit.get("hrTotalContactoInt")),
        },
    )
    unit.full_clean()
    unit.save()
    return unit, created


def import_data(course_data: dict[str, Any]) -> tuple[int, int]:
    detail = course_data.get("courseDetail")
    plan = course_data.get("courseFlatPlan")
    teachers_data = course_data.get("teachers")
    if not isinstance(detail, dict):
        raise ValueError("O detalhe do curso está ausente ou é inválido.")
    if not isinstance(plan, list) or not plan:
        raise ValueError("O plano curricular está ausente ou vazio.")
    if not isinstance(teachers_data, list):
        raise ValueError("A lista de docentes está ausente ou é inválida.")

    created_count = 0
    updated_count = 0
    with transaction.atomic():
        course = update_course(detail)
        teachers = [get_teacher(item) for item in teachers_data]
        course.docentes.set(teachers)

        for plan_unit in plan:
            readable_code = validate_plan_unit(plan_unit)
            unit_detail = read_json(DATA_ROOT / "ucs" / f"{readable_code}.json")
            _, created = update_unit(course, plan_unit, unit_detail)
            if created:
                created_count += 1
            else:
                updated_count += 1

    return created_count, updated_count


def main() -> None:
    course_data = read_json(COURSE_PATH)
    created, updated = import_data(course_data)
    course = Licenciatura.objects.get(codigo=COURSE_CODE)

    print(f"UCs criadas: {created}")
    print(f"UCs atualizadas: {updated}")
    print(f"UCs de LEI: {course.unidades_curriculares.count()}")
    print(f"Docentes associados a LEI: {course.docentes.count()}")
    print(f"Docentes totais: {Docente.objects.count()}")
    print(f"TFCs preservados: {TFC.objects.count()}")


if __name__ == "__main__":
    main()
