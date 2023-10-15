"""The Worker UI is a web interface for the ChimeraPy worker."""
import asyncio
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from pathlib import Path

from uvicorn import run

from chimerapy.workerui.utils import instantiate_worker


def add_worker_connect_parser(subparsers):
    """Add the worker connect parser to the subparsers."""
    worker_connect_parser = subparsers.add_parser(
        "connect",
        help="Connect to a ChimeraPy Manager",
    )

    worker_connect_parser.add_argument(
        "--name",
        "-n",
        required=True,
        type=str,
        help="Name of the worker",
    )

    worker_connect_parser.add_argument(
        "--id",
        default=None,
        type=str,
        help="Unique identifier for the worker",
    )

    worker_connect_parser.add_argument(
        "--zeroconf",
        "-z",
        action="store_true",
        help="Use zeroconf to find the manager",
    )

    worker_connect_parser.add_argument(
        "--ip",
        type=str,
        help="IP address of the manager",
        required=False,
    )

    worker_connect_parser.add_argument(
        "--port",
        "-p",
        type=int,
        help="Port of the manager",
        required=False,
    )

    worker_connect_parser.add_argument(
        "--delete-temp",
        "-d",
        action="store_true",
        help="Delete temporary files after processing",
        required=False,
    )

    worker_connect_parser.add_argument(
        "--wport",
        "-wp",
        type=int,
        default=0,
        help="Port to serve the worker on",
        required=False,
    )

    worker_connect_parser.add_argument(
        "--timeout",
        "-t",
        type=int,
        default=20,
        help="Timeout for connecting to the manager",
    )


def add_worker_ui_parser(subparsers):
    """Add the worker ui parser to the subparsers."""
    worker_ui_parser = subparsers.add_parser(
        "ui",
        help="Serve the ChimeraPy worker UI",
    )

    worker_ui_parser.add_argument(
        "--port",
        default=8000,
        type=int,
    )


async def aconnect_worker(args):
    """Connect the worker to the manager."""
    worker = instantiate_worker(
        name=args.name,
        id=args.id,
        wport=args.wport,
        delete_temp=args.delete_temp,
    )
    print("Starting worker")
    await worker.aserve()

    port = args.port
    ip = args.ip
    zeroconf = args.zeroconf

    method = "zeroconf" if zeroconf else "ip"

    success = await worker.async_connect(
        method=method,
        host=ip,
        port=port,
        timeout=args.timeout,
    )

    if not success:
        raise ConnectionError(
            "Connection to ChimeraPy Manager Failed. "
            "Please retry when the manager is running."
        )

    worker.logger.info("IDLE")
    while True:
        await asyncio.sleep(1)


def serve_worker_ui(args):
    """Serve the worker UI."""
    run(
        "chimerapy.workerui.server:create_worker_ui_app",
        host="0.0.0.0",
        port=args.port,
        log_level="info",
        factory=True,
        reload=True,
        reload_dirs=[str(Path(__file__).parent.parent.resolve())],
    )


def main(args=None):
    """The CLI entrypoint for the worker UI."""
    parser = ArgumentParser(
        description="Serve the ChimeraPy worker UI",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )

    subparsers = parser.add_subparsers(
        title="subcommands",
        description="valid subcommands",
        dest="subcommand",
    )

    add_worker_connect_parser(subparsers)
    add_worker_ui_parser(subparsers)

    cli_args = parser.parse_args(args)

    if cli_args.subcommand == "connect":
        asyncio.run(aconnect_worker(cli_args))
    elif cli_args.subcommand == "ui":
        serve_worker_ui(cli_args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
