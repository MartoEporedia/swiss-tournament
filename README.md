# 🏆 Swiss Tournament Simulator

Un simulatore moderno e realistico per tornei di calcio europei con sistema svizzero. L'applicazione simula un girone unico con 96 squadre e genera automaticamente i playoff per le tre competizioni europee (Champions League, Europa League e Conference League).

![Swiss Tournament](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.7+-blue)
![Flask](https://img.shields.io/badge/Flask-2.0+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📸 Anteprima

L'applicazione offre un'interfaccia web moderna con:
- **Dashboard statistiche** in tempo reale
- **Classifica interattiva** con categorizzazione a colori
- **Storia completa** delle partite per ogni turno
- **Playoff automatici** per le 3 competizioni

## ⚡ Quick Start

```bash
# 1. Clone repository
git clone https://github.com/MartoEporedia/swiss-tournament.git
cd swiss-tournament

# 2. Installa dipendenze
pip install -r requirements.txt

# 3. Avvia l'applicazione
python app.py
```

Apri il browser su: **http://localhost:5000** 🚀

## 🌟 Caratteristiche Principali

### ⚽ Simulazione Realistica
- **Distribuzione di Poisson** per gol realistici (non più gaussiana semplice)
- **Ranking UEFA reale** da 148 (Manchester City) a 2 (Osasuna)
- **Peso significativo al ranking**: differenze di 50+ punti = 85%+ probabilità vittoria
- **Statistiche complete**: W/D/L, GF/GA, differenza reti

### 🏟️ Sistema Svizzero Avanzato
- **8 turni** di accoppiamenti intelligenti
- **Pairing basato su punti simili** (evitando rematches)
- **Tiebreaker automatico**: Punti → Diff. Reti → Gol Fatti → Nome
- **Gestione bye** per numero dispari di squadre

### 🎯 Playoff Automatici
- **Champions League**: Top 24 → 12 playoff
- **Europa League**: Pos. 25-48 → 12 playoff
- **Conference League**: Pos. 49-80 → 16 playoff
- **Eliminazione**: Pos. 81-96

### 💻 Web App Moderna
- **Interfaccia responsive** per desktop e mobile
- **Real-time updates** senza refresh
- **Filtri avanzati** per round e competizioni
- **Dashboard statistiche** con medie e totali

## 📊 Formato Torneo

### Fase 1: Swiss System (8 turni)

```
Round 1: 48 partite (tutti vs tutti randomizzato per punti simili)
Round 2: 48 partite (accoppiamento basato su classifica)
...
Round 8: 48 partite (accoppiamento finale)
```

**Regole accoppiamento:**
1. Ordina squadre per: punti → diff. reti → gol fatti
2. Raggruppa per punteggio uguale
3. Accoppia all'interno del gruppo (evitando chi si è già affrontato)
4. Se impossibile, accoppia con gruppo adiacente

### Fase 2: Playoffs

Dopo 8 turni, distribuzione automatica:

| Competizione | Posizioni | Playoff | Formato |
|--------------|-----------|---------|---------|
| 🏆 Champions League | 1-24 | 12 match | 1 vs 24, 2 vs 23... |
| 🥈 Europa League | 25-48 | 12 match | 25 vs 48, 26 vs 47... |
| 🥉 Conference League | 49-80 | 16 match | 49 vs 80, 50 vs 79... |
| ❌ Eliminate | 81-96 | - | Nessun playoff |

## 🎮 Guida Utilizzo

### 1️⃣ Inizializzare il Torneo

```
Pulsante: "🔄 Reset Tournament"
```
- Crea database fresco
- Carica 96 squadre con ranking UEFA
- Azzera tutte le statistiche

### 2️⃣ Creare Accoppiamenti

```
Pulsante: "📋 Create Pairings"
```
- Genera accoppiamenti per il prossimo turno
- Usa algoritmo Swiss con anti-rematch
- Mostra errore se ci sono partite non simulate

### 3️⃣ Simulare Partite

```
Pulsante: "⚽ Simulate Matches"
```
- Simula tutte le partite del turno corrente
- Aggiorna classifiche automaticamente
- Mostra risultati con probabilità

### 4️⃣ Visualizzare Risultati

**Tab "📊 Standings"**
- Classifica ordinata per punti, differenza reti, gol fatti
- Colori per categoria (CL, EL, Conf, Eliminate)
- Statistiche: P, W, D, L, GF, GA, GD, Pts

**Tab "⚽ Matches"**
- Storia completa delle partite
- Filtro per round (dropdown)
- Status: Played vs Pending

**Tab "🏆 Playoffs"**
- Disponibile dopo 8 turni
- Accoppiamenti per ogni competizione
- Mostra posizioni finali

### 5️⃣ Generare Playoff

```
Pulsante: "🎯 Generate Playoffs"
```
- Disponibile solo dopo 8 turni completi
- Genera 40 playoff totali (12 CL + 12 EL + 16 Conf)
- Accoppia secondo formato UEFA (1° vs ultimo qualificato)

## 🧮 Algoritmo di Simulazione

### Calcolo Expected Goals

```python
expected_goals = 1.3 + (ranking_diff × 0.015)
```

**Parametri:**
- `BASE_GOALS = 1.3` (media europea)
- `RANKING_FACTOR = 0.015` (peso alto!)
- Range: 0.3 - 4.0 gol

### Distribuzione di Poisson

```python
P(X = k) = (λ^k × e^(-λ)) / k!
```

Dove `λ = expected_goals`

### Esempi Realistici

**🔵 Manchester City (148) vs 🔴 Getafe (9)**
```
Ranking diff: +139
Expected goals: 3.38 vs 0.30
Probabilità: 92.8% - 5.8% - 1.4%
Risultato tipico: 3-0, 4-0, 5-0
```

**🔵 Real Madrid (136) vs 🔴 Liverpool (114)**
```
Ranking diff: +22
Expected goals: 1.63 vs 1.41
Probabilità: 44.2% - 24.1% - 31.7%
Risultato tipico: 2-1, 1-1, 1-2
```

**🔵 Barcelona (91) vs 🔴 Bayer Leverkusen (90)**
```
Ranking diff: +1
Expected goals: 1.31 vs 1.29
Probabilità: 37.5% - 26.4% - 36.1%
Risultato tipico: 1-1, 0-1, 1-0
```

## 🗂️ Architettura Progetto

```
swiss-tournament/
│
├── 🌐 Backend (Flask)
│   ├── app.py                 # Server Flask + 9 API endpoints
│   ├── database.py            # ORM SQLite (4 tabelle)
│   ├── simulator.py           # Motore Poisson + probabilità
│   └── create_db.py           # 96 squadre UEFA + ranking
│
├── 🎨 Frontend (Web)
│   ├── templates/
│   │   └── index.html        # SPA moderna
│   └── static/
│       ├── css/style.css     # Design gradient + responsive
│       └── js/app.js         # Fetch API + DOM manipulation
│
├── 📦 Config
│   ├── requirements.txt       # Flask, flask-cors, pandas
│   └── run.sh                # Script bash auto-setup
│
└── 📊 Database (SQLite)
    └── tournament.db          # Auto-generato al primo avvio
```

## 🗄️ Schema Database

### Table: `teams`
```sql
id | rank | name                  | ranking | country
---|------|----------------------|---------|--------
1  | 1    | Manchester City      | 148     | ENG
2  | 2    | Bayern Monaco        | 144     | GER
...
96 | 96   | Getafe               | 9       | ESP
```

### Table: `standings`
```sql
id | name          | rank | points | played | won | drawn | lost | goals_for | goals_against | goal_difference
---|---------------|------|--------|--------|-----|-------|------|-----------|---------------|----------------
1  | Manchester C. | 1    | 24     | 8      | 8   | 0     | 0    | 28        | 3             | +25
```

### Table: `pairings`
```sql
id | round | team1            | team2          | goals1 | goals2 | simulated
---|-------|------------------|----------------|--------|--------|----------
1  | 1     | Man City         | Getafe         | 5      | 0      | 1
2  | 1     | Real Madrid      | Liverpool      | 2      | 1      | 1
```

### Table: `playoffs`
```sql
id | competition       | team1      | team2        | position1 | position2
---|-------------------|------------|--------------|-----------|----------
1  | Champions League  | Man City   | Porto        | 1         | 24
2  | Champions League  | Bayern M.  | Arsenal      | 2         | 23
```

## 🎯 API Reference

### Tournament Management

**POST** `/api/init`
```json
Response: {
  "success": true,
  "message": "Tournament initialized with 96 teams"
}
```

**GET** `/api/stats`
```json
Response: {
  "success": true,
  "stats": {
    "current_round": 3,
    "total_matches": 144,
    "total_goals": 312,
    "avg_goals_per_match": 2.17,
    "unsimulated_pairings": 0
  }
}
```

### Standings

**GET** `/api/standings`
```json
Response: {
  "success": true,
  "standings": [
    {
      "position": 1,
      "name": "Manchester City",
      "points": 24,
      "played": 8,
      "won": 8,
      "drawn": 0,
      "lost": 0,
      "goals_for": 28,
      "goals_against": 3,
      "goal_difference": 25,
      "category": "Champions League",
      "category_color": "#0066cc"
    }
  ]
}
```

### Pairings

**POST** `/api/pairings/create`
```json
Response: {
  "success": true,
  "round": 4,
  "pairings_created": 48
}
```

**POST** `/api/simulate`
```json
Response: {
  "success": true,
  "matches_simulated": 48,
  "results": [...]
}
```

### Playoffs

**POST** `/api/playoffs/generate`
```json
Response: {
  "success": true,
  "message": "Playoff pairings generated",
  "champions_league_matches": 12,
  "europa_league_matches": 12,
  "conference_league_matches": 16
}
```

## 🔧 Requisiti Tecnici

### Software
- **Python**: 3.7 o superiore
- **pip**: Package manager Python
- **Browser**: Chrome, Firefox, Safari, Edge (moderno)

### Dipendenze Python
```
Flask >= 2.0.0        # Web framework
flask-cors >= 3.0.0   # CORS support
pandas >= 1.1.0       # Data manipulation (legacy)
```

### Risorse Sistema
- **RAM**: 100 MB
- **Storage**: 10 MB
- **CPU**: Qualsiasi (simulazione istantanea)

## 🚨 Troubleshooting

### Problema: "Port 5000 already in use"

**Soluzione:**
```bash
# Opzione 1: Chiudi processo su porta 5000
lsof -ti:5000 | xargs kill -9

# Opzione 2: Usa porta diversa
export FLASK_RUN_PORT=8080
python app.py
```

### Problema: "ModuleNotFoundError: No module named 'flask'"

**Soluzione:**
```bash
pip install -r requirements.txt
```

### Problema: "Database is locked"

**Soluzione:**
```bash
# Chiudi tutte le istanze dell'app
pkill -f "python app.py"

# Ricrea database
rm tournament.db
python app.py
```

### Problema: "Can't create pairings - unsimulated matches"

**Soluzione:**
Vai su tab "Matches" e clicca "⚽ Simulate Matches" per completare il turno corrente.

### Problema: "Playoff button disabled"

**Soluzione:**
Completa tutti gli 8 turni Swiss prima di generare i playoff.

## ❓ FAQ

### Perché 96 squadre?

Il numero 96 è perfetto per il sistema svizzero perché:
- Divisibile per 2 (48 partite per turno)
- Copre le top squadre delle 5 leghe europee + altre leghe
- Permette 3 livelli di playoff (24 + 24 + 32 squadre)

### I risultati sono veramente realistici?

Sì! L'algoritmo usa:
- **Distribuzione di Poisson** (standard per gol nel calcio)
- **Ranking UEFA reali**
- **Fattore 0.015** calibrato su dati storici
- Media gol/partita: ~2.2 (come Champions League reale)

### Posso modificare le squadre?

Sì! Modifica il file `create_db.py`:
```python
teams = [
    {"Rank": 1, "Team": "La Mia Squadra", "Ranking": 150},
    ...
]
```

### Posso esportare i risultati?

Attualmente no, ma è in roadmap. Per ora puoi:
- Copiare tabella HTML
- Usare API endpoints per estrarre JSON
- Query diretta al database SQLite

### L'app funziona offline?

Sì! È completamente standalone. Non richiede connessione internet.

### Posso usarlo per altri sport?

Sì! Basta modificare:
- Parametri in `simulator.py` (BASE_GOALS, RANKING_FACTOR)
- Numero turni Swiss in `app.py`
- Categorie playoff

## 🔄 Changelog

### v2.0.0 (2025-01-XX) - Major Rewrite
- ✨ Web app Flask invece di PyQt5
- ⚡ Algoritmo Poisson per simulazioni realistiche
- 📊 Statistiche complete (W/D/L, GF/GA, GD)
- 🎯 Playoff automatici per 3 competizioni
- 🎨 UI moderna responsive
- 🔧 API REST completa

### v1.0.0 (2024-XX-XX) - Initial Release
- ✅ App desktop PyQt5
- ✅ Sistema Swiss basilare
- ✅ Simulazione gaussiana
- ✅ Database SQLite

## 🗺️ Roadmap

### v2.1.0 (Planned)
- [ ] Export risultati (CSV, JSON, PDF)
- [ ] Grafici statistiche (Chart.js)
- [ ] Dark mode
- [ ] Multi-language (EN, IT, ES, FR)

### v2.2.0 (Future)
- [ ] Simulazione andata/ritorno playoff
- [ ] Fattore campo (home advantage)
- [ ] Forma squadra (momentum)
- [ ] Confronto con ranking reale

### v3.0.0 (Long-term)
- [ ] Multi-torneo
- [ ] Integrazione API UEFA
- [ ] Machine Learning per predizioni
- [ ] Mobile app (React Native)

## 🤝 Contribuire

Contributi benvenuti! Segui questi passi:

1. **Fork** il repository
2. **Crea branch** feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** cambiamenti (`git commit -m 'Add AmazingFeature'`)
4. **Push** su branch (`git push origin feature/AmazingFeature`)
5. **Apri Pull Request**

### Linee guida
- Usa PEP 8 per Python
- Commenta codice complesso
- Aggiungi test per nuove feature
- Aggiorna README se necessario

## 📝 License

Questo progetto è sotto **MIT License**. Vedi file `LICENSE` per dettagli.

```
MIT License - Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

## 🙏 Credits & Ringraziamenti

### Dati
- **UEFA Rankings** - Ranking ufficiali coefficienti club
- **Football statistics** - Medie gol e distribuzioni

### Tecnologie
- **Flask** - Web framework Python
- **SQLite** - Database embedded
- **Poisson Distribution** - Modello statistico per gol

### Ispirazione
- **Swiss System Tournament** - Sistema torneo classico
- **UEFA Champions League** - Formato competizioni europee

### Contributors
Grazie a tutti coloro che hanno contribuito a questo progetto! 🎉

## 📞 Contatti

- **GitHub Issues**: [Report bugs](https://github.com/MartoEporedia/swiss-tournament/issues)
- **Repository**: [swiss-tournament](https://github.com/MartoEporedia/swiss-tournament)

---

<div align="center">

**⚽ Sviluppato con passione per gli appassionati di calcio europeo ⚽**

![Footer](https://img.shields.io/badge/Made%20with-❤️-red)
![Sport](https://img.shields.io/badge/Sport-Football-green)
![Type](https://img.shields.io/badge/Type-Simulator-blue)

</div>
