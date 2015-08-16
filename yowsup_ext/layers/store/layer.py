from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_messages.protocolentities import MessageProtocolEntity, TextMessageProtocolEntity
from yowsup.layers.protocol_contacts.protocolentities import GetSyncIqProtocolEntity
from yowsup.layers.protocol_receipts.protocolentities import IncomingReceiptProtocolEntity
from yowsup.layers.protocol_media.protocolentities import MediaMessageProtocolEntity
from yowsup.common.tools import StorageTools
from layer_interface import StorageLayerInterface
import datetime
import peewee
import db
import logging
import sys

Models = State = Message = MessageState = Conversation = Contact = \
    Group= GroupContact = MediaType = Media = Broadcast = \
    BroadcastContact = Status = None


logger = logging.getLogger(__name__)
DB_NAME = StorageTools.constructPath("yow.db")

class YowStorageLayer(YowInterfaceLayer):
    def __init__(self):
        super(YowStorageLayer, self).__init__()
        self.interface = StorageLayerInterface(self)
        self.db = peewee.SqliteDatabase(DB_NAME, threadlocals=True)
        db.set_db(self.db)
        self.db.connect()
        self.setup_models()

    def setup_models(self):
        global             Models
        global             MessageState, GroupContact, BroadcastContact
        global             State, Message, Conversation, Contact, Group, MediaType, Media, Broadcast, Status
        from models import State, Message, Conversation, Contact, Group, MediaType, Media, Broadcast, Status
        from models.messagestate import MessageState
        from models.groupcontact import GroupContact
        from models.broadcastcontact import BroadcastContact
        Models = [
            State,
            Message,
            MessageState,
            Conversation,
            Contact,
            Group,
            GroupContact,
            MediaType,
            Media,
            Broadcast,
            BroadcastContact,
            Status
        ]
        logger.debug("setting up models")
        self.db.create_tables(Models, True)

        #init Models that require init to setup initial vals
        State.init()
        MediaType.init()

    def reset(self):
        self.db.drop_tables(Models)
        self.setup_models()

    def getMessages(self, jid, offset, limit):
        conversation = self.getConversation(jid)
        messages = Message.select()\
            .where(Message.conversation == conversation)\
            .order_by(Message.id.desc())\
            .limit(limit)\
            .offset(offset)
        return messages

    def isGroupJid(self, jid):
        return "-" in jid

    def getConversation(self, jid):
        if self.isGroupJid(jid):
            group = Group.get_or_create(jid = jid)
            conversation = Conversation.get_or_create(group = group)[0]
        else:
            contact = Contact.get_or_create(jid = jid)
            conversation = Conversation.get_or_create(contact = contact[0])[0]

        return conversation

    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):
        '''
        Should store alpl incoming messages. Must afterwards send the entity to upper layers
        :param messageProtocolEntity:
        :return:
        '''
        message = self.storeMessage(messageProtocolEntity)
        MessageState.set_received(message)
        self.toUpper(messageProtocolEntity)

    @ProtocolEntityCallback("ack")
    def onAck(self, incomingAckProtocolEntity):
        '''
        For when a server acks our outgoing message
        :param incomingAckProtocolEntity:
        :return:
        '''
        if incomingAckProtocolEntity.getClass() == "message":
            '''handle'''
            message = self.getMessageByGenId(incomingAckProtocolEntity.getId())
            MessageState.set_sent(message)

    @ProtocolEntityCallback("receipt")
    def onReceipt(self, receiptProtocolEntity):
        '''
        Update message status to delivered or read
        :param receiptProtocolEntity:
        :return:
        '''

        ids = [receiptProtocolEntity.getId()] if receiptProtocolEntity.items is None else receiptProtocolEntity.items

        for id_ in ids:
            message = self.getMessageByGenId(id_)
            if not receiptProtocolEntity.getType():
                MessageState.set_sent_delivered(message)
            elif receiptProtocolEntity.getType() == "read":
                contact = None
                if receiptProtocolEntity.getParticipant():
                    contact = Contact.get_or_create(jid = receiptProtocolEntity.getParticipant())
                MessageState.set_sent_read(message, contact)


    def getMessageByGenId(self, genId):
        return Message.get(Message.id_gen == genId)

    def storeMessage(self, messageProtocolEntity):
        if messageProtocolEntity.isOutgoing():
            conversation = self.getConversation(messageProtocolEntity.getTo())
        else:
            conversation = self.getConversation(messageProtocolEntity.getFrom())

        message = Message(
            id_gen = messageProtocolEntity.getId(),
            conversation = conversation,
            t_sent = datetime.datetime.fromtimestamp(messageProtocolEntity.getTimestamp())
        )

        if messageProtocolEntity.getType() == MessageProtocolEntity.MESSAGE_TYPE_MEDIA:
            media = self.getMedia(messageProtocolEntity, message)
            media.save()
            message.media = media
        else:
            message.content = messageProtocolEntity.getBody()

        message.save()
        return message

    def getMedia(self, mediaMessageProtocolEntity, message):
        media = Media(
            type=MediaType.get_mediatype(mediaMessageProtocolEntity.getMediaType()),
            preview=mediaMessageProtocolEntity.getPreview())
        if mediaMessageProtocolEntity.getMediaType() in (
            MediaMessageProtocolEntity.MEDIA_TYPE_IMAGE,
            MediaMessageProtocolEntity.MEDIA_TYPE_AUDIO,
            MediaMessageProtocolEntity.MEDIA_TYPE_VIDEO
        ):
            self.setDownloadableMediaData(mediaMessageProtocolEntity, media)

            if mediaMessageProtocolEntity.getMediaType() == MediaMessageProtocolEntity.MEDIA_TYPE_IMAGE:
                message.content = mediaMessageProtocolEntity.getCaption()
                media.encoding = mediaMessageProtocolEntity.encoding

        elif mediaMessageProtocolEntity.getMediaType() == MediaMessageProtocolEntity.MEDIA_TYPE_LOCATION:
            message.content = mediaMessageProtocolEntity.getLocationName()
            self.setLocationMediaData(mediaMessageProtocolEntity, media)
        elif mediaMessageProtocolEntity.getMediaType() == MediaMessageProtocolEntity.MEDIA_TYPE_VCARD:
            message.content = mediaMessageProtocolEntity.getName()
            self.setVCardMediaData(mediaMessageProtocolEntity, media)

        return media

    def setLocationMediaData(self, locationMediaMessageProtocolEntity, media):
        media.remote_url = locationMediaMessageProtocolEntity.getLocationURL()
        media.data = ";".join((locationMediaMessageProtocolEntity.getLatitude(), locationMediaMessageProtocolEntity.getLongitude()))
        media.encoding = locationMediaMessageProtocolEntity.encoding

    def setVCardMediaData(self, vcardMediaMessageProtocolEntity, media):
        media.data = vcardMediaMessageProtocolEntity.getCardData()

    def setDownloadableMediaData(self, downloadableMediaMessageProtocolEntity, media):
        media.size = downloadableMediaMessageProtocolEntity.getMediaSize()
        media.remote_url = downloadableMediaMessageProtocolEntity.getMediaUrl()
        media.mimetype = downloadableMediaMessageProtocolEntity.getMimeType()
        media.filehash = downloadableMediaMessageProtocolEntity.fileHash
        media.filename = downloadableMediaMessageProtocolEntity.fileName

    def storeContactsSyncResult(self, resultSyncIqProtocolEntity, originalGetSyncProtocolEntity):
        for number, jid in resultSyncIqProtocolEntity.inNumbers.items():
            Contact.get_or_create(number = number, jid = jid)

        self.toUpper(resultSyncIqProtocolEntity)

    def send(self, protocolEntity):
        '''
        Store what should be stored from incoming data and then forward to lower layers
        :param protocolEntity:
        :return:
        '''

        if isinstance(protocolEntity, MessageProtocolEntity):
            message = self.storeMessage(protocolEntity)
            MessageState.set_sent_queued(message)
        elif protocolEntity.__class__ == GetSyncIqProtocolEntity:
            self._sendIq(protocolEntity, self.storeContactsSyncResult)
        elif protocolEntity.__class__ == "receipt":
            #@@TODO intercept
            pass

        self.toLower(protocolEntity)
