# Portfólio — Ficha 6

Primeira fase do portfólio académico em Django. Nesta entrega existem apenas os
modelos e o painel de administração; não existem páginas públicas.

## Preparar o projeto

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
```

O superutilizador local criado durante o desenvolvimento é `admin`, com a
password `admin`. A base de dados SQLite não é guardada no Git; noutra máquina,
deverá ser criado um novo superutilizador depois das migrações.

## Verificar

```bash
python manage.py check
python manage.py makemigrations --check
```

Para consultar o painel, iniciar o servidor local e abrir `/admin/`:

```bash
python manage.py runserver
```

## Limite desta fase

Não foram implementadas as secções 4 a 6 da ficha: não existem importadores de
JSON, pedidos às APIs da Lusófona, scraping ou carregamento de dados. O modelo
de TFC é deliberadamente inicial e deverá ser revisto quando o JSON real for
analisado.

O diário de modelação e o DER encontram-se em
[`docs/MAKING_OF.md`](docs/MAKING_OF.md).
