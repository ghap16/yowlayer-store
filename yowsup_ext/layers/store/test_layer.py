import unittest
from yowsup.stacks.yowstack import YowStack
from yowsup.layers.protocol_messages.protocolentities import TextMessageProtocolEntity
from yowsup_ext.layers import YowStorageLayer


class YowStorageLayerTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(YowStorageLayerTest, self).__init__(*args, **kwargs)
        self.stack = YowStack([YowStorageLayer])
    #def test_reset(self):
    #    self.stack.getLayerInterface(YowStorageLayer).reset()

    def test_storeOutgoingTextMessages(self):
        from yowsup_ext.layers.store.models.messagestate import MessageState
        from yowsup_ext.layers.store.models.message import Message
        from yowsup_ext.layers.store.models.state import State
        msgContent = "Hello World"
        msgJid = "aaa@s.whatsapp.net"
        msg = TextMessageProtocolEntity(msgContent, to=msgJid)
        x = self.stack.send(msg)

        message = self.stack.getLayerInterface(YowStorageLayer).getMessages(msgJid, limit=1)[0]

        self.assertEqual(message.content, msgContent)
        self.assertEqual(message.conversation.contact.jid, msgJid)
        states = (State
            .select()
            .join(MessageState)
            .join(Message)
            .where(Message.id == message.id))

        self.assertEqual(states[0], State.get_sent_queued())
