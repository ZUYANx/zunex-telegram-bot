# config.py

BOT_TOKEN = "8847591236:AAEVfMbZbsfXGIXwNL9BHn2MPwSLWjKpuoU"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Database
DATABASE_FILE = "zunex_orders.db"

# Steadfast
STEADFAST_BASE_URL = "https://portal.packzy.com/api/v1"
LABEL_SIZE = "2x3"

# Image Hosting API (freeimage.host)
IMAGE_API_KEY = "6d207e02198a847aa98d0a2a901485a5"

# Order Settings
INVOICE_PREFIX = "ZX"
STARTING_ORDER_NUM = 1000

# SQLAlchemy
SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_FILE}"