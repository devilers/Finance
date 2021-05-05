import pika


class AMQP:
    def __init__(self):
        self.channel = None
        self.param = None
        self.connection = None

    def connect(self):
        self.param = pika.ConnectionParameters(host='localhost')
        self.connection = pika.BlockingConnection(self.param)
        self.channel = self.connection.channel()

    def publish(self, exch, key, msg):
        self.channel.exchange_declare(
            exchange=exch, exchange_type='direct', durable=True)

        self.channel.basic_publish(exchange=exch, routing_key=key,
                                   body=msg, properties=pika.BasicProperties(delivery_mode=2, expiration='300000'))

    def consume(self, exch, queue, key, callback):
        self.channel.queue_declare(queue=queue, durable=True
                                   )
        self.channel.queue_bind(queue=queue, exchange=exch, routing_key=key)
        self.channel.basic_consume(
            queue=queue, on_message_callback=callback)
        self.channel.start_consuming()
