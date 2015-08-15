import unittest
from yowsup.stacks.yowstack import YowStack
from yowsup.layers.protocol_messages.protocolentities import TextMessageProtocolEntity
from yowsup.layers.protocol_acks.protocolentities import IncomingAckProtocolEntity
from yowsup.layers.protocol_receipts.protocolentities import IncomingReceiptProtocolEntity, OutgoingReceiptProtocolEntity
from yowsup_ext.layers import YowStorageLayer
from yowsup.layers.protocol_contacts.protocolentities import ResultSyncIqProtocolEntity, GetSyncIqProtocolEntity
from yowsup.layers.protocol_media.protocolentities import *
import sys
import time

class YowStorageLayerTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(YowStorageLayerTest, self).__init__(*args, **kwargs)
        self.stack = YowStack([YowStorageLayer])
    #def test_reset(self):
    #    self.stack.getLayerInterface(YowStorageLayer).reset()
    #


    def sendMessage(self):
        msgContent = "Hello World"
        msgJid = "aaa@s.whatsapp.net"
        msg = TextMessageProtocolEntity(msgContent, to=msgJid)
        self.stack.send(msg)
        return msg

    def sendReceipt(self, message, read = False, participant = None):
        receipt = OutgoingReceiptProtocolEntity(message.getId(), message.getTo(), read)
        self.stack.send(receipt)
        return receipt

    def receiveMessage(self):
        msgContent = "Received message"
        msgJid = "bbb@s.whatsapp.net"
        msg = TextMessageProtocolEntity(msgContent, _from = msgJid)
        self.stack.receive(msg)
        return msg

    def receiveAck(self, message):
        ack = IncomingAckProtocolEntity(message.getId(), "message", message.getTo(), str(int(time.time())))
        self.stack.receive(ack)

    def test_incomingAck(self):
        from yowsup_ext.layers.store.models.state import State
        message = self.sendMessage()
        self.receiveAck(message)

        state = self.getMessageState(message.getId())
        self.assertEqual(state.name, State.get_sent().name)

    def test_incomingReceipt(self):
        from yowsup_ext.layers.store.models.state import State
        message = self.sendMessage()
        ack = self.receiveAck(message)

        receipt = IncomingReceiptProtocolEntity(message.getId(), message.getTo(), str(int(time.time())))
        self.stack.receive(receipt)

        state = self.getMessageState(message.getId())
        self.assertEqual(state.name, State.get_sent_delivered().name)

        receipt.type = "read"

        self.stack.receive(receipt)
        state = self.getMessageState(message.getId())
        self.assertEqual(state.name, State.get_sent_read().name)

    def test_incomingReceipt_multi(self):
        from yowsup_ext.layers.store.models.state import State

        messages = [self.sendMessage(), self.sendMessage(), self.sendMessage()]

        #get acks
        for message in messages:
            self.receiveAck(message)

        #get receipt
        receipt = IncomingReceiptProtocolEntity(str(time.time()), messages[0].getTo(),
            str(int(time.time())),
            items = [message.getId() for message in messages])

        self.stack.receive(receipt)

        # check
        for message in messages:
            state = self.getMessageState(message.getId())
            self.assertEqual(state.name, State.get_sent_delivered().name)


        receipt.type = "read"

        self.stack.receive(receipt)

        for message in messages:
            state = self.getMessageState(message.getId())
            self.assertEqual(state.name, State.get_sent_read().name)


    def getMessageState(self, messageGenId):
        from yowsup_ext.layers.store.models.messagestate import MessageState
        from yowsup_ext.layers.store.models.message import Message
        from yowsup_ext.layers.store.models.state import State

        message = self.stack.getLayerInterface(YowStorageLayer).getMessageByGenId(messageGenId)

        states = (State
            .select()
            .join(MessageState)
            .join(Message)
            .where(Message.id == message.id))

        return states[0]

    def test_storeOutgoingLocationMessage(self):
        from yowsup_ext.layers.store.models.message import Message
        locData = {
            "latitude": "LAT",
            "longitude": "LONG",
            "name": "name"
        }
        locationMessage = LocationMediaMessageProtocolEntity(
            locData["latitude"],locData["longitude"],locData["name"],
            "http://maps.google.com/", "raw", to="t@s.whatsapp.net", preview = "PREV"
        )
        self.stack.send(locationMessage)

        message = Message.get(id_gen = locationMessage.getId())

        self.assertEqual(message.content, locData["name"])
        self.assertEqual(message.media.data, ";".join((locData["latitude"], locData["longitude"])))


    def test_storeOutgoingTextMessages(self):
        from yowsup_ext.layers.store.models.state import State
        from yowsup_ext.layers.store.models.messagestate import MessageState
        from yowsup_ext.layers.store.models.message import Message
        msg = self.sendMessage()

        message = self.stack.getLayerInterface(YowStorageLayer).getMessages(msg.getTo(), limit=1)[0]

        self.assertEqual(message.content, msg.getBody())
        self.assertEqual(message.conversation.contact.jid, msg.getTo())
        states = (State
            .select()
            .join(MessageState)
            .join(Message)
            .where(Message.id == message.id))

        self.assertEqual(states[0], State.get_sent_queued())

    # def test_incomingMessageReceipts(self):
    #     from yowsup_ext.layers.store.models.state import State
    #     message = self.receiveMessage()
    #     self.sendReceipt(message)
    #
    #     state = self.getMessageState(message.getId())
    #
    #     self.assertEqual(state, State.get_received())
    #
    #     self.sendReceipt(message, True)
    #
    #     self.assertEqual(self.getMessageState(message.getId()), State.get_received_read())


    def test_storeIncomingTextMessage(self):
        from yowsup_ext.layers.store.models.messagestate import MessageState
        from yowsup_ext.layers.store.models.message import Message
        from yowsup_ext.layers.store.models.state import State

        msg = self.receiveMessage()

        message = Message.get(id_gen = msg.getId())

        self.assertEqual(message.content, msg.getBody())
        self.assertEqual(message.conversation.contact.jid, msg.getFrom())
        states = (State
            .select()
            .join(MessageState)
            .join(Message)
            .where(Message.id == message.id))

        self.assertEqual(states[0].name, State.get_received().name)

    def test_contactsSync(self):
        from yowsup_ext.layers.store.models.contact import Contact
        inNumbers = {
            "492743103668": "492743103668@s.whatsapp.net",
            "4915225256022": "4915225256022@s.whatsapp.net"
        }

        getSyncProtocolEntity = GetSyncIqProtocolEntity([inNumbers.keys()])
        self.stack.send(getSyncProtocolEntity)


        outNumbers = {}
        invalidNumbers = []
        resultSync = ResultSyncIqProtocolEntity(getSyncProtocolEntity.getId(), "1.2341", "0",
        True, "12345", inNumbers, outNumbers, invalidNumbers)
        self.stack.receive(resultSync)


        for number, jid  in inNumbers.items():
            Contact.get(jid = jid, number = number)
