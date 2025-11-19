from marshmallow import Schema, fields, validate


class UserLoginSchema(Schema):
    """用户登录Schema"""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    password = fields.Str(required=True, validate=validate.Length(min=4, max=128))


class UserRegisterSchema(Schema):
    """用户注册Schema"""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    password = fields.Str(required=True, validate=validate.Length(min=4, max=128))
    role = fields.Str(validate=validate.OneOf(['operator', 'admin']), missing='operator')


class UserUpdateSchema(Schema):
    """用户更新Schema"""
    password = fields.Str(validate=validate.Length(min=4, max=128))
    role = fields.Str(validate=validate.OneOf(['operator', 'admin']))

