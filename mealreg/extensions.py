from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# 實例化 ORM
db = SQLAlchemy()
# 實例化 JWT 管理器
jwt = JWTManager()