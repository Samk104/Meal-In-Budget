from logging_config import setup_logging
from mib_app.services.utils import init_driver_pool
from mib_app import create_app


init_driver_pool(min_drivers=2, max_drivers=4)
setup_logging()


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=8080, use_reloader=False)
