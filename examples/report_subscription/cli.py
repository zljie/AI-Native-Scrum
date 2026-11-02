"""Demo CLI; each invocation reuses one explicit local SQLite file."""

import argparse
import json
import sys

from .service import ReportService


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True, help="local SQLite database path; no remote writes")
    commands = parser.add_subparsers(dest="command", required=True)
    subscribe = commands.add_parser("subscribe")
    subscribe.add_argument("--user", required=True)
    subscribe.add_argument("--report", required=True)
    request = commands.add_parser("request")
    request.add_argument("--user", required=True)
    request.add_argument("--description", required=True)
    listing = commands.add_parser("list")
    listing.add_argument("--user", required=True)
    args = parser.parse_args(argv)
    service = ReportService(args.db)
    try:
        if args.command == "subscribe":
            result = service.subscribe(args.user, args.report)
        elif args.command == "request":
            result = service.request_report(args.user, args.description)
        else:
            result = {"user_id": args.user, "reports": service.subscriptions(args.user)}
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2
    finally:
        service.close()
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
