from marshmallow import Schema, fields, validate

class ScheduleSchema(Schema):
    """
    Marshmallow schema for a Schedule document/record.
    """
    class_name = fields.String(required=True)
    start_date = fields.DateTime(format='%Y-%m-%d', required=True)
    end_date = fields.DateTime(format='%Y-%m-%d', required=True)

    # Days must be a list containing only these values
    days = fields.List(
        fields.String(),
        required=True,
        validate=validate.ContainsOnly(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    )

    class_time = fields.String(required=True)
    location = fields.String(required=True)
    room = fields.String(required=True)

schedule_schema = ScheduleSchema()
schedules_schema = ScheduleSchema(many=True)
