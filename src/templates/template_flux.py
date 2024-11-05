from dotenv import load_dotenv

from core.flux.flux import Flux
from core.logger import log


def main():
    log.info("=== Initializing Flux ===")
    load_dotenv()

    # 1 - Configure connectors, tools, listener e tasks
    # 2 - Create flux

    flux = Flux(
        name="Template Flux",
        description="Description template",
        connectors=[],
        tools=[],
        listeners=[],
        tasks=[]
    )

    # Execute flux
    flux.execute()
    log.info("Flux executed successfully")


if __name__ == "__main__":
    main()