# Swiss Tournament Simulator

Un simulatore moderno per tornei di calcio europei con sistema svizzero. L'applicazione simula un girone unico con formato svizzero e genera i playoff per le tre competizioni europee (Champions League, Europa League e Conference League).

## 🌟 Caratteristiche

- **Sistema Svizzero**: 8 turni di accoppiamenti basati su punteggi simili
- **Simulazione Realistica**: Algoritmo migliorato con distribuzione di Poisson per risultati realistici
- **Peso al Ranking UEFA**: I risultati sono fortemente influenzati dal ranking UEFA delle squadre
- **Statistiche Complete**: Punti, vittorie, pareggi, sconfitte, gol fatti/subiti, differenza reti
- **Playoff Automatici**: Generazione automatica dei playoff per le 3 coppe europee
- **Web App Moderna**: Interfaccia web responsive e user-friendly
- **Standalone**: Funziona completamente in locale senza server esterni

## 📊 Formato Torneo

### Fase Svizzera (8 turni)
- Tutti i 96 team giocano in un girone unico
- Accoppiamenti basati su punteggi simili (evitando rematches)
- Classifica con tiebreaker: Punti → Differenza Reti → Gol Fatti

### Fase Playoff
Dopo gli 8 turni svizzeri, le squadre vengono distribuite in:

- **Champions League** (Pos. 1-24): 12 playoff (1 vs 24, 2 vs 23, ..., 12 vs 13)
- **Europa League** (Pos. 25-48): 12 playoff (25 vs 48, 26 vs 47, ..., 36 vs 37)
- **Conference League** (Pos. 49-80): 16 playoff (49 vs 80, 50 vs 79, ..., 64 vs 65)
- **Eliminate** (Pos. 81+): Retrocesse/eliminate

## 🚀 Installazione e Avvio

### Metodo 1: Script automatico (consigliato)

```bash
# Clone repository
git clone https://github.com/MartoEporedia/swiss-tournament.git
cd swiss-tournament

# Avvia l'applicazione (installa automaticamente le dipendenze)
./run.sh
```

### Metodo 2: Manuale

```bash
# Clone repository
git clone https://github.com/MartoEporedia/swiss-tournament.git
cd swiss-tournament

# Installa dipendenze
pip install -r requirements.txt

# Avvia l'applicazione
python app.py
```

L'applicazione sarà disponibile su: **http://localhost:5000**

## 🎮 Come Usare

1. **Reset Tournament**: Inizializza il torneo con 96 squadre europee
2. **Create Pairings**: Genera gli accoppiamenti per il prossimo turno
3. **Simulate Matches**: Simula tutte le partite del turno corrente
4. **Ripeti 2-3** per completare 8 turni svizzeri
5. **Generate Playoffs**: Dopo 8 turni, genera i playoff per le 3 coppe

### Tabs

- **📊 Standings**: Classifica completa con statistiche e categorizzazione
- **⚽ Matches**: Risultati di tutte le partite, filtrabili per turno
- **🏆 Playoffs**: Accoppiamenti playoff per Champions, Europa e Conference League

## 🧮 Algoritmo di Simulazione

### Distribuzione di Poisson
L'algoritmo utilizza la distribuzione di Poisson per generare gol realistici:

```python
expected_goals = BASE_GOALS + (ranking_diff × RANKING_FACTOR)
```

- **BASE_GOALS**: 1.3 (media gol per squadra)
- **RANKING_FACTOR**: 0.015 (impatto della differenza di ranking)
- La differenza di ranking ha un peso significativo sui risultati

### Esempi di Probabilità

**Manchester City (148) vs Getafe (9)**
- Differenza ranking: +139
- Expected goals: 3.4 vs 0.3
- Probabilità vittoria City: ~93%

**Barcelona (91) vs Bayer Leverkusen (90)**
- Differenza ranking: +1
- Expected goals: 1.31 vs 1.29
- Probabilità: ~37% vs ~36% (26% pareggio)

## 📁 Struttura Progetto

```
swiss-tournament/
├── app.py                 # Backend Flask con API REST
├── database.py            # Gestione database SQLite
├── simulator.py           # Algoritmo di simulazione partite
├── create_db.py           # Dati squadre e ranking UEFA
├── templates/
│   └── index.html        # Frontend web
├── static/
│   ├── css/
│   │   └── style.css     # Stili moderni
│   └── js/
│       └── app.js        # Logica frontend
├── requirements.txt       # Dipendenze Python
└── run.sh                # Script di avvio

# File legacy (non più utilizzati)
├── main.py               # Vecchia app PyQt5
└── test_tournament.py    # Test per vecchia versione
```

## 🔧 Requisiti

- Python 3.7+
- Flask >= 2.0.0
- flask-cors >= 3.0.0
- pandas >= 1.1.0

Tutte le dipendenze vengono installate automaticamente con `pip install -r requirements.txt`.

## 📊 Database

SQLite database con 4 tabelle:

- **teams**: Squadre con ranking UEFA
- **standings**: Classifica con statistiche complete
- **pairings**: Accoppiamenti e risultati partite
- **playoffs**: Accoppiamenti playoff per le 3 coppe

## 🎯 API Endpoints

- `POST /api/init` - Inizializza torneo
- `GET /api/teams` - Lista squadre
- `GET /api/standings` - Classifica attuale
- `GET /api/pairings?round=X` - Accoppiamenti (opzionale: per turno)
- `POST /api/pairings/create` - Crea accoppiamenti prossimo turno
- `POST /api/simulate` - Simula partite
- `POST /api/playoffs/generate` - Genera playoff
- `GET /api/playoffs` - Ottieni playoff
- `GET /api/stats` - Statistiche torneo

## 🔄 Differenze con la Versione Precedente

### ✅ Miglioramenti

- **Web App** invece di desktop PyQt5
- **Algoritmo Poisson** invece di gaussiano
- **Peso maggiore al ranking** (0.015 vs 0.002)
- **Statistiche complete** (W/D/L, GF/GA, GD)
- **Tiebreaker avanzati** (punti → GD → GF)
- **Playoff automatici** per le 3 coppe
- **UI moderna** responsive e user-friendly

## 🤝 Contribuire

Pull requests sono benvenute! Per modifiche importanti, apri prima un issue per discutere i cambiamenti.

## 📝 License

Questo progetto è sotto licenza MIT.

## 🙏 Ringraziamenti

- Ranking UEFA ufficiali
- Flask framework
- Algoritmo Swiss-system tournament

---

**Sviluppato con ⚽ per gli appassionati di calcio europeo**
