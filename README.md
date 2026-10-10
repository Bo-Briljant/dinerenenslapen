# dinerenenslapen.nl

Statische site, gebouwd met `build/build.py` naar `docs/` en gehost op GitHub Pages.

- Bouwen: `python3 build/build.py` (Python 3 + Pillow). Beelden komen uit `DES_ASSETS`.
- Data: `build/data/data.json` (adressen, prijzen, teksten) en `build/data/blog.json` (verhalen).
- Elke pagina is gewone HTML met eigen title, meta description, canonical, hreflang en JSON-LD.
- `docs/sitemap.xml`, `docs/robots.txt` en `docs/llms.txt` worden mee gebouwd.
