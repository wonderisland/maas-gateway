import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("model_gateway.log"), logging.StreamHandler()],
)
logger = logging.getLogger("maas_gateway")