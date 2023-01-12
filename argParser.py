from argparse import ArgumentParser

parser = ArgumentParser(
    prog='DeliverySystem',
    description='Simplifies the delivery of goods',
    epilog='With this system, delivery is easy',
    add_help=False
)

parser.add_argument(
    '--host',
    type=str,
    help='host for this delivery system',
    default="127.0.0.1",
    required=False
)
parser.add_argument(
    '--port',
    type=int,
    help='the port on which the delivery system will operate',
    default=5000,
    required=False
)