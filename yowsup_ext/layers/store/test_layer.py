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
        msgContent = "Hello World"
        msgJid = "aaa@s.whatsapp.net"
        msg = TextMessageProtocolEntity(msgContent, to=msgJid)
        x = self.stack.send(msg)

        message = self.stack.getLayerInterface(YowStorageLayer).getMessages(msgJid, limit=1)[0]

        self.assertEqual(message.content, msgContent)
        self.assertEqual(message.conversation.contact.jid, msgJid)
        # self.assertEqual(message.sta)
        #print(message.state)