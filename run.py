# 启动脚本

from app import app
from config import UPLOAD_FOLDER, FLASK_HOST, FLASK_PORT, FLASK_DEBUG
from app.di.container import container

if __name__ == '__main__':
    container.init_index(UPLOAD_FOLDER)
    app.run(
        debug=FLASK_DEBUG,
        host=FLASK_HOST,
        port=FLASK_PORT
    )
