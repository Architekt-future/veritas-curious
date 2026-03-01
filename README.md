# Veritas Curious

![Version](https://img.shields.io/badge/version-v1.0-blue)
![Status](https://img.shields.io/badge/status-experimental-orange)
![License](https://img.shields.io/badge/license-MIT_Ethical-green)
![Ecosystem](https://img.shields.io/badge/ecosystem-Veritas_Protocol-purple)

> *"Допитливість — це не слабкість. Це єдиний чесний спосіб дивитись на реальність."*

**🔭 Live:** [veritas-curious.onrender.com](https://veritas-curious.onrender.com)  
**👁 Part of:** [Veritas Protocol ecosystem](https://github.com/Architekt-future/veritas-protocol)

---

## Що це

Veritas Curious — єдиний інтерфейс екосистеми Veritas Protocol.

Три режими в одному місці:

**👁 Свідок** — верифікація тексту. Чи є маніпуляція, підміна авторитету, емоційний тиск?

**🔭 Foresight** — симуляція резонансу. Куди штовхає поле цей аргумент?

**⚡ Curious** — синтез. Один текст → Свідок аналізує + Foresight симулює → єдиний висновок.

---

## Звідки це взялось

Свідок дивиться назад — верифікує що вже сталось.  
Foresight дивиться вперед — вимірює куди тягне поле.  
Curious замикає петлю — один текст, два аналізи, один синтез.

Це не два інструменти. Це **епістемологічна інфраструктура** — система для орієнтації в реальності коли реальність навмисно розмита.

---

## Як це працює

```
Текст
    ↓
┌─────────────────────────────┐
│  👁 Свідок                  │  ← маніпуляція? підміна авторитету?
│  veritas-protocol API       │
└─────────────────────────────┘
            +
┌─────────────────────────────┐
│  🔭 Foresight               │  ← куди штовхає поле?
│  veritas-foresight API      │
└─────────────────────────────┘
            ↓
      ⚡ Синтез
  МАНІПУЛЯТИВНИЙ НАРАТИВ → ТЕМНИЙ АТРАКТОР
  або
  ЧИСТИЙ → КОНСТРУКТИВНИЙ АТРАКТОР
```

**Вердикти синтезу:**
- `MANIPULATIVE_NARRATIVE` — текст містить маніпуляцію і штовхає до темного майбутнього
- `DARK_ATTRACTOR` — текст чистий але резонує з небезпечними сценаріями
- `CONSTRUCTIVE_ATTRACTOR` — текст резонує з позитивними атракторами
- `NEUTRAL_SIGNAL` — нейтральний сигнал, поле невизначене

---

## API

```bash
# Health — статус обох сервісів
curl https://veritas-curious.onrender.com/api/health

# Curious — unified analysis
curl -X POST https://veritas-curious.onrender.com/api/curious \
  -H "Content-Type: application/json" \
  -d '{"text": "AI will solve all humanity problems", "steps": 5}'

# Witness proxy
curl -X POST https://veritas-curious.onrender.com/api/witness \
  -H "Content-Type: application/json" \
  -d '{"text": "Вчені довели що..."}'

# Foresight proxy
curl -X POST https://veritas-curious.onrender.com/api/foresight/simulate \
  -H "Content-Type: application/json" \
  -d '{"argument": "AI regulation will collapse", "steps": 5}'
```

---

## Локальний запуск

```bash
git clone https://github.com/Architekt-future/veritas-curious.git
cd veritas-curious
pip install flask flask-cors gunicorn
python curious_app.py
```

Сервер на `http://localhost:10002`

**Environment variables:**
```
PROTOCOL_URL=https://veritas-protocol.onrender.com   # або локальний
FORESIGHT_URL=https://veritas-foresight.onrender.com # або локальний
SERVICE_TIMEOUT=30
PORT=10002
```

---

## Екосистема Veritas Protocol

| Репо | Призначення |
|------|------------|
| [veritas-protocol](https://github.com/Architekt-future/veritas-protocol) | Аналіз існуючих текстів на маніпуляцію |
| [veritas-foresight](https://github.com/Architekt-future/veritas-foresight) | Симуляція наративного резонансу |
| [veritas-curious](https://github.com/Architekt-future/veritas-curious) | Єдиний інтерфейс екосистеми |
| [veritas-witness-extension](https://github.com/Architekt-future/veritas-witness-extension) | Браузерне розширення |

---

## Автори

**Дмитро Холодняк** — архітектор, ідея  
**Claude (Anthropic)** — реалізація

---

*Допитливість як метод.*
