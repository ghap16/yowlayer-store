from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_messages.protocolentities import MessageProtocolEntity, TextMessageProtocolEntity
from yowsup.layers.protocol_contacts.protocolentities import GetSyncIqProtocolEntity
from yowsup.layers.protocol_receipts.protocolentities import IncomingReceiptProtocolEntity, OutgoingReceiptProtocolEntity
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

class YowStorageLayer(YowInterfaceLayer):
    PROP_DB_PATH = "org.openwhatsapp.yowsup.prop.store.db"
    def __init__(self):
        super(YowStorageLayer, self).__init__()
        self.interface = StorageLayerInterface(self)

    def setStack(self, stack):
        super(YowStorageLayer, self).setStack(stack)
        self.db = peewee.SqliteDatabase(self.getProp(self.__class__.PROP_DB_PATH, StorageTools.constructPath("yow.db")), threadlocals=True)
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

    def getContacts(self):
        return Contact.select()

    def addContact(self, jidOrNumber):
        if '@' in jidOrNumber:
            number = jidOrNumber.split('@')[0]
            contact = Contact.get_or_create(jid = jidOrNumber, number = number)[0]
        else:
            jid = jidOrNumber + '@s.whatsapp.net'
            contact = Contact.get_or_create(jid = jid, number = jidOrNumber)[0]

        return contact

    def getContact(self, jidOrNumber):
        try:
            if '@' in jidOrNumber:
                return Contact.get(Contact.jid == jidOrNumber)

            return Contact.get(Contact.number == jidOrNumber)
        except peewee.DoesNotExist:
            return None

    def isContact(self, jidOrNumber):
        return self.getContact(jidOrNumber) is not None

    def getMessages(self, jid, offset, limit):
        conversation = self.getConversation(jid)
        messages = Message.select()\
            .where(Message.conversation == conversation)\
            .order_by(Message.id.desc())\
            .limit(limit)\
            .offset(offset)
        return messages

    def _getJid(self, jidOrNumber):
        return jidOrNumber if '@' in jidOrNumber else jidOrNumber + "@s.whatsapp.net"

    def getUnreadReceivedMessages(self, jidOrNumber):
        jid = self._getJid(jidOrNumber)
        conversation = self.getConversation(jid)
        messages = Message.getByState([State.get_received_remote()], conversation)

        return messages

    def getUnackedReceivedMessages(self, jidOrNumber = None):
        if jidOrNumber:
            jid = self._getJid(jidOrNumber)
            conversation = self.getConversation(jid)
        else:
            conversation = None

        return Message.getByState([State.get_received()], conversation)

    def getUnackedSentMessages(self, jidOrNumber = None):
        if jidOrNumber:
            jid = self._getJid(jidOrNumber)
            conversation = self.getConversation(jid)
        else:
            conversation = None

        return Message.getByState([State.get_sent_queued()], conversation)

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
    def onAck(self, incomingAckProtocolEntity, OutgoingReceiptProtocolEntity = None):
        from models import state
        if incomingAckProtocolEntity.getClass() == "message":
            message = self.getMessageByGenId(incomingAckProtocolEntity.getId())
            MessageState.set_sent(message)

        self.toUpper(incomingAckProtocolEntity)

    @ProtocolEntityCallback("success")
    def onAuthed(self, successProtocolEntity):
        #send pending receipts
        messages = self.getUnackedReceivedMessages()
        if messages.count():
            self.sendReceipts(messages)

        #send offline messages
        # messages = self.getUnackedSentMessages()
        # for message in messages:
        #     if message.media:
        #         #handle Media
        #         pass
        #     else:
        #         '''
        #         (self, body, _id = None,  _from = None, to = None, notify = None,
        # timestamp = None, participant = None, offline = None, retry = None)
        #         '''
        #         jid = message.group.jid if message.group is not None else message.contact.jid
        #         textMessagePE = TextMessageProtocolEntity(message.content, message.id_gen, to = jid, timestamp)


        self.toUpper(successProtocolEntity)

    def sendReceipts(self, messageList, read = False):
        receipts = {}
        for m in messageList:
            conversation = m.conversation
            if conversation.contact is not None:
                jid = conversation.contact.jid
            elif conversation.group is not None:
                jid = conversation.group.jid
            else:
                continue

            if jid not in receipts:
                receipts[jid] = []
            receipts[jid].append(m.id_gen)

        for jid, messageIds in receipts.items():
            receipt = OutgoingReceiptProtocolEntity(messageIds, jid, read=read)

            self.sendReceipt(receipt)

    def sendReceipt(self, outgoingReceiptProtocolEntity):
        for messageId in outgoingReceiptProtocolEntity.getMessageIds():
            try:
                message = Message.get(id_gen = messageId)
                if outgoingReceiptProtocolEntity.read:
                    MessageState.set_received_read_remote(message)
                else:
                    MessageState.set_received_remote(message)

            except peewee.DoesNotExist:
                logger.warning("Sending receipt for non existent message in storage. Id: %s" % messageId)

        self.toLower(outgoingReceiptProtocolEntity)


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
            if message:
                if not receiptProtocolEntity.getType():
                    MessageState.set_sent_delivered(message)
                elif receiptProtocolEntity.getType() == "read":
                    contact = None
                    if receiptProtocolEntity.getParticipant():
                        contact = Contact.get_or_create(jid = receiptProtocolEntity.getParticipant())
                    MessageState.set_sent_read(message, contact)

        self.toUpper(receiptProtocolEntity)


    def getMessageByGenId(self, genId):
        try:
            return Message.get(Message.id_gen == genId)
        except peewee.DoesNotExist:
            logger.warning("Message with id %s does not exist" % genId)
            return None

    def storeMessage(self, messageProtocolEntity):
        if messageProtocolEntity.isOutgoing():
            conversation = self.getConversation(messageProtocolEntity.getTo())
        else:
            conversation = self.getConversation(messageProtocolEntity.getFrom())

        if messageProtocolEntity.isOutgoing():
            messageGenId = messageProtocolEntity.getId()
            try:
                while True:
                    Message.get(id_gen = messageGenId)
                    messageIdDis = messageGenId.split('-')
                    if len(messageGenIdDis) == 2:
                        messageIdCount = int(messageIdDis[1]) + 1
                    else:
                        messageIdCount = 1
                    messageGenId = "%s-%s" % (messageIdDis[0], messageIdCount)
            except peewee.DoesNotExist:
                pass

            messageProtocolEntity._id = messageGenId
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

        if type(message.content) is bytearray:
            message.content = message.content.decode('latin-1')

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

            media.encoding = mediaMessageProtocolEntity.encoding
            if mediaMessageProtocolEntity.getMediaType() != MediaMessageProtocolEntity.MEDIA_TYPE_AUDIO:
                message.content = mediaMessageProtocolEntity.getCaption()

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

        if protocolEntity.__class__ == GetSyncIqProtocolEntity:
            self._sendIq(protocolEntity, self.storeContactsSyncResult)
        elif protocolEntity.__class__ == OutgoingReceiptProtocolEntity:
            if protocolEntity.read:
                for messageId in protocolEntity.getMessageIds():
                    try:
                        message = Message.get(id_gen = messageId)
                        MessageState.set_received_read(message)
                    except peewee.DoesNotExist:
                        continue
            self.sendReceipt(protocolEntity)
        # elif protocolEntity.__class__ == ListOutgoingReceiptProtocolEntity:
        #     if protocolEntity.read:
        #         for mId in protocolEntity.getMessageIds():
        #             message = Message.get(id_gen = mId)
        #             MessageState.set_received_read(message)
        #     self.sendReceipt(protocolEntity)
        else:
            if isinstance(protocolEntity, MessageProtocolEntity):
                message = self.storeMessage(protocolEntity)
                MessageState.set_sent_queued(message)
            self.toLower(protocolEntity)
