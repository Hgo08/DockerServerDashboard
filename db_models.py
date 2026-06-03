# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Setting(db.Model):
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.String(255), nullable=False)

    @staticmethod
    def get_val(key, default=None):
        setting = Setting.query.get(key)
        return setting.value if setting else default