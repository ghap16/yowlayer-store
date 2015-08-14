import unittest
from yowsup.stacks.yowstack import YowStack
from yowsup.layers.protocol_messages.protocolentities import TextMessageProtocolEntity
from yowsup.layers.protocol_acks.protocolentities import IncomingAckProtocolEntity
from yowsup.layers.protocol_receipts.protocolentities import IncomingReceiptProtocolEntity
from yowsup_ext.layers import YowStorageLayer
from yowsup.layers.protocol_contacts.protocolentities import ResultSyncIqProtocolEntity, GetSyncIqProtocolEntity
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

    def test_storeOutgoingTextMessages(self):
        from yowsup_ext.layers.store.models.messagestate import MessageState
        from yowsup_ext.layers.store.models.message import Message
        from yowsup_ext.layers.store.models.state import State
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

    def test_storeIncomingTextMessage(self):
        from yowsup_ext.layers.store.models.messagestate import MessageState
        from yowsup_ext.layers.store.models.message import Message
        from yowsup_ext.layers.store.models.state import State

        msgContent = "INCOMING HELLO WORLD"
        msgJid = "aaa@s.whatsapp.net"
        timestamp = int(time.time())
        notify = "aaa"
        offline = False
        id_ = "message_id"

        msg = TextMessageProtocolEntity(msgContent, _id=id_, offline=offline, notify=notify, _from=msgJid, timestamp=timestamp)
        self.stack.receive(msg)

        message = self.stack.getLayerInterface(YowStorageLayer).getMessages(msgJid, limit=1)[0]

        self.assertEqual(message.content, msgContent)
        self.assertEqual(message.conversation.contact.jid, msgJid)
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
