# AI PRD Generator v2.1 - Enhanced Interactive Chat

Pokročilý interaktivní nástroj pro vytváření a editaci Product Requirements Documents (PRD) pomocí GPT-4o s pokročilým session managementem a version control.

## 🚀 Nové funkce v v2.1

### 🗂️ Session Management

- **Navigace mezi sessions** - Proklikávání mezi různými produkty/projekty
- **Session list** - Přehled všech sessions s počtem verzí
- **Active session indicator** - Vizuální označení aktivní session

### 🔄 Advanced Version Control

- **Version navigation** - Tlačítka ⬅️ ➡️ pro pohyb mezi verzemi
- **Diff view** - Zelené/červené zobrazení změn mezi verzemi
- **Side-by-side comparison** - Porovnání verzí vedle sebe
- **Change statistics** - Počet přidaných/odebraných řádků
- **Quick current button** - Rychlý návrat na aktuální verzi

### � User Prompt History (NEW!)

- **Original request display** - Zobrazení původního uživatelského promptu
- **Historical context** - Pochopení, proč byla verze vytvořena
- **Audit trail** - Kompletní historie požadavků a změn
- **Expandable prompts** - Prompty v sidebar i main preview

### �💫 Enhanced UX

- **Loading overlay** - Točící kolečko s overlay při zpracování
- **Smart quick actions** - Funkční rychlá tlačítka pro časté úpravy
- **Version status indicators** - Zobrazení aktuální vs. historické verze
- **Disabled editing** - Editace pouze aktuální verze

### 🎨 Vylepšené UI

- **Custom CSS styling** - Profesionální vzhled
- **Interactive elements** - Hover efekty a transitions
- **Visual feedback** - Jasné indikátory stavu
- **Responsive design** - Optimalizace pro různé velikosti

## 📁 Struktura projektu

```
PRD-Generator/
├── app/
│   ├── app.py                 # Hlavní Streamlit aplikace (Enhanced)
│   ├── utils/
│   │   ├── database.py        # SQLite databáze s rozšířenými funkcemi
│   │   ├── llm_utils.py       # GPT-4o integrace
│   │   ├── file_utils.py      # Zpracování souborů
│   │   └── diff_utils.py      # Diff zobrazování a statistiky
│   └── components/
├── .env                       # Environment proměnné
├── .env.example              # Šablona pro env proměnné
├── .gitignore                # Git ignore (chrání API klíče)
├── requirements.txt          # Python závislosti
├── start.sh                  # Rychlý start script
└── .vscode/                  # VS Code konfigurace pro debugging
```

## 🛠️ Instalace a spuštění

### 1. Klonování a prostředí

```bash
cd PRD-Generator
python3 -m venv .venv
source .venv/bin/activate  # na macOS/Linux
pip install -r requirements.txt
```

### 2. Konfigurace API klíče

```bash
# Zkopírujte .env.example do .env
cp .env.example .env

# Editujte .env a nastavte váš OpenAI API klíč
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 3. Spuštění aplikace

```bash
# Rychlé spuštění
./start.sh

# Nebo manuálně
streamlit run app/app.py
```

Nebo použijte VS Code debugging (F5) s připravenou konfigurací.

## 🎯 Jak používat

### 1. Session Management

1. **Nová session** - Klikněte "🆕 New Session"
2. **Přepínání sessions** - Vyberte session ze seznamu v sidebaru
3. **Aktivní session** - Označena zeleným kroužkem

### 2. Vytvoření nového PRD

1. Zadejte název produktu
2. Nahrajte MRD dokument (volitelné)
3. Přidejte dodatečný kontext
4. Klikněte "🎯 Generate Initial PRD"

### 3. Interaktivní úpravy

- **Chat zprávy** - Pište požadavky na změny
- **Quick actions** - Použijte tlačítka pro časté úpravy
- **Loading overlay** - Sledujte progress při zpracování
- **Real-time preview** - Okamžitý náhled změn

### 4. Version Control & Navigation

- **⬅️ ➡️ tlačítka** - Navigace mezi verzemi
- **🔄 Current** - Rychlý návrat na aktuální verzi
- **Show differences** - Zapnutí diff view
- **Version history** - Detailní historie v sidebaru

### 5. Diff zobrazování

- **Side-by-side view** - Porovnání verzí vedle sebe
- **Change statistics** - Přidané/odebrané řádky
- **Color coding** - Zelená (přidáno), červená (odebráno)

### 6. Stahování

- **Download button** - Pouze pro aktuální verzi
- **Auto naming** - Soubor s časovým razítkem

## 🔧 Technické detaily

### Databáze (SQLite) - Enhanced

```sql
sessions:
- session_id, product_name, created_at, updated_at

versions:
- session_id, version_number, content, section_name, change_description, created_at

chat_messages:
- session_id, message_type, content, created_at
```

### Nové funkce v databázi

- `get_max_version_number()` - Najít nejvyšší verzi
- `get_version_by_number()` - Načíst konkrétní verzi
- `get_all_sessions()` - Seznam všech sessions s počtem verzí

### Diff Engine

- **Line-by-line comparison** pomocí `difflib`
- **HTML rendering** s color coding
- **Change statistics** - přidané/odebrané řádky
- **Side-by-side view** - pro lepší porovnání

### UX Enhancements

- **Loading overlay** s CSS animations
- **State management** pro viewing vs. current version
- **Smart navigation** s disabled states
- **Visual feedback** pro všechny akce

## 🚨 Požadavky

- Python 3.9+
- OpenAI API klíč
- Internetové připojení

## 📝 Changelog

### v2.1.0 - Enhanced Navigation & UX

- ✅ Session management s přepínáním
- ✅ Version navigation (prev/next/current)
- ✅ Diff view s side-by-side porovnáním
- ✅ Loading overlay s animací
- ✅ Funkční quick action tlačítka
- ✅ **User prompt history** - zobrazení původních požadavků
- ✅ **Audit trail** - kompletní historie s kontextem
- ✅ Improved CSS styling
- ✅ Smart state management

### v2.0.0 - Interactive Chat Version

- ✅ Interaktivní chat interface
- ✅ SQLite databáze pro historie verzí
- ✅ Přímé stahování PRD souborů
- ✅ GPT-4o integrace s error handling
- ✅ Vylepšené UX s real-time náhledem
- ✅ VS Code debugging konfigurace

### v1.0.0 - Original Version

- Základní generování PRD z MRD
- Statické sekce
- Jednorázové generování

## 🎨 UI/UX Features

### Visual Design

- 🎨 **Custom CSS** - Profesionální styling
- 🌈 **Color coding** - Intuitivní barevné rozlišení
- ⚡ **Animations** - Loading spinner a transitions
- 📱 **Responsive** - Optimalizace pro různé velikosti

### Interaction Design

- 🖱️ **Hover effects** - Interactive feedback
- 🔘 **Smart buttons** - Contextual enable/disable
- 📊 **Progress indicators** - Loading states
- 🔄 **State persistence** - Zachování stavu při navigaci

## 🤝 Příspěvky

Projekt je otevřený pro příspěvky. Pro nové funkce vytvořte issue nebo pull request.

## 📄 Licence

MIT License

---

**🚀 Aplikace běží na:** http://localhost:8501  
**⚡ Quick start:** `./start.sh`
