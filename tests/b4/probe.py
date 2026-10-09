"""Ein Satz als Text, zum Ausprobieren. Aufruf: python tests/b4/probe.py "Satz" """

import asyncio
import collections
import sys

from rolle_app import Sitzung


async def main() -> None:
    async with Sitzung() as sitzung:
        antwort = await sitzung.sage_text(sys.argv[1])
        print({k: v for k, v in antwort.items() if k != "aufrufe"})
        print(collections.Counter(e["type"] for _, e in sitzung.ereignisse))


asyncio.run(main())
