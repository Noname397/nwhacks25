from marshmallow import Schema, fields, validate

class ItemSchema(Schema):
    """
    Example schema for items in the 'items' collection.
    """
    name = fields.String(required=True, validate=validate.Length(min=1))
    quantity = fields.Integer(required=True, validate=validate.Range(min=1))
    price = fields.Float(required=True, validate=validate.Range(min=0.0))

item_schema = ItemSchema()           # For single item
items_schema = ItemSchema(many=True) # For multiple items
