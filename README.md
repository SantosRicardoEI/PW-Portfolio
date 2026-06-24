# Portfólio

**Aluno:** Ricardo Santos  
**Número:** 22409527  
**Curso:** Licenciatura em Engenharia Informática (LEI) — Universidade Lusófona

**User:** admin
**Password:** admin

---

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_ficha9_demo
python manage.py createsuperuser
```

---

## Executar localmente

Sem `DATABASE_URL` e credenciais Cloudinary, a aplicação usa automaticamente
SQLite e a pasta local `media/`.

```bash
python manage.py runserver
```

--
