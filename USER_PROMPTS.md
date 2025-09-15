# 📝 User Prompt History - Feature Documentation

## 🎯 Nová funkce: Zobrazení původních promptů

V historických verzích PRD je nyní viditelné, jaký přesný prompt byl poslán AI agentovi pro vytvoření dané verze.

## 🏗️ Implementace

### 📊 Databázové změny

```sql
-- Rozšíření tabulky versions o user_prompt
ALTER TABLE versions ADD COLUMN user_prompt TEXT;

-- Nová struktura:
versions:
  - id, session_id, version_number
  - content, section_name, change_description
  - user_prompt (NOVÉ!)
  - created_at
```

### 🔄 Automatická migrace

- Při prvním spuštění se automaticky přidá sloupec `user_prompt`
- Starší verze bez promptu budují fungovat normálně

## 🎨 UI Změny

### 📚 Sidebar - Version History

```
Version 3 - 2025-09-15 15:45
├── Changes: Added mobile features section
└── 📝 Original Request (expandable)
    └── [Text area with original user prompt]
```

### 📄 Main Preview Panel

Pro historické verze se zobrazuje:

```
📝 Original Request for this Version (expandable)
├── User Prompt: [readonly text area]
└── AI Changes Made: [info box with changes]
```

## 📋 Co se ukládá

### Initial PRD (Version 1)

```
User Prompt includes:
- Product: [product name]
- MRD Content: [first 200 chars of MRD]...
- Additional Context: [user context]
```

### Update Versions (Version 2+)

```
User Prompt = exact user message from chat
Examples:
- "Add a section about mobile app features"
- "Update the timeline to include Q2 milestones"
- "Remove the analytics requirements"
```

### Quick Actions

```
Quick action buttons generate standard prompts:
- "Add a new section to the PRD"
- "Update the timeline and milestones"
- "Add or update success metrics"
```

## 🎯 Výhody

### 👀 Transparentnost

- **Viditelnost procesu**: Jasné zobrazení, co uživatel požadoval
- **Audit trail**: Kompletní historie změn s důvody
- **Debug možnosti**: Pochopení, proč AI udělalo specifické změny

### 🔍 Analysis

- **Pattern recognition**: Rozpoznání častých typů požadavků
- **Quality control**: Ověření, zda AI splnilo požadavek
- **Learning**: Pochopení, jak formulovat lepší prompty

### 🔄 Reprodukovatelnost

- **Rollback s kontextem**: Nejen co se změnilo, ale proč
- **Inspiration**: Nápady pro budoucí úpravy
- **Consistency**: Konzistentní styl požadavků

## 🎨 Visual Design

### CSS Styly

```css
.user-prompt-box {
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  font-family: "Courier New", monospace;
  /* Monospace font pro lepší čitelnost promptů */
}

.prompt-header {
  background-color: #e9ecef;
  font-weight: bold;
  /* Jasné označení sekce s promptem */
}
```

### 📱 Responsive Features

- **Expandable sections**: Prompty nezabírají místo když nejsou potřeba
- **Readonly mode**: Nelze editovat historické prompty
- **Consistent styling**: Stejný vzhled v sidebar i main panel

## 🔧 Technical Details

### Database Migration

```python
# Automatická detekce a migrace
cursor.execute("PRAGMA table_info(versions)")
columns = [column[1] for column in cursor.fetchall()]
if 'user_prompt' not in columns:
    cursor.execute('ALTER TABLE versions ADD COLUMN user_prompt TEXT')
```

### Function Signatures

```python
# Updated save_version function
def save_version(session_id, content, section_name=None,
                change_description=None, user_prompt=None) -> int

# Updated get functions return user_prompt in dict
{'version_number': 1, 'content': '...', 'user_prompt': '...', ...}
```

## 🚀 Usage Examples

### 📝 Pro uživatele

1. **Vytvoř PRD** → Zobrazí se první verze s initial prompt
2. **Požádej o změnu** → "Add mobile features"
3. **Přepni na historii** → Vidíš přesně co jsi požadoval
4. **Porovnej verze** → Pochopíš jak AI interpretoval požadavek

### 🔍 Pro analýzu

```
Version 1: "Product: Smart Scheduler, MRD: Meeting management..."
Version 2: "Add mobile app support with push notifications"
Version 3: "Update timeline to include Q2 2024 milestones"
Version 4: "Remove analytics section, add security requirements"
```

## ⚡ Performance Impact

### 💾 Storage

- **Minimal overhead**: Text prompts jsou relativně malé
- **Efficient indexing**: Indexy zůstávají rychlé
- **Optional field**: Starší verze bez promptů fungují normálně

### 🚀 Loading

- **Lazy loading**: Prompty se načítají jen když potřeba
- **Expandable UI**: Nezpomaluje základní view
- **Cached queries**: Stejné dotazy jsou cachovány

## 🎉 User Feedback Expected

### ✅ Pozitivní

- **"Konečně vidím, co jsem vlastně požadoval!"**
- **"Pomáhá mi formulovat lepší požadavky"**
- **"Audit trail je skvělý pro team collaboration"**

### 🔄 Možná vylepšení

- **Prompt templates**: Předpřipravené prompty pro časté akce
- **Prompt history**: Vyhledávání podobných požadavků
- **Smart suggestions**: AI navrhuje optimalizace promptů

## 📚 Related Features

Tato funkce doplňuje:

- 🔄 **Version navigation** - Navigace mezi verzemi
- 🎨 **Diff viewing** - Porovnání změn
- 💾 **Session management** - Správa projektů
- 📊 **Change statistics** - Analýza změn

---

**🌐 Aplikace s user prompt history běží na:** http://localhost:8501
