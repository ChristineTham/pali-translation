# pali-translation

Pāli translation tools based on dpd-db

1. Download and untar dpd.db
```sh
curl -O https://github.com/digitalpalidictionary/dpd-db/releases/download/v0.2.20250413/dpd.db.tar.bz2
tar xvf dpd.db.tar.bz2
```
2. Install [uv](https://astral.sh/uv/install) for your operating system
```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```
3. Install libraries and create environment
```sh
uv sync
```
4. Run test
```sh
uv run db_search_example.py
```
