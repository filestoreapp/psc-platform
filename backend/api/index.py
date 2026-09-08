from mangum import Mangum
import sys
sys.path.append("..")
from app.main import app

handler = Mangum(app, lifespan="off")
