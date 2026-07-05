# Assist Digital Project

Ein lokaler Rick-and-Morty-RAG-Chat mit FastAPI-Backend, Vue-Frontend, ChromaDB als Vektorspeicher und Azure OpenAI als Chat-Modell. Das System beantwortet Fragen ausschliesslich auf Basis der zuvor ingestierten Daten der [Rick and Morty API](https://rickandmortyapi.com/), zeigt Quellen an und bewertet jede Antwort mit einem Konfidenzscore. Zudem kann man jede Antwort mit einem Daumen hoch oder runter bewerten. Dies wird ebenfalls an das Model geschickt und beachtet das Feedback in den folgenden Antworten.

## Features

- Chat-UI für Fragen zu Charakteren, Episoden und Orten aus Rick and Morty
- Retrieval-Augmented Generation mit ChromaDB und `mixedbread-ai/mxbai-embed-large-v1`
- Query-Rewrite-Agent für bessere semantische Suchanfragen
- RAG-Agent mit Retrieval-Tools, Quellenpflicht und strikter Kontextbindung
- Confidence-Agent, der Antworten gegen den tatsächlich genutzten Retrieval-Kontext bewertet
- Optionaler Retry bei mittlerer Konfidenz
- Feedback-Endpunkt für Daumen-hoch/Daumen-runter-Signale in der laufenden Unterhaltung
- Docker-Compose-Setup für Backend, Frontend und optionalen Daten-Ingest

### Wichtige Komponenten

- `frontend/`: Vue 3 + Vite Chat-Oberfläche
- `backend/api.py`: FastAPI-App mit `/chat` und `/feedback`
- `backend/main.py`: Verdrahtung von Modell, ChromaDB und Agenten
- `backend/chat_service.py`: Orchestrierung von Rewrite, RAG, Confidence und Chat-Historie
- `backend/agents/agents_factory.py`: Agenten und Retrieval-Tools
- `backend/ingestion/`: Import aus der Rick-and-Morty-API und Upload in ChromaDB
- `backend/system_prompts/`: Systemprompts für RAG-, Rewrite- und Confidence-Agent
- `chromadb/`: persistierter lokaler Vektorindex

## Retrieval-Strategie

Die Datenbasis besteht aus strukturierten Entitäten der Rick-and-Morty-API: `characters`, `episodes` und `locations`. Beim Ingest werden die Rohdaten nicht nur gespeichert, sondern auch gegenseitig angereichert:

- Charaktere enthalten die Namen ihrer Episoden statt nur Episode-URLs.
- Episoden enthalten die Namen ihrer Charaktere.
- Locations enthalten die Namen ihrer Residents.
- Zusätzlich werden API-Info-Dokumente gespeichert, zum Beispiel Anzahl und Seiteninformationen je Entity-Gruppe.

Jede Entität wird als lesbarer Text serialisiert und mit `mixedbread-ai/mxbai-embed-large-v1` eingebettet. Die Embeddings liegen in ChromaDB in der Collection `rick_and_morty`.

Die eigentliche Anfrage läuft mehrstufig:

1. **Query Rewrite**  
   Die Nutzerfrage wird in eine kurze, semantisch starke Suchfrage umgeschrieben. um das semantische Retrieval
   effizienter zu gestalten.

2. **Semantisches Retrieval**  
   Das RAG-Tool sucht per Query-Embedding die besten Treffer in ChromaDB (`n_results=5`). Dadurch funktionieren auch Fragen, die nicht exakt dieselben Begriffe wie die Daten verwenden.

3. **Gezielte Tools für bekannte Zugriffsmuster**  
   Neben der freien Vektorsuche gibt es Tools wie z.B. Episoden per ID. Das reduziert Fehler bei Fragen wie "Wie viele Episoden gibt es?" oder "Was ist Episode 3?".

4. **Antwort nur aus Kontext**  
   Der RAG-Agent darf laut Prompt kein internes Modellwissen verwenden. Wenn der Retrieval-Kontext nicht reicht, soll er das ehrlich sagen.

5. **Confidence-Prüfung und Retry**  
   Ein separater Confidence-Agent bewertet, ob die Antwort durch die sichtbaren Tool-Ergebnisse belegt ist. Bei mittlerer Konfidenz wird ein zweiter Retrieval-/Antwortversuch gestartet.

## Setup: in 5 Minuten lokal starten

### Voraussetzungen

- Docker und Docker Compose
- Azure-OpenAI-kompatibler Endpoint mit Zugriff auf das Chat-Modell

### 1. Environment-Datei anlegen

Im Projektroot wird eine `.env` erwartet:

AZURE_ENDPOINT=https://<dein-resource>.openai.azure.com/openai/v1
AZURE_API=<api-key>

### 2. Docker Setup
Das Docker Setup besteht aus drei Service:
  - Frontend
  - Backend
  - load_data -> inserten der Daten von der API in die Vektor-DB (vorausgefüllte DB liegt bereits vor)

### 3. App starten

docker compose up --build -d frontend backend

Danach sind die Dienste erreichbar unter:

- Frontend: http://localhost:5173
- Backend/OpenAPI: http://localhost:8000/docs

Beim ersten Start kann das Backend etwas länger brauchen, weil das Embedding-Modell in das Docker-Volume `hf-cache` geladen wird.


### Optional: Vektorindex neu aufbauen

Der lokale ChromaDB-Index liegt unter `./chromadb`. Wenn die Daten neu geladen werden sollen, müssen die Dateien
unter im chromadb/ Ordner gelöscht werden und danach folgendes ausgeführt werden:

docker compose up -d ingest

## Lokale Entwicklung ohne Docker

Backend:

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000

Frontend:

cd frontend
npm ci
npm run dev -- --host 0.0.0.0 --port 5173

## Bekannte Limitierungen

- Die Chat-Historie liegt nur im Prozessspeicher. Es gibt keine Sessions pro Nutzer und keine Persistenz
- Feedback wird nicht in einer Datenbank gespeichert und nicht für Offline-Auswertung genutzt
- Retrieval nutzt einen festen Top-k-Wert (`n_results=5`) ohne Reranking oder Metadatenfilter
- Die semantische Suche arbeitet auf serialisierten Entity-Texten. Das ist einfach und transparent, aber nicht optimal für komplexe Aggregationen
- Es gibt keine automatisierten Tests, keine CI-Pipeline und keine Eval-Suite für Antwortqualität

## Was ich mit mehr Zeit anders machen würde

- Als Alternative zu einer klassischen RAG-Pipeline -> MCP-Server, wo dann das LLM die ANfragen an den Server    selber konstruieren kann
- Hybrid Retrieval kombinieren: Vektorsuche plus exakte Namens-/ID-Suche und Metadatenfilter nach `characters`, `episodes` und `locations`.
- Eine kleine RAG-Eval-Suite mit typischen Fragen, erwarteten Quellen und Confidence-Schwellen aufbauen.
- Einen Reranker nach der Chroma-Suche einsetzen, um die retrieveden Dokumente nach Relevanz nochmal zu sortieren
- Sessions, persistente Chat-Historie und persistentes Feedback einführen
- Backend-URL, Modellname, Collection, Top-k und CORS über Konfiguration steuerbar machen
- Tests für Ingest, Retrieval-Tools, API-Schemas und Prompt-orchestrierte Edge Cases ergänzen
- Streaming-Antworten und bessere Lade-/Fehlerzustände im Frontend einbauen
- Observability ergänzen: strukturierte Logs, Trace-IDs, Tool-Aufruf-Metriken und Confidence-Verteilung
