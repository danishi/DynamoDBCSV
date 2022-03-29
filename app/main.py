import os
import boto3
import configparser
import argparse
import sys
from typing import Any

from app.dynamodb import csv_import, csv_export, truncate

__version__ = "1.3.3"
config_file = "config.ini"


def main() -> str:
    """Main routine

    Raises:
        ValueError: invalied config

    Returns:
        str: result message
    """

    result = "No operations."

    # arguments parse
    args = parse_args(sys.argv[1:])

    # boto3 config setting
    try:
        table = config_read_and_get_table(args)
    except ValueError as e:
        return str(e)

    except Exception:
        return f"Invalid format {config_file} file"

    # csv import
    if args.imp:
        if args.file is not None:
            result = csv_import(table, args.file)
        else:
            result = "Import mode requires a input file option."

    # csv export
    if args.exp:
        if args.output is not None:
            result = csv_export(table, args.output)
        else:
            result = "Export mode requires a output file option."

    # truncate table
    if args.truncate:
        result = truncate(table)

    return result


def parse_args(args: str) -> Any:
    """Parse arguments

    Args:
        args (str): _description_

    Returns:
        Any: parsed args
    """
    parser = argparse.ArgumentParser(
        description="Import CSV file into DynamoDB table utilities")
    parser.add_argument("-v", "--version", action="version",
                        version=__version__,
                        help="show version")
    parser.add_argument(
        "-i", "--imp", help="mode import", action="store_true")
    parser.add_argument(
        "-e", "--exp", help="mode export", action="store_true")
    parser.add_argument(
        "--truncate", help="mode truncate", action="store_true")
    parser.add_argument(
        "-t", "--table", help="DynamoDB table name", required=True)
    parser.add_argument(
        "-f", "--file", help="UTF-8 CSV file path required import mode")
    parser.add_argument(
        "-o", "--output", help="output file path required export mode")

    return parser.parse_args()


def config_read_and_get_table(args: Any) -> Any:
    """Config read and Create DynamoDB table instance

    Args:
        args (Any): arguments

    Returns:
        Any: DynamoDB table class
    """
    if not os.path.isfile(config_file):
        raise ValueError(f"Please make your {config_file} file")

    config = configparser.ConfigParser()
    config.read_dict({"AWS": {"ENDPOINT_URL": ""}})
    config.read(config_file)

    endpoint_url = None
    if config.get("AWS", "ENDPOINT_URL"):
        endpoint_url = config.get("AWS", "ENDPOINT_URL")
    dynamodb = boto3.resource("dynamodb",
        region_name=config.get("AWS", "REGION"),
        aws_access_key_id=config.get("AWS", "AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=config.get("AWS", "AWS_SECRET_ACCESS_KEY"),
        endpoint_url=endpoint_url)

    table = dynamodb.Table(args.table)
    return table


if __name__ == "__main__":
    result = main()
    print(result)