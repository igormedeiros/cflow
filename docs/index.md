# Fluxr - Task Automation Framework

Fluxr é um framework Python para automação de workflow e integração entre diferentes ferramentas e APIs. Permite que desenvolvedores definam pipelines de dados personalizados usando triggers, conectores, ferramentas e tarefas modulares para orquestrar workflows.

## Estrutura do Projeto

```python
fluxr/
├── connectors/    # Conectores para diferentes fontes de dados/APIs
├── tools/         # Ferramentas reutilizáveis
├── tasks/         # Tarefas que combinam conectores e ferramentas
└── flux.py        # Definição do workflow
```

## Recursos Principais

Modularidade: Conectores, ferramentas e tarefas são componentes modulares que podem ser combinados
Execution Hooks: Adicione comportamentos personalizados antes e depois das execuções
Resiliência: Implementação de mecanismos de retry (com exponential backoff) para conectores
Monitoramento e Logging: Logging detalhado e monitoramento de métricas do workflow
Estados do Workflow: O workflow gerencia seu próprio ciclo de vida

## Exemplo Rápido
```python
from fluxr.flux import Flux
from fluxr.connectors.excel import ExcelConnector
from fluxr.connectors.telegram import TelegramConnector
from fluxr.tasks import ExcelToTelegramTask

def main():
    # Configurando conectores
    excel = ExcelConnector(name="Excel", file_path="data.xlsx")
    telegram = TelegramConnector(name="Telegram", token="BOT_TOKEN")

    # Criando uma tarefa
    task = ExcelToTelegramTask(
        name="Excel to Telegram",
        connectors=[excel, telegram]
    )

    # Configurando o workflow
    workflow = Flux(
        name="Data Pipeline",
        connectors=[excel, telegram],
        tasks=[task]
    )

    # Executando
    workflow.run()
```

