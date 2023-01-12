from argparse import ArgumentParser

parser = ArgumentParser(
    prog='DeliveryWebsite',
    description='Simplifies the delivery of goods',
    epilog='With this website, delivery is easy',
    add_help=False
)

parser.add_argument(
    '--host',
    type=str,
    help='host for this delivery website',
    default="127.0.0.1",
    required=False
)
parser.add_argument(
    '--port',
    type=int,
    help='the port on which the delivery website will operate',
    default=5000,
    required=False
)
