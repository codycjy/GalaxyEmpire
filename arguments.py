import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--ENABLE_MYSQL", action="store_true", help="enable mysql")
parser.add_argument("-L", "--LOG_LEVEL", type=str, default="INFO", help="log level")
args = parser.parse_args()
ENABLE_MYSQL = args.ENABLE_MYSQL
LOG_LEVEL = args.LOG_LEVEL
SALT = 'b6bd8a93c54cc404c80d5a6833ba12eb'
