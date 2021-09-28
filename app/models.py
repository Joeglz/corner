from tortoise import fields
from tortoise.models import Model
from passlib.hash import bcrypt

class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(50, unique=True)
    password_hash = fields.CharField(128)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def verify_password(self, password):
        return bcrypt.verify(password, self.password_hash)

class Data(Model):
    id = fields.IntField(pk=True)
    value = fields.CharField(128)
    provider = fields.CharField(1)
    last_updated = fields.DatetimeField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)