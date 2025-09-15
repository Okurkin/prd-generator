# 🛠️ Utility Scripts Documentation

Tento projekt obsahuje několik utility scriptů pro snadnou správu aplikace.

## 📜 Dostupné scripty

### 🚀 `start.sh` - Spuštění aplikace

```bash
./start.sh
```

**Co dělá:**

- ✅ Kontroluje existenci virtual environment
- ✅ Kontroluje existenci .env souboru
- ✅ Kontroluje, zda port 8501 není obsazený
- ✅ Aktivuje virtual environment
- ✅ Spustí Streamlit aplikaci

### 🧹 `cleanup.sh` - Kompletní vyčištění

```bash
./cleanup.sh
```

**Co dělá:**

- 🔫 Killne všechny procesy na portech 8501-8505
- 🔫 Killne všechny Streamlit procesy
- 🗑️ Smaže všechny databázové soubory (prd_history.db, test_prd.db)
- 🗑️ Smaže cache soubory (.streamlit, **pycache**)
- 🗑️ Smaže .pyc a temporary soubory
- ⚠️ **Vyžaduje potvrzení před spuštěním**

### ⚡ `reset.sh` - Rychlý reset

```bash
./reset.sh
```

**Co dělá:**

- 🔫 Rychle killne procesy na portech 8501-8503
- 🔫 Killne Streamlit procesy
- 🗑️ Smaže databáze a cache
- 🚀 **Bez potvrzení - okamžité spuštění**

## 🔄 Typické workflow

### Při prvním spuštění:

```bash
# 1. Nastavit environment
cp .env.example .env
# Editovat .env a nastavit OPENAI_API_KEY

# 2. Spustit aplikaci
./start.sh
```

### Při problémech s aplikací:

```bash
# Rychlý restart
./reset.sh && ./start.sh

# Nebo kompletní cleanup
./cleanup.sh
./start.sh
```

### Pro development:

```bash
# Reset před novým testem
./reset.sh

# Spuštění s fresh state
./start.sh
```

## ⚠️ Důležité poznámky

### `cleanup.sh` vs `reset.sh`

- **`cleanup.sh`** - Bezpečnější, vyžaduje potvrzení, detailní výstup
- **`reset.sh`** - Rychlejší, bez potvrzení, pro časté použití

### Co se smaže při cleanup/reset:

```
🗑️ Databázové soubory:
   - prd_history.db (všechny sessions a verze)
   - test_prd.db (testovací data)
   - *.db-shm, *.db-wal (SQLite soubory)

🗑️ Cache soubory:
   - .streamlit/ (Streamlit cache)
   - __pycache__/ (Python cache)
   - *.pyc (Python bytecode)
   - *.tmp, *.temp (temporary soubory)
```

### Co se NESMAZE:

```
✅ Zachová se:
   - .env soubor (API klíče)
   - .venv/ (virtual environment)
   - Zdrojové kódy
   - README a dokumentace
   - .git/ (git historie)
```

## 🚨 Port Management

### Porty používané aplikací:

- **8501** - Výchozí Streamlit port
- **8502-8505** - Backup porty při konfliktů

### Kontrola portů:

```bash
# Zjistit co běží na portu
lsof -i :8501

# Killnout specifický port
lsof -ti:8501 | xargs kill -9

# Najít všechny Streamlit procesy
pgrep -f streamlit
```

## 🐛 Troubleshooting

### Port už je obsazený:

```bash
./cleanup.sh  # nebo ./reset.sh
./start.sh
```

### Aplikace se nespustí:

```bash
# Zkontrolovat .env
cat .env

# Zkontrolovat virtual environment
source .venv/bin/activate
pip list | grep streamlit

# Reinstalace závislostí
pip install -r requirements.txt
```

### Databáze je poškozená:

```bash
./reset.sh  # Smaže všechny databáze
./start.sh  # Vytvoří nové
```

### Chyba při importu modulů:

```bash
# Reset Python cache
./reset.sh

# Nebo manuálně
find . -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete
```

## 📊 Exit kódy

### `start.sh`:

- **0** - Úspěšné spuštění
- **1** - Chybí .venv nebo .env

### `cleanup.sh`:

- **0** - Úspěšné vyčištění nebo zrušeno uživatelem
- **1** - Spuštěno z nesprávného adresáře

### `reset.sh`:

- **0** - Vždy (nemá error handling)

## 🎯 Příklady použití

### Development workflow:

```bash
# Začátek práce
./start.sh

# Testování změn
./reset.sh && ./start.sh

# Konec práce
./cleanup.sh
```

### Production deployment:

```bash
# Clean start
./cleanup.sh
./start.sh

# Monitor logs
tail -f ~/.streamlit/logs/streamlit.log
```

### Emergency reset:

```bash
# Když nic nefunguje
./reset.sh
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
./start.sh
```
