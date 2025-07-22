import argparse
import asyncio
from cli.cli import CLI
from scripts.bootstrap import bootstrap

def manual_loop(ctx):
    CLI(ctx).run()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cli", action="store_true", help="run interactive CLI")
    args = parser.parse_args()

    ctx = asyncio.run(bootstrap())
    if args.cli:
        manual_loop(ctx)
    else:
        print("Nothing to do. Use --cli or run uvicorn from Docker.")

if __name__ == "__main__":
    main()
