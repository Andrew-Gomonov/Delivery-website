from App import app
from argParser import parser

args = parser.parse_args()

if __name__ == '__main__':
    app.run(args.host, args.port)
