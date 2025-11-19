from marshmallow import Schema, fields, validate


class FlightApplicationCreateSchema(Schema):
    """飞行申请创建Schema"""
    drone_model = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    task_purpose = fields.Str(required=True, validate=validate.Length(min=1))
    planned_airspace_id = fields.Int(required=True)
    planned_start_time = fields.DateTime(required=True, format='iso')
    planned_end_time = fields.DateTime(required=True, format='iso')
    total_time = fields.Int(required=True)  # 分钟
    route = fields.Dict(required=True)  # GeoJSON格式
    is_long_term = fields.Bool(missing=False)
    long_term_start = fields.DateTime(format='iso', allow_none=True)
    long_term_end = fields.DateTime(format='iso', allow_none=True)


class FlightApplicationUpdateSchema(Schema):
    """飞行申请更新Schema（仅草稿状态）"""
    drone_model = fields.Str(validate=validate.Length(min=1, max=100))
    task_purpose = fields.Str(validate=validate.Length(min=1))
    planned_airspace_id = fields.Int()
    planned_start_time = fields.DateTime(format='iso')
    planned_end_time = fields.DateTime(format='iso')
    total_time = fields.Int()
    route = fields.Dict()
    is_long_term = fields.Bool()
    long_term_start = fields.DateTime(format='iso', allow_none=True)
    long_term_end = fields.DateTime(format='iso', allow_none=True)


class FlightApprovalSchema(Schema):
    """飞行申请审批Schema"""
    action = fields.Str(required=True, validate=validate.OneOf(['approve', 'reject']))
    rejection_reason = fields.Str(allow_none=True)

