`docs/guide/getting-started.md`:
```markdown
# Primeiros Passos

## Configuração Básica

```python
from fluxr.flux import Flux
from fluxr.connectors.excel import ExcelConnector
from fluxr.connectors.telegram import TelegramConnector

# Configuração dos conectores
excel = ExcelConnector(name="Excel", file_path="data.xlsx")
telegram = TelegramConnector(name="Telegram", token="BOT_TOKEN")

# Criação do workflow
workflow = Flux(
    name="Meu Primeiro Workflow",
    connectors=[excel, telegram]
)