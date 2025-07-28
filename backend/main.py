import argparse
import asyncio
from cli.cli import CLI
from scripts.bootstrap import bootstrap


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cli", action="store_true",
                        help="run interactive CLI")

    args = parser.parse_args()

    if args.cli:
        async def _main():
            ctx = await bootstrap()
            try:
                await CLI(ctx).run()
            finally:
                await ctx.exchange.stop()
        asyncio.run(_main())
    else:
        print("Nothing to do. Use --cli or run uvicorn from Docker.")


if __name__ == "__main__":
    main()
