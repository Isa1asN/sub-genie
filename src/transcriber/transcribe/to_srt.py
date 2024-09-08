import pika, tempfile, json, os
from bson.objectid import ObjectId
import pika.spec
from stt import STT

def start(message, fs_videos, fs_srts, channel):
    message = json.loads(message)

    stt = STT(model_size="tiny.en", device="cpu")
    temp_file = tempfile.NamedTemporaryFile()

    out = fs_videos.get(ObjectId(message["video_fid"]))

    temp_file.write(out.read())
    segments = stt.transcribe(input_file=temp_file.name)
    temp_file.close()

    srt_out = stt.get_srt(segments)

    temp_f_path = tempfile.gettempdir() + f"/{message['video_fid']}.srt"
    stt.write_srt_to_file(srt_dict=srt_out, srt_path=temp_f_path)

    f = open(temp_f_path, "rb")
    data = f.read()
    fid = fs_srts.put(data)
    f.close()
    os.remove(temp_f_path)

    message["srt_fid"] = str(fid)

    try:
        channel.basic_publish(
            exchange="",
            routing_key=os.environ.get("SRT_QUEUE"),
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                ),
        )
    except Exception as e:
        fs_srts.delete(fid)
        return "failed to publish message"





