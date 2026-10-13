# CRM Project – Reference and Important Details

## Overview
This repository implements a lightweight **RugsCo ERP / CRM** system built with **Django**, **Django‑Admin**, **Jazzmin** for UI theming, **Django‑Import‑Export** for bulk data handling, and **Django‑REST‑Framework** for API exposure.  The core models cover:
- Accounts & Interactions
- Invoices, Payments, Shipments
- Master Orders & Sale Records (imported from Excel/CSV)
- Debit Notes (financial adjustments)
- Leads (sales pipeline) with a custom visual analytics dashboard

---

## Useful Open‑Source CRM References
| Project | Language / Framework | Highlights | Why it matters |
|---|---|---|---|
| **EspoCRM** | PHP (Laravel) | Full‑featured lead, opportunity, activity tracking; REST API; easy extensions | Shows how a robust lead pipeline can be structured – useful for future feature extensions (e.g., opportunity stages). |
| **Dolibarr ERP/CRM** | PHP | Integrated invoicing, payments, shipping, multi‑company support | Demonstrates solid accounting flows that map well to our `Invoice`, `Payment`, and `Shipment` models. |
| **Odoo** (Community) | Python (ORM) | Very modular – CRM, Sales, Accounting, Inventory; powerful reporting | Provides ideas for modular app design and reusable wizard patterns that could replace our custom admin actions. |
| **Saleor** | Python (Django + GraphQL) | Headless commerce, GraphQL API, modern UI | Inspires a potential move to a GraphQL API for our mobile/web front‑ends. |
| **SimpleCRM** (GitHub: `simplecrm-django`) | Python (Django) | Minimal lead management, dashboard widgets | Very close to our current stack – a good reference for lean feature sets and clean admin customizations. |

---

## Important Architectural Details
1. **Database** – Currently using SQLite for local development. For production on Render (or any persistent environment) switch to PostgreSQL to avoid data loss on each deploy.
2. **Authentication** – A default super‑user (`admin` / `Admin@12345`) is created by `create_admin.py` during the build step.  Consider using environment variables (`DJANGO_SUPERUSER_USERNAME`, etc.) for better security.
3. **Static Files** – `whitenoise` handles static file serving; ensure `STATIC_ROOT` is set and `collectstatic` runs in `build.sh`.
4. **Dashboard** – Two dashboards exist:
   - **Leads Dashboard** (`erp/templates/admin/erp/lead/change_list.html`) – specific to the Lead model.
   - **Global CRM Dashboard** (`templates/admin/index.html`) – shown on the admin home page with overall stats (total leads, orders, debit notes) and Chart.js visualisations.
   Both use the same **Glassmorphism** CSS styling.
5. **API** – DRF viewsets are wired in `erp/urls.py`.  They expose standard CRUD endpoints for all core models.  Authentication is via Django session cookies by default.
6. **Import/Export** – `django-import-export` resources are registered in `admin.py` for bulk Excel/CSV uploads (e.g., Master Orders).

---

## Suggested Enhancements (Future Roadmap)
- **Switch to PostgreSQL** – Update `DATABASES` in `config/settings.py` to use `dj-database-url` and configure a Render Postgres add‑on.
- **Token‑Based API** – Add `djangorestframework-simplejwt` for API clients (mobile apps, external services).
- **GraphQL API** – Use `graphene-django` to provide flexible data queries akin to Saleor.
- **Role‑Based Permissions** – Implement `django-guardian` or custom groups to restrict access to sensitive models (e.g., Debit Notes).
- **Email Notifications** – Hook into signals (`post_save`) for Leads to auto‑email sales reps when a new lead is created.
- **Background Tasks** – Integrate `django-q` or `Celery` for periodic reports (e.g., daily lead conversion summary).
- **Unit Tests** – Add a minimal test suite (`tests/`) covering model validation and the dashboard view.

---

## Quick Start Checklist for New Developers
```bash
# Clone & cd into the project (already done)
poetry install   # install deps (or pip install -r requirements.txt)
python manage.py migrate   # apply migrations
python create_admin.py     # creates default admin (admin / Admin@12345)
python manage.py runserver  # start dev server
```
Visit `http://127.0.0.1:8000/admin/` → you will see the **Global CRM Dashboard** on the home page, and the **Leads** section under the ERP app.

---

## Licensing & Credits
- This code is released under the **MIT License**.
- UI styling uses **Chart.js** (MIT) and **Jazzmin** (BSD‑3).
- Inspiration for the glass‑morphism theme was taken from various modern admin templates.

For any further questions or feature requests, feel free to open an issue on the repository.
