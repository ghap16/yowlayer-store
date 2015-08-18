import unittest
from yowsup.stacks.yowstack import YowStack
from yowsup.layers.protocol_messages.protocolentities import TextMessageProtocolEntity
from yowsup.layers.protocol_acks.protocolentities import IncomingAckProtocolEntity
from yowsup.layers.protocol_receipts.protocolentities import IncomingReceiptProtocolEntity, OutgoingReceiptProtocolEntity
from yowsup_ext.layers.store.layer import YowStorageLayer
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
            "name": "name",
            "url": "URL",
            "encoding": "raw"
        }
        locationMessage = LocationMediaMessageProtocolEntity(
            locData["latitude"],locData["longitude"],locData["name"],
            locData["url"], locData["encoding"], to="t@s.whatsapp.net", preview = "PREV"
        )
        self.stack.send(locationMessage)

        message = Message.get(id_gen = locationMessage.getId())

        self.assertEqual(message.content, locData["name"])
        self.assertEqual(message.media.data, ";".join((locData["latitude"], locData["longitude"])))
        self.assertEqual(str(message.media.preview), "PREV")
        self.assertEqual(message.media.remote_url, locData["url"])
        self.assertEqual(message.media.encoding, locData["encoding"])


    def test_storeOutgoingVCardMessage(self):
        from yowsup_ext.layers.store.models.message import Message
        vcardData = {
            "name": "NAME",
            "data": "VCARD_DATA"
        }
        vcardMessageEntity = VCardMediaMessageProtocolEntity(vcardData["name"], vcardData["data"], to="t@s.whatsapp.net")
        self.stack.send(vcardMessageEntity)

        message = Message.get(id_gen = vcardMessageEntity.getId())

        self.assertEqual(message.content, vcardData["name"])
        self.assertEqual(message.media.data, vcardData["data"])

    def test_storeOutgoingImageMessage(self):
        from yowsup_ext.layers.store.models.message import Message
        mediaData = {
            "mimetype": "image/jpeg",
            "filehash": "fhash",
            "url": "http:/google.com",
            "ip": "ip",
            "size": 1234,
            "file": "filename",
            "encoding": "raw",
            "height": 123,
            "width": 321,
            "preview": "PREV",
            "caption": "CAPTN"
        }

        messageEntity = ImageDownloadableMediaMessageProtocolEntity(
            mediaData["mimetype"],
            mediaData["filehash"],
            mediaData["url"],
            mediaData["ip"],
            mediaData["size"],
            mediaData["file"],
            mediaData["encoding"],
            mediaData["width"],
            mediaData["height"],
            mediaData["caption"],
            to = "t@s.whatsapp.net"
        )

        self.stack.send(messageEntity)

        message = Message.get(id_gen = messageEntity.getId())

        self.assertEqual(message.content, mediaData["caption"])
        self.assertEqual(message.media.encoding, mediaData["encoding"])
        self.assertEqual(message.media.filehash, mediaData["filehash"])
        self.assertEqual(message.media.mimetype, mediaData["mimetype"])
        self.assertEqual(message.media.filename, mediaData["file"])
        self.assertEqual(message.media.remote_url, mediaData["url"])


    def test_storeOutgoingAudioMessage(self):
            from yowsup_ext.layers.store.models.message import Message
            mediaData = {
                "mimetype": "image/jpeg",
                "filehash": "fhash",
                "url": "http:/google.com",
                "ip": "ip",
                "size": 1234,
                "file": "filename",
                "encoding": "raw",
                "abitrate": "bitrate",
                "acodec": "code"
            }

            messageEntity = AudioDownloadableMediaMessageProtocolEntity(
                mediaData["mimetype"],
                mediaData["filehash"],
                mediaData["url"],
                mediaData["ip"],
                mediaData["size"],
                mediaData["file"],
                None,
                None,
                None,
                None,
                mediaData["encoding"],
                None,
                None,
                to = "t@s.whatsapp.net"
            )

            self.stack.send(messageEntity)

            message = Message.get(id_gen = messageEntity.getId())

            self.assertEqual(message.media.encoding, mediaData["encoding"])
            self.assertEqual(message.media.filehash, mediaData["filehash"])
            self.assertEqual(message.media.mimetype, mediaData["mimetype"])
            self.assertEqual(message.media.filename, mediaData["file"])
            self.assertEqual(message.media.remote_url, mediaData["url"])

    def test_storeOutgoingVideoMessage(self):
            from yowsup_ext.layers.store.models.message import Message
            mediaData = {
                "mimetype": "image/jpeg",
                "filehash": "fhash",
                "url": "http:/google.com",
                "ip": "ip",
                "size": 1234,
                "file": "filename",
                "encoding": "raw",
                "abitrate": "bitrate",
                "acodec": "code",
                "caption": "CAPT"
            }

            messageEntity = VideoDownloadableMediaMessageProtocolEntity(
                mediaData["mimetype"],
                mediaData["filehash"],
                mediaData["url"],
                mediaData["ip"],
                mediaData["size"],
                mediaData["file"],
                None,
                None,
                None,
                None,
                None,
                mediaData["encoding"],
                None,
                None,
                None,
                None,
                None,
                None,
                mediaData["caption"],
                to = "t@s.whatsapp.net"
            )

            self.stack.send(messageEntity)

            message = Message.get(id_gen = messageEntity.getId())

            self.assertEqual(message.content, mediaData["caption"])
            self.assertEqual(message.media.encoding, mediaData["encoding"])
            self.assertEqual(message.media.filehash, mediaData["filehash"])
            self.assertEqual(message.media.mimetype, mediaData["mimetype"])
            self.assertEqual(message.media.filename, mediaData["file"])
            self.assertEqual(message.media.remote_url, mediaData["url"])

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
        self.sendReceipt(msg)

        message = Message.get(id_gen = msg.getId())

        self.assertEqual(message.content, msg.getBody())
        self.assertEqual(message.conversation.contact.jid, msg.getFrom())
        states = (State
            .select()
            .join(MessageState)
            .join(Message)
            .where(Message.id == message.id))

        self.assertEqual(states[0].name, State.get_received_remote().name)
        self.sendReceipt(msg, read=True)

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

        interface = self.stack.getLayerInterface(YowStorageLayer)


        # get by number
        contact = interface.getContact(inNumbers.keys()[0])
        self.assertTrue(contact is not None)
        self.assertEqual(contact["jid"], inNumbers[inNumbers.keys()[0]])

        # get by jid
        phone = inNumbers.keys()[1]
        jid = inNumbers[inNumbers.keys()[1]]
        contact = interface.getContact(jid)
        self.assertTrue(contact is not None)
        self.assertEqual(contact["number"], phone)

    def test_getUnreadMessages(self):
        message1 = self.receiveMessage()
        message2 = self.receiveMessage()

        self.sendReceipt(message1)
        self.sendReceipt(message2)

        iface = self.stack.getLayerInterface(YowStorageLayer)
        unreadIds = [m["id"] for m in iface.getUnreadReceivedMessages(message1.getFrom())]


        self.assertEqual(len(unreadIds), 2)
        self.assertTrue(message1.getId() in unreadIds)
        self.assertTrue(message2.getId() in unreadIds)

        self.sendReceipt(message1, True)
        self.sendReceipt(message2, True)
