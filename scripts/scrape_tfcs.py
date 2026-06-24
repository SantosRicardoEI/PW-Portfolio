"""Extrai os TFCs de 2025 e 2026 publicados no site do DEISI."""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup, Tag


SOURCE_URL = (
    "https://informatica.ulusofona.pt/"
    "investigacao/tfcs-dissertacoes-teses/"
)
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "tfcs.json"
YEARS = {2025, 2026}

# O site repete estes três trabalhos. Mantém-se a primeira publicação, tal como
# aparece na página, e ignoram-se as cópias identificadas pelo relatório.
DUPLICATE_REPORT_URLS = {
    "https://teses.deisi.ulusofona.pt/media/teses/"
    "TFC_segunda_entrega_a22204317_1.zip",
    "https://teses.deisi.ulusofona.pt/media/teses/1325.pdf",
    "https://teses.deisi.ulusofona.pt/media/teses/DEISI2037_taZ6YdA.pdf",
}


def clean_text(value: str) -> str:
    """Normaliza espaços sem alterar a grafia publicada."""

    return re.sub(r"\s+", " ", value.replace("\xa0", " ")).strip()


def unique_values(values: list[str]) -> list[str]:
    """Remove repetições, preservando a primeira grafia e a ordem."""

    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = clean_text(value).strip(" ;")
        key = normalized.casefold()
        if normalized and key not in seen:
            result.append(normalized)
            seen.add(key)
    return result


def split_list(value: str) -> list[str]:
    """Separa listas editoriais, cujo delimitador no site é o ponto e vírgula."""

    return unique_values(value.split(";"))


def split_students(value: str) -> list[str]:
    """Separa alunos apenas quando o formato publicado não é ambíguo."""

    value = clean_text(value)
    if ";" in value:
        return unique_values(value.split(";"))

    if re.fullmatch(r"A?\d{8}\s*/\s*A?\d{8}", value, flags=re.IGNORECASE):
        return unique_values(value.split("/"))

    comma_parts = [clean_text(part) for part in value.split(",")]
    if len(comma_parts) == 2 and not re.fullmatch(r"A?\d{8}", comma_parts[1]):
        return unique_values(comma_parts)

    return [value] if value else []


def split_courses(value: str) -> tuple[list[str], int | None]:
    """Retira o ano final e separa TFCs associados a várias licenciaturas."""

    value = clean_text(value)
    year_match = re.search(r"(20\d{2})\s*$", value)
    if not year_match:
        return [], None

    year = int(year_match.group(1))
    courses_text = value[: year_match.start()].rstrip(". ")
    courses = re.split(r"\.\s*(?=Licenciatura\b)", courses_text)
    return unique_values(courses), year


def text_after_label(content: Tag, label: str) -> str:
    """Obtém o texto do parágrafo que começa por uma etiqueta em negrito."""

    wanted = label.casefold().rstrip(":")
    for span in content.find_all("span"):
        span_label = clean_text(span.get_text(" ", strip=True)).casefold().rstrip(":")
        if span_label == wanted:
            paragraph = span.find_parent("p")
            if paragraph is None:
                return ""
            full_text = clean_text(paragraph.get_text(" ", strip=True))
            prefix = clean_text(span.get_text(" ", strip=True))
            return clean_text(full_text.removeprefix(prefix))
    return ""


def absolute_url(value: str | None) -> str | None:
    if not value:
        return None
    return urljoin(SOURCE_URL, value)


def find_tfc_cards(soup: BeautifulSoup, heading: str) -> list[Tag]:
    section_heading = soup.find(
        "h2", string=lambda text: bool(text and clean_text(text) == heading)
    )
    if section_heading is None:
        raise ValueError(f"Secção não encontrada: {heading}")

    group_title = section_heading.find_next(
        "span",
        string=lambda text: bool(text and "Trabalhos Finais de Curso" in text),
    )
    if group_title is None:
        raise ValueError(f"Grupo de TFCs não encontrado em: {heading}")

    group = group_title.find_parent("li")
    cards_list = group.find("ul", attrs={"uk-accordion": True}) if group else None
    if cards_list is None:
        raise ValueError(f"Lista de TFCs não encontrada em: {heading}")

    return [card for card in cards_list.find_all("li", recursive=False)]


