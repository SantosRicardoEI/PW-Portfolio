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

Aceder ao painel de administração em
[http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) com o superuser
criado localmente. Nunca devem ser usadas credenciais de demonstração em
produção.

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

---

## Deploy cloud — Ficha 10

A configuração é controlada por variáveis de ambiente. O ficheiro `.env` é
local e nunca deve ser submetido ao Git; `.env.example` documenta apenas os
nomes necessários.

### PostgreSQL no Neon

Antes de definir `DATABASE_URL`, exportar os dados do SQLite:

```bash
python manage.py dumpdata auth.user portfolio escola artigos \
  --exclude artigos.likeartigo \
  --natural-foreign --natural-primary --indent 2 \
  --output dados.json
```

Depois de inserir no `.env` a connection string pooled do Neon:

```bash
python manage.py migrate
python manage.py loaddata dados.json
python manage.py changepassword admin
python manage.py seed_ficha9_demo
```

`dados.json`, tokens mágicos, sessões e likes anónimos não são versionados.

### Media no Cloudinary

Inserir as três credenciais Cloudinary no `.env` e verificar primeiro os 14
ficheiros atualmente associados aos modelos:

```bash
python manage.py migrate_media_cloudinary --dry-run
python manage.py migrate_media_cloudinary
```

O segundo comando é idempotente: ignora ficheiros que já existam remotamente.

### Static e produção

Os ficheiros CSS e imagens fixas são recolhidos e servidos pelo WhiteNoise:

```bash
python manage.py collectstatic --noinput
gunicorn project.wsgi
```

Em produção devem ser definidos `DEBUG=False`, uma `SECRET_KEY` forte,
`ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` e `SECURE_SSL_REDIRECT=True`.
