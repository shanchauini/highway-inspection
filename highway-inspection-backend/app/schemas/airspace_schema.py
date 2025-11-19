from marshmallow import Schema, fields, validate


class AirspaceCreateSchema(Schema):
    """空域创建Schema"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    number = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    type = fields.Str(required=True, validate=validate.OneOf(['suitable', 'restricted', 'no_fly']))
    area = fields.Dict(required=True)  # GeoJSON格式
    remark = fields.Str(allow_none=True)
    status = fields.Str(validate=validate.OneOf(['available', 'occupied', 'unavailable']), missing='available')


class AirspaceUpdateSchema(Schema):
    """空域更新Schema"""
    name = fields.Str(validate=validate.Length(min=1, max=100))
    number = fields.Str(validate=validate.Length(min=1, max=50))
    type = fields.Str(validate=validate.OneOf(['suitable', 'restricted', 'no_fly']))
    area = fields.Dict()
    remark = fields.Str(allow_none=True)
    # 管理员只能设置 available 或 unavailable，occupied 状态由任务自动管理
    status = fields.Str(validate=validate.OneOf(['available', 'unavailable']))

