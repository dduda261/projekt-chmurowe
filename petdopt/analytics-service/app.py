import pika
import json

clicks = {}

def callback(ch, method, properties, body):
    data = json.loads(body)
    pet_name = data.get("pet_name")
    if pet_name:
        clicks[pet_name] = clicks.get(pet_name, 0) + 1
        print(f"[Analytics] {pet_name} clicked {clicks[pet_name]} times")

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue='pet_clicks')
    channel.basic_consume(queue='pet_clicks', on_message_callback=callback, auto_ack=True)
    print(" [*] Waiting for pet click events. To exit press CTRL+C")
    channel.start_consuming()

if __name__ == "__main__":
    main()
