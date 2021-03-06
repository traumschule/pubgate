
from pubgate.app import create_app
from pubgate.logging import PGHttpProtocol

if __name__ == "__main__":

    app = create_app('config/conf.cfg')
    app.run(host="0.0.0.0", port=8000, protocol=PGHttpProtocol)
