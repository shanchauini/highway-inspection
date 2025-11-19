from marshmallow import Schema, fields, validate


class AlertCreateSchema(Schema):
    """告警创建Schema"""
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    event_type = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    severity = fields.Str(required=True, validate=validate.OneOf(['low', 'medium', 'high']))
    road_section = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    occurred_time = fields.DateTime(required=True, format='iso')
    video_id = fields.Int(required=True)
    mission_id = fields.Int(required=True)


class AlertUpdateSchema(Schema):
    """告警更新Schema"""
    status = fields.Str(required=True, validate=validate.OneOf(['new', 'confirmed', 'processing', 'closed']))

