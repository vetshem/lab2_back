# schemas.py
from marshmallow import Schema, fields, validate, ValidationError

class UserSchema(Schema):
    id = fields.Int()
    username = fields.String(required=True)
    default_currency_id = fields.Int(required=False)
    password = fields.String(required=True)
class CategorySchema(Schema):
    name = fields.String(required=True)

class RecordSchema(Schema):
    category_id = fields.Integer(required=True, validate=validate.Range(min=0))
    user_id = fields.Integer(required=True, validate=validate.Range(min=0))
    amount = fields.Float(required=True, validate=validate.Range(min=0.0))
    currency_id = fields.Int(required=False)
class CurrencySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    symbol = fields.Str(required=True)
