# Portfólio

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

## Autenticação e permissões — Ficha 9

- O login por username e password está disponível em `/accounts/login/`.
- O registo exige um email único e associa automaticamente a conta ao grupo `autores`.
- O link mágico é enviado para o terminal em desenvolvimento e expira após 15 minutos.
- Apenas `gestor-portfolio` e superusers podem gerir o conteúdo do portfólio.
- Apenas autores podem publicar; cada autor só edita e elimina os seus artigos.
- Likes são públicos e identificados por utilizador ou pela sessão anónima do browser.
- Comentários exigem autenticação.

Para repor os grupos e criar dados de demonstração idempotentes:

```bash
python manage.py seed_ficha9_demo
```

O comando não substitui passwords de utilizadores já existentes.
