import pika, json

def upload(f, fs, channel, access):
    try:
        fid = fs.put(f)
        print(f"File uploaded successfully with id: {fid}")
    except Exception as e:
        print(f"Error during file upload to GridFS: {e}")
        return "Internal Server Error", 500
    
    print("access: ", access)
    
    message = {
        "video_fid": str(fid),
        "srt_fid": None,
        "username": access["username"],
    }
    print(f"Prepared RabbitMQ message: {message}")

    try:
        channel.basic_publish(
            exchange="", 
            routing_key="video", 
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )
        print("Message successfully published to RabbitMQ")
    except Exception as e:
        print(f"Error during message publishing to RabbitMQ: {e}")
        fs.delete(fid)
        return "Internal Server Error", 500
    


