from app.models import db, User
from flask_jwt_extended import create_access_token


class AuthService:
    """认证服务"""

    @staticmethod
    def register(username, password, role='operator'):
        """用户注册"""
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            raise ValueError('用户名已存在')

        # 创建新用户
        user = User(username=username, role=role)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return user

    @staticmethod
    def login(username, password):
        """用户登录"""
        # 查找用户
        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            raise ValueError('用户名或密码错误')

        # 生成JWT token（identity必须是字符串）
        access_token = create_access_token(identity=str(user.id))

        return {
            'user': user.to_dict(),
            'access_token': access_token
        }

    @staticmethod
    def get_user_by_id(user_id):
        """根据ID获取用户"""
        return User.query.get(user_id)

    @staticmethod
    def update_user(user_id, **kwargs):
        """更新用户信息"""
        user = User.query.get(user_id)
        if not user:
            raise ValueError('用户不存在')

        if 'password' in kwargs:
            user.set_password(kwargs['password'])
            kwargs.pop('password')

        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)

        db.session.commit()
        return user

