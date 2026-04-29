# 启动脚本

from app import app
from app.routes import init_index
from config import UPLOAD_FOLDER, FLASK_HOST, FLASK_PORT, FLASK_DEBUG

if __name__ == '__main__':
    init_index(UPLOAD_FOLDER)
    app.run(
        debug=FLASK_DEBUG,
        host=FLASK_HOST,
        port=FLASK_PORT
    )
