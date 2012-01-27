__author__ = 'kivsiak@gmail.com'

import pickle
import threading
import  amfast
from amfast.remoting import memcache_manager
from amfast.remoting.channel import ChannelSet
from amfast.remoting.connection import Connection, ConnectionError
from amfast.remoting.connection_manager import ConnectionManager, NotConnectedError, SessionAttrError
from amfast.remoting.wsgi_channel import WsgiChannel, WsgiChannelSet
import gevent
import amfast.remoting.flex_messages as messaging
import time

class StreamingGeventChannel(WsgiChannel):
    """WsgiChannel that opens a persistent connection with the client to serve messages."""

    def __init__(self, name, max_connections=-1, endpoint=None, wait_interval=0, heart_interval=30000):
        WsgiChannel.__init__(self, name, max_connections=max_connections,
            endpoint=endpoint, wait_interval=wait_interval)

        self.heart_interval = heart_interval

    def __call__(self, environ, start_response):

        if environ['CONTENT_TYPE'] == self.CONTENT_TYPE:
            # Regular AMF message
            return WsgiChannel.__call__(self, environ, start_response)

        # Create streaming message command
        try:
            msg = messaging.StreamingMessage()
            msg.parseParams(environ['QUERY_STRING'])

            body = environ['wsgi.input'].read(int(environ['CONTENT_LENGTH']))
            msg.parseBody(body)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception, exc:
            amfast.log_exc(exc)
            return self.badServer(start_response, self.getBadServerMsg())

        if msg.operation == msg.OPEN_COMMAND:
            return self.startStream(environ, start_response, msg)

        if msg.operation == msg.CLOSE_COMMAND:
            return self.stopStream(msg)

        return self.badRequest(start_response, self.getBadRequestMsg('Streaming operation unknown: %s' % msg.operation))

    def startStream(self, environ, start_response, msg):
        """Start streaming response."""

        try:
            connection = self.channel_set.connection_manager.getConnection(msg.headers.get(msg.FLEX_CLIENT_ID_HEADER))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception, exc:
            amfast.log_exc(exc)
            return self.badServer(start_response, self.getBadServerMsg())

        write = start_response('200 OK', [
            ('Content-Type', self.CONTENT_TYPE)
        ])

        try:
            # Send acknowledge message
            response = msg.acknowledge()
            response.body = connection.id

            try:
                bytes = messaging.StreamingMessage.prepareMsg(response, self.endpoint)
                write(bytes)

                write(chr(messaging.StreamingMessage.NULL_BYTE) * self.KICKSTART_BYTES)

            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception, exc:
                amfast.log_exc(exc)
                return []

            # Start heart beat
            timer = threading.Timer(float(self.heart_interval) / 1000, self.beat, (connection, ))
            timer.daemon = True
            timer.start()

            # Wait for new messages.
            event = gevent.event.Event()
            connection.setNotifyFunc(event.set)
            poll_secs = float(self.poll_interval) / 1000
            while True:

                if connection.connected is False:
                    # Connection is no longer active
                    msg = messaging.StreamingMessage.getDisconnectMsg()
                    try:
                        write(messaging.StreamingMessage.prepareMsg(msg, self.endpoint))
                    except:
                        # Client may have already disconnected
                        pass
                        # Stop stream
                    return []

                if self.channel_set.notify_connections is True:
                # Block until notification of new message
                    event.wait()
                else:
                    # Block until poll_interval is reached
                    event.wait(poll_secs)

                # Message has been published,
                # or it's time for a heart beat

                # Remove notify_func so that
                # New messages don't trigger event.
                connection.unSetNotifyFunc()

                msgs = self.channel_set.subscription_manager.pollConnection(connection)
                if len(msgs) > 0:
                    while len(msgs) > 0:
                        # Dispatch all messages to client
                        for msg in msgs:
                            try:
                                bytes = messaging.StreamingMessage.prepareMsg(msg, self.endpoint)
                            except (KeyboardInterrupt, SystemExit):
                                raise
                            except Exception, exc:
                                amfast.log_exc(exc)
                                self.channel_set.disconnect(connection)
                                break

                            try:
                                write(bytes)
                            except (KeyboardInterrupt, SystemExit):
                                raise
                            except:
                                # Client has disconnected
                                self.channel_set.disconnect(connection)
                                return []

                        msgs = self.channel_set.subscription_manager.pollConnection(connection)
                else:
                    # Send heart beat
                    try:
                        write(chr(messaging.StreamingMessage.NULL_BYTE))
                    except (KeyboardInterrupt, SystemExit):
                        raise
                    except:
                        # Client has disconnected
                        self.channel_set.disconnect(connection)
                        return []

                # Create new event to trigger new messages or heart beats
                event = gevent.event.Event()
                connection.setNotifyFunc(event.set)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception, exc:
            amfast.log_exc(exc)
            self.channel_set.disconnect(connection)
            return []

    def beat(self, connection):
        """Send a heart beat."""
        if hasattr(connection, "notify_func") and connection.notify_func is not None:
            connection.notify_func()
        else:
            return

        # Create timer for next beat
        timer = threading.Timer(float(self.heart_interval) / 1000, self.beat, (connection, ))
        timer.daemon = True
        timer.start()

    def stopStream(self, msg):
        """Stop a streaming connection."""
        connection = self.channel_set.connection_manager.getConnection(msg.headers.get(msg.FLEX_CLIENT_ID_HEADER))
        connection.disconnect()
        if hasattr(connection, "notify_func") and connection.notify_func is not None:
            connection.notify_func()
        return []



class SecureChannelSet(WsgiChannelSet):
    def checkCredentials(self, user, password):
        return True