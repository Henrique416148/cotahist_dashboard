# 📈 COTAHIST Dashboard – ETL & Visualização de Dados da B3

<p align="center">
  <img src="assets/demo.gif" alt="Demonstração do dashboard" width="720">
</p>

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35.0-ff4b4b.svg)](https://streamlit.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-blue.svg)](https://www.postgresql.org/)
[![CI](https://github.com/Henrique416148/cotahist_dashboard/actions/workflows/tests.yml/badge.svg)](https://github.com/Henrique416148/cotahist_dashboard/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🏆 Descrição

Este repositório apresenta uma solução completa de **Data Science** para o mercado financeiro brasileiro, usando a base **COTAHIST** da B3.

* **ETL**: download diário, limpeza e carga no **PostgreSQL 17**;
* **Dashboard**: visualização interativa com **Streamlit**;
* **Automação**: pipeline no **GitHub Actions** com testes em **pytest** e agendamento (`cron`).

<!-- Dica: Adapte a descrição para seu contexto ou vagas-alvo. -->

---

## 📂 Índice

* [🏆 Descrição](#🏆-descrição)
* [🛠️ Stack](#🛠️-stack)
* [🚀 Como rodar localmente](#🚀-como-rodar-localmente)
* [🔬 Metodologia](#🔬-metodologia)
* [📊 Resultados](#📊-resultados)
* [💡 Aprendizados & Diferenciais](#💡-aprendizados--diferenciais)
* [👤 Autor](#👤-autor)

---

## 🛠️ Stack

| Camada        | Tecnologias principais               |
| ------------- | ------------------------------------ |
| Ingestão      | `Python 3.12`, `requests`, `pandas`  |
| Armazenamento | `PostgreSQL 17`, `SQLAlchemy`        |
| Visualização  | `Streamlit 1.35`, `Plotly`, `Altair` |
| Qualidade     | `pytest`, `coverage`                 |
| Orquestração  | `GitHub Actions` (CI/CD + cron)      |

---

## 🚀 Como rodar localmente

```bash
# 1. Clone o projeto
 git clone https://github.com/Henrique416148/cotahist_dashboard.git
 cd cotahist_dashboard

# 2. (Opcional) Crie ambiente virtual
 python -m venv .venv
 source .venv/bin/activate   # Windows: .\.venv\Scripts\activate

# 3. Instale dependências
 pip install -r requirements.txt

# 4. Configuração
 cp .env.example .env      # edite DB_URL=postgresql://usuario:senha@localhost:5432/cotahist

# 5. Execute o ETL
 python etl.py             # baixa e carrega dados no Postgres

# 6. Inicie o dashboard
 streamlit run app_preco_volume.py
```

> ⚡ **Dica:** tudo isso roda no *CI* semanalmente (`.github/workflows/etl.yml`).

---

## 🔬 Metodologia

| Fase             | Ferramentas                         | Técnicas / Objetivo            |
| ---------------- | ----------------------------------- | ------------------------------ |
| **Coleta**       | `requests`, `schedule`              | Download do arquivo COTAHIST   |
| **Preprocess**   | `pandas`, `numpy`                   | *Parsing*, tratamento de nulos |
| **Persistência** | `SQLAlchemy`, `PostgreSQL`          | Tabelas normalizadas + índices |
| **Visualização** | `Streamlit`, `Plotly`               | Gráficos OHLC, volume, filtros |
| **Deploy**       | `GitHub Actions`, `Streamlit Cloud` | CI/CD + demo pública           |

---

## 📊 Resultados

* **+10 anos** de histórico diário da B3 carregados em < 30 s.
* Consulta interativa por **ticker**, **período** e **time frame**.
* **Dashboard** disponível em produção 👉 [https://cotahist-dashboard.streamlit.app](https://cotahist-dashboard.streamlit.app)

<p align="center">
  <img src="assets/screenshot.png" alt="Screenshot do dashboard" width="720">
</p>

---

## 💡 Aprendizados & Diferenciais

* **Pipeline completo** (ETL → API → Dashboard) pronto para nuvem.
* **Testes automatizados** garantem integridade dos dados a cada *push*.
* **CI/CD** no GitHub Actions + deploy grátis via Streamlit Cloud.
* **Modularidade**: fácil plugar novos datasets ou hospedar no AWS RDS.

---

## 👤 Autor

|                   |                                                                                                                                      |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| **Luis Henrique** | [https://www.linkedin.com/in/luis-henrique-dos-ribeiro-991aa8250/](https://www.linkedin.com/in/luis-henrique-dos-ribeiro-991aa8250/) |
| **Portfólio**     | [https://github.com/Henrique416148](https://github.com/Henrique416148)                                                               |

---

<!-- Sinta‑se à vontade para abrir _issues_ ou _pull requests_. Obrigado pela visita! -->



