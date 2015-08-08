import peewee
db = None
base_model = None

def set_db(_db_):
    global  db
    db = _db_

def get_base_model():
    global base_model
    if base_model:
        return base_model

    class BaseModel(peewee.Model):
        class Meta:
            database = db

    base_model = BaseModel
    return  base_model