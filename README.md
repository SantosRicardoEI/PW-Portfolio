# Portfólio Académico — Ficha 6

**Aluno:** Ricardo Santos  
**Número:** 22409527  
**Curso:** Licenciatura em Engenharia Informática (LEI) — Universidade Lusófona

---

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## Executar

A base de dados (`db.sqlite3`) já está incluída com todos os dados carregados.

```bash
python manage.py runserver
```

Aceder ao painel de administração em [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

| Campo      | Valor   |
| ---------- | ------- |
| Utilizador | `admin` |
| Password   | `admin` |

---

## Scripts (opcional)

Para recriar a base de dados de raiz, executar por ordem:

```bash
python scripts/1_scrape_tfcs.py            # extrai TFCs do site do DEISI
python scripts/2_descarregar_curso_ucs.py  # descarrega dados de LEI da API da Lusófona
python scripts/3_carregar_tfcs.py          # carrega TFCs na base de dados
python scripts/4_carregar_curso_ucs.py     # carrega curso e UCs na base de dados
```
