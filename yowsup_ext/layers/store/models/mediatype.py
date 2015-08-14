from yowsup_ext.layers.store import db
import peewee

TYPE_IMAGE      = "image"
TYPE_AUDIO      = "audio"
TYPE_VIDEO      = "video"
TYPE_CONTACT    = "contact"
TYPE_LOCATION   = "location"

class MediaType(db.get_base_model()):
    type = peewee.CharField()

    def __unicode__(self):
        return self.type

    @classmethod
    def init(cls):
        cls.get_or_create(type=TYPE_IMAGE)
        cls.get_or_create(type=TYPE_AUDIO)
        cls.get_or_create(type=TYPE_VIDEO)
        cls.get_or_create(type=TYPE_CONTACT)
        cls.get_or_create(type=TYPE_LOCATION)

    @classmethod
    def get_image(cls):
        return cls.get_mediatype(TYPE_IMAGE)

    @classmethod
    def get_audio(cls):
        return cls.get_meditype(TYPE_AUDIO)

    @classmethod
    def get_video(cls):
        return cls.get_mediatype(TYPE_VIDEO)

    @classmethod
    def get_contact(cls):
        return cls.get_mediatype(TYPE_CONTACT)

    @classmethod
    def get_location(cls):
        return cls.get_mediatype(TYPE_LOCATION)

    @classmethod
    def get_mediatype(cls, name):
        return cls.get(cls.type==name)
