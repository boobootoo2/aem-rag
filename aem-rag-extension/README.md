# AEM RAG Extension — Architecture & Step-by-Step Build Guide

> **Goal**: Package a reusable AEM add-on that brings Retrieval-Augmented Generation (RAG) to AEM.  
> **Key design**: **Keep Python** for **indexing/embeddings** (fast iteration, rich ecosystem), and run **querying** natively in **AEM (Java Sling Servlet)** for seamless author UX, security, and scale.

![Alt text](aem-rag-integration.png)

## 1) High-Level Architecture

```mermaid
flowchart LR
  AEM[(AEM Author/Publish)]
  subgraph AEM Bundle
    S[/RagQueryServlet\n(/bin/ragquery)/]
    IDX[[RagIndexService\n(OO/RPC to Python)]]
    SCH[[RagIndexerScheduler\n(CRON/Oak Event)]]
    CFG[(OSGi Config)]
  end
  PY[Python Indexer\n(flatten_infinity.py + build_index.py)]
  VEC[(Vector Store)\nFAISS files under /var/rag-index]
  LLM[(OpenAI API)]
  UI[Tools ▸ AEM RAG Console\n(HTL + clientlib)]
  
  UI --> S
  S --> IDX
  SCH --> IDX
  IDX <--> PY
  PY --> VEC
  IDX --> VEC
  S --> VEC
  S --> LLM
  CFG --> SCH
  CFG --> IDX
  CFG --> S
  AEM --- UI
  AEM --- S
```

## 2) Repositories & Modules

```
aem-rag-extension/
├─ aem/                      # Maven AEM project (core/ui.apps/ui.config/all)
│  ├─ core/                  # OSGi services, servlet, scheduler
│  ├─ ui.apps/               # HTL component, clientlibs, tool registration
│  ├─ ui.config/             # OSGi configs (defaults)
│  └─ all/                   # Deployable content package
└─ indexer/                  # Python indexer (your existing code)
   ├─ flatten_infinity.py
   ├─ build_index.py
   ├─ requirements.txt
   └─ aem_index_meta.json  (generated)
```

## 3) Data Model & Storage

- Flattened corpus: `aem_index_meta.json` (array of `{ content, metadata }`).
- Vector store: FAISS artifacts under `/var/rag-index/` (`index.faiss`, `index.pkl`, `meta/aem_index_meta.json`).

## 4) Configuration (OSGi)

`com.example.aem.rag.config.RagConfig` exposes:
- `openai.api.key`, `index.paths`, `index.storage`, `model.chat`, `max.k`, `index.cron`

## 5) Indexing Pipeline (Python)

1. Crawl & flatten (`flatten_infinity.py`) — pagination-aware AEM fetch.  
2. Build FAISS (`build_index.py`) — writes vectors to `/var/rag-index`.

## 6) Query Path (Java, inside AEM)

`/bin/ragquery` servlet:
- Retrieve neighbors → build prompt → call OpenAI → return JSON/Markdown.

## 7) Background Indexing

`RagIndexerScheduler` triggers periodic `RagIndexService.rebuildIndex()` for automated refresh.

## 8) Author UI

Tools ▸ General ▸ **AEM RAG Console** (HTL + clientlib) posts to `/bin/ragquery`.

## 9) Quick Start

**AEM side**
```bash
cd aem-rag-extension/aem
mvn clean install -PautoInstallSinglePackage
```

**Python side**
```bash
cd ../indexer
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
python flatten_infinity.py
python build_index.py
```

## 10) Notes

- Keep secrets server-side (OSGi config).  
- Consider atomic index swaps (`/var/rag-index.staging` → `/var/rag-index`).  
- Optional: Lucene HNSW vectors as pure-Java alternative to FAISS.
