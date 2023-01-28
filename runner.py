from App import create_app
from argParser import parser

args = parser.parse_args()

if __name__ == '__main__':
    app = create_app()
    app.run(args.host, args.port)
