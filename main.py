import uvicorn
import logging
from app.api import app

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Запуск сервера T-Bank Logo Detector")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
