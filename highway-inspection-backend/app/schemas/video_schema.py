from marshmallow import Schema, fields, validate


class VideoUploadSchema(Schema):
    """视频上传Schema"""
    mission_id = fields.Int(required=True)
    collected_time = fields.DateTime(required=True, format='iso')
    road_section = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    file_format = fields.Str(validate=validate.OneOf(['mp4', 'avi', 'mov', 'mkv']), missing='mp4')
    file_size = fields.Int(allow_none=True)
    duration = fields.Int(allow_none=True)

