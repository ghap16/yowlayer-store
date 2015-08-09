from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_messages.protocolentities import TextMessageProtocolEntity
from yowsup.common.tools import StorageTools
from layer_interface import StorageLayerInterface
import datetime
import peewee
import db
import logging

#
# StateModel = None
# MessageModel = None
# MessageStateModel = None
# # ConversationModel = None
# ContactModel = None
# GroupModel = None
# GroupContactModel = None
# MediaTypeModel = None
# MediaModel = None
# BroadcastModel = None
# BroadcastContactModel = None
# StatusModel = None
#
# Conversation = None


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

    def reset(self):
        self.db.drop_tables(Models)
        self.setup_models()

    def getMessages(self, jid, offset, limit):
        conversation = self.getConversation(jid)
        messages = Message.select()\
            .where(Message.conversation == conversation)\
            .order_by(Message.id)\
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
        Should store all incoming messages. Must afterwards send the entity to upper layers
        :param messageProtocolEntity:
        :return:
        '''
        message = self.storeMessage(messageProtocolEntity)
        self.toUpper(messageProtocolEntity)

    def storeMessage(self, messageProtocolEntity):
        if messageProtocolEntity.isOutgoing():
            conversation = self.getConversation(messageProtocolEntity.getTo())
        else:
            conversation = self.getConversation(messageProtocolEntity.getFrom())

        if messageProtocolEntity.getType() == TextMessageProtocolEntity.MESSAGE_TYPE_TEXT:
            return self.storeTextMessage(messageProtocolEntity, conversation)

    def storeTextMessage(self, textMessageProtocolEntity, conversation):
        message = Message(
            conversation = conversation,
            content = textMessageProtocolEntity.getBody(),
            t_sent = datetime.datetime.fromtimestamp(textMessageProtocolEntity.getTimestamp())
        )
        message.save()
        return message

    def send(self, protocolEntity):
        '''
        Store what should be stored from incoming data and then forward to lower layers
        :param protocolEntity:
        :return:
        '''

        if protocolEntity.__class__ == TextMessageProtocolEntity:
            message = self.storeMessage(protocolEntity)
            MessageState.set_sent_queued(message)

        self.toLower(protocolEntity)