# AJF-Tech deployment guide

## What changed

- Secrets are no longer hardcoded in `config/settings.py`.
- The app now reads values from environment variables or `.env`.
- Web dependencies were reduced to the packages the Django site actually uses.
- Optional analytics libraries were moved to `requirements-analytics.txt`.
- Static files are configured for production with WhiteNoise.

## Important hosting reality

Hostinger shared hosting is not suitable for this Django project.
Keep Hostinger only for the domain and DNS if needed.

## Lowest-cost path

1. Keep the backend in Django.
2. Deploy the app on Railway or Render.
3. Point `ajftech.tech` from Hostinger DNS to that app.
4. Use Postgres in production instead of SQLite.

## Minimum env vars

- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS=ajftech.tech,www.ajftech.tech`
- `CSRF_TRUSTED_ORIGINS=https://ajftech.tech,https://www.ajftech.tech`
- `DATABASE_URL`
- `MISTRAL_API_KEY` if AI chat is enabled

## Local run

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Optional analytics script

If you want to run `rapportSeminaire.py`, also install:

```bash
pip install -r requirements-analytics.txt
```