def parse_card(card: Tag, state: str) -> dict[str, object] | None:
    header = card.find("a", class_="uk-accordion-title", recursive=False)
    content = card.find("div", class_="uk-accordion-content", recursive=False)
    if header is None or content is None:
        raise ValueError("Foi encontrado um cartão de TFC com estrutura desconhecida.")

    title_span = header.find(
        "span", style=lambda value: bool(value and "display: block" in value)
    )
    italic_span = header.find(
        "span", style=lambda value: bool(value and "font-style:italic" in value)
    )
    if title_span is None or italic_span is None:
        raise ValueError("O cartão não contém título ou curso/ano.")

    title = clean_text(title_span.get_text(" ", strip=True))
    courses, year = split_courses(italic_span.get_text(" ", strip=True))
    if year not in YEARS or not courses or not all(
        course.startswith("Licenciatura") for course in courses
    ):
        return None

    meta = title_span.find_next_sibling("span")
    bold_spans = (
        meta.find_all(
            "span", style=lambda value: bool(value and "font-weight:bold" in value)
        )
        if meta
        else []
    )
    if len(bold_spans) < 2:
        raise ValueError(f"Não foi possível identificar alunos/orientadores em: {title}")

    students = split_students(bold_spans[0].get_text(" ", strip=True))
    supervisors = unique_values(
        bold_spans[1].get_text(" ", strip=True).split(",")
    )

    partner_tag = meta.find("b") if meta else None
    partnership = (
        clean_text(partner_tag.get_text(" ", strip=True)) if partner_tag else None
    )

    report_tag = content.find("a", attrs={"download": True})
    email_tag = content.find("a", href=lambda value: bool(value and value.startswith("mailto:")))
    image_tag = content.find("img")
    video_tag = content.find("iframe")

    report_url = absolute_url(report_tag.get("href") if report_tag else None)
    if report_url in DUPLICATE_REPORT_URLS:
        return None

    if title == "Venom Autonomous Pentest Tool":
        supervisors = ["Daniel Silveira"]

    email = None
    if email_tag:
        email = clean_text(email_tag.get("href", "").removeprefix("mailto:"))

    summary = text_after_label(content, "Resumo")
    keywords = split_list(text_after_label(content, "Palavras chave"))
    areas = split_list(text_after_label(content, "Áreas"))
    technologies = split_list(text_after_label(content, "Tecnologias usadas"))

    result: dict[str, object] = {
        "tipo": "TFC",
        "estado": state,
        "titulo": title,
        "alunos": students,
        "orientadores": supervisors,
        "parceria": partnership,
        "cursos": courses,
        "ano": year,
        "email": email,
        "relatorio_url": report_url,
        "imagem_url": absolute_url(
            image_tag.get("src") or image_tag.get("data-src") if image_tag else None
        ),
        "video_url": absolute_url(video_tag.get("src") if video_tag else None),
        "resumo": summary,
        "palavras_chave": keywords,
        "areas": areas,
        "tecnologias": technologies,
    }

    required = (
        "titulo",
        "alunos",
        "orientadores",
        "cursos",
        "ano",
        "email",
        "imagem_url",
        "resumo",
        "palavras_chave",
        "areas",
        "tecnologias",
    )
    missing = [field for field in required if not result[field]]
    if missing:
        raise ValueError(f"Campos obrigatórios ausentes em {title}: {', '.join(missing)}")

    return result


def download_page() -> str:
    request = Request(
        SOURCE_URL,
        headers={
            "User-Agent": "PortfolioAcademico/1.0 (extracao de dados publicos para estudo)"
        },
    )
    with urlopen(request, timeout=120) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset)


def scrape_tfcs(html: str) -> list[dict[str, object]]:
    soup = BeautifulSoup(html, "html.parser")
    tfcs: list[dict[str, object]] = []

    sections = (
        ("Trabalhos em Curso", "em_curso"),
        ("Trabalhos Concluídos", "concluido"),
    )
    for heading, state in sections:
        for card in find_tfc_cards(soup, heading):
            tfc = parse_card(card, state)
            if tfc is not None:
                tfcs.append(tfc)

    return tfcs


def main() -> None:
    tfcs = scrape_tfcs(download_page())
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(tfcs, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    by_year = {year: sum(tfc["ano"] == year for tfc in tfcs) for year in YEARS}
    print(f"Guardados {len(tfcs)} TFCs em {OUTPUT_PATH}")
    print(f"2025: {by_year[2025]} | 2026: {by_year[2026]}")


if __name__ == "__main__":
    main()
