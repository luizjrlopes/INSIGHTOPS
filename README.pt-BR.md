# InsightOps AI

[English](README.md) | [Português](README.pt-BR.md)

InsightOps AI é uma plataforma de inteligência operacional para transformar dados de vendas, estoque, devoluções e suporte em datasets validados, KPIs determinísticos, sinais explicáveis de anomalia e análises fundamentadas em evidências.

O sistema foi projetado com separação rígida de responsabilidades: engenharia de dados, cálculo de KPIs e detecção de anomalias permanecem determinísticos, enquanto a camada de IA só pode inspecionar informações aprovadas por meio de ferramentas tipadas e somente leitura. O agente não pode executar SQL arbitrário, alterar dados operacionais, gerar previsões financeiras ou emitir recomendações de investimento.

## O que o InsightOps resolve

Equipes operacionais recebem dados de fontes desconectadas e precisam responder rapidamente a três perguntas:

1. **Esses dados são confiáveis?**
2. **O que mudou ou parece anormal?**
3. **Quais evidências sustentam a explicação?**

O InsightOps cobre esse fluxo de ponta a ponta: ingere dados operacionais, valida e coloca linhas inválidas em quarentena, produz análises reproduzíveis, detecta anomalias por regras estatísticas e expõe as evidências resultantes por dashboards e por um assistente de IA restrito.

## Capacidades principais

- ingestão de CSV e conectores operacionais simulados;
- validação de schema e regras de negócio antes da aceitação dos dados;
- quarentena de linhas rejeitadas com motivo explícito e linhagem de origem;
- transformações determinísticas com Polars;
- snapshots de KPI sobre o dataset válido mais recente;
- dashboards operacionais e filtros;
- detecção estatística de anomalias separada da interpretação por IA;
- investigação e resolução de anomalias;
- análise em linguagem natural baseada em evidências por ferramentas seguras;
- bloqueio explícito de SQL arbitrário e ferramentas fora da allowlist;
- geração de relatórios com histórico de exportações CSV/JSON;
- trilha de auditoria para cargas, anomalias, ferramentas do agente, exportações e ações administrativas;
- isolamento de falhas preservando o último snapshot analítico válido;
- reset local repetível para avaliação controlada.

## Arquitetura

```text
CSV / conectores simulados
        ↓
validação + quarentena
        ↓
transformações Polars
        ↓
PostgreSQL como analytics store operacional
        ↓
snapshots de KPI + engine de anomalias
        ↓
FastAPI
        ↓
Next.js UI
        ↓
ferramentas tipadas e somente leitura do agente
```

### Fronteiras de responsabilidade

- **Pipeline:** parsing, validação, transformação, linhagem da carga e linhas rejeitadas.
- **Analytics:** fórmulas determinísticas de KPI e snapshots.
- **Anomaly engine:** regras estatísticas, severidade e entradas do ciclo de vida da anomalia.
- **API/workflow:** RBAC, transições de estado e ações operacionais.
- **Agent layer:** acesso somente leitura por ferramentas tipadas e explicitamente permitidas.
- **Audit:** rastreabilidade de ações relevantes do usuário e do sistema.

## Stack tecnológica

| Camada | Tecnologia |
|---|---|
| Web | Next.js 16, React 19, TypeScript, App Router |
| API | Python 3.13, FastAPI, SQLAlchemy |
| Processamento de dados | Polars |
| Banco | PostgreSQL |
| Autenticação | Sessões JWT assinadas com RBAC server-side |
| Fronteira de IA | Abstração de provider + provider local determinístico + ferramentas tipadas |
| Runtime local | Docker Compose |

O ambiente local não exige serviço externo pago.

## Modelo de segurança do agente

O componente de IA é deliberadamente restrito. Ele recebe contexto operacional apenas por ferramentas tipadas cujas entradas e saídas são controladas pela aplicação.

O agente não pode:

- executar SQL arbitrário;
- gravar diretamente no banco;
- alterar estado de anomalias ou workflows;
- ignorar RBAC;
- inventar métricas operacionais fora da camada analítica determinística;
- produzir previsões financeiras ou recomendações de investimento.

Solicitações inseguras de ferramentas são rejeitadas antes da execução no banco e podem ser registradas na auditoria.

## Modelo de qualidade dos dados

Registros recebidos são validados antes de fazer parte do snapshot analítico ativo. Registros inválidos são colocados em quarentena com motivo de rejeição e linhagem de origem, em vez de serem descartados silenciosamente.

Uma carga com falha não substitui o último snapshot válido. Dashboards e consultas analíticas continuam sobre um dataset conhecido como válido mesmo quando uma nova importação falha.

## Execução local

```bash
cp .env.example .env
docker compose up --build
```

Serviços:

- aplicação web: `http://localhost:3000`
- API e documentação OpenAPI: `http://localhost:8000/docs`

A API inicializa automaticamente o schema local e os dados de exemplo.

## Fluxo de avaliação

1. importe `examples/sales_august.csv`;
2. inspecione resultados de validação e linhas em quarentena;
3. revise mudanças de KPI e a anomalia `AN-104`;
4. investigue a anomalia pelo agente orientado por evidências;
5. inspecione as ferramentas e evidências usadas pela resposta;
6. resolva uma anomalia pelo workflow autorizado;
7. gere uma exportação operacional;
8. inspecione a trilha de auditoria;
9. habilite o cenário de agente inseguro e confirme que `execute_sql` é bloqueado;
10. simule falha no pipeline e confirme que o último snapshot válido permanece ativo.

## Estrutura do repositório

```text
apps/
  api/       FastAPI, pipeline, analytics, engine de anomalias e agente seguro
  web/       aplicação Next.js
examples/    datasets operacionais de exemplo
docs/        arquitetura, pipeline de dados e segurança do agente
scripts/     validação determinística do repositório
```

## Validação

Backend e estrutura:

```bash
python scripts/validate_repo.py
python -m unittest discover apps/api/tests -v
```

Frontend:

```bash
cd apps/web
npm ci
npm run typecheck
npm run build
```

Ambiente completo:

```bash
docker compose up --build
```

## Documentação

- `docs/architecture.md`
- `docs/data-pipeline.md`
- `docs/agent-safety.md`
- `docs/demo.md`
