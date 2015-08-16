from yowsup_ext.layers.store import db
from yowsup.layers.protocol_media.protocolentities import MediaMessageProtocolEntity
import peewee

TYPE_IMAGE      = MediaMessageProtocolEntity.MEDIA_TYPE_IMAGE
TYPE_AUDIO      = MediaMessageProtocolEntity.MEDIA_TYPE_AUDIO
TYPE_VIDEO      = MediaMessageProtocolEntity.MEDIA_TYPE_VIDEO
TYPE_VCARD      = MediaMessageProtocolEntity.MEDIA_TYPE_VCARD
TYPE_LOCATION   = MediaMessageProtocolEntity.MEDIA_TYPE_LOCATION

class MediaType(db.get_base_model()):
    name = peewee.CharField()

    def __unicode__(self):
        return self.name

    @classmethod
    def init(cls):
        cls.get_or_create(name=TYPE_IMAGE)
        cls.get_or_create(name=TYPE_AUDIO)
        cls.get_or_create(name=TYPE_VIDEO)
        cls.get_or_create(name=TYPE_VCARD)
        cls.get_or_create(name=TYPE_LOCATION)

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
    def get_vcard(cls):
        return cls.get_mediatype(TYPE_VCARD)

    @classmethod
    def get_location(cls):
        return cls.get_mediatype(TYPE_LOCATION)

    @classmethod
    def get_mediatype(cls, name):
        return cls.get(cls.name==name)
