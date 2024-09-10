import os, gridfs, pika, json, sys
from flask import Flask, request, send_file
from flask_pymongo import PyMongo
from auth_ import validate
from auth_svc import access
from storage import util
from bson.objectid import ObjectId
import logging

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


server = Flask(__name__)

server.logger.setLevel(logging.DEBUG)

mongo_video = PyMongo(
    server,
    uri="mongodb://host.docker.internal:27017/videos"
    )

mongo_srt = PyMongo(
    server,
    uri="mongodb://host.docker.internal:27017/srts"
    )

fs_videos = gridfs.GridFS(mongo_video.db)
fs_srts = gridfs.GridFS(mongo_srt.db)

connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()

@server.route("/register", methods=["POST"])
def register():
    resp, err = access.register(request)

    if not err:
        return resp
    else:
        return err

@server.route("/login", methods=["POST"])
def login():
    token, err = access.login(request)

    if not err:
        return token
    else:
        return err
    
@server.route("/upload", methods=["POST"])
def upload():
    access, err = validate.token(request)

    if err:
        return err
    
    access = json.loads(access)
    
    if access["admin"]:
        if len(request.files) > 1 or len(request.files) < 1:
            return "exactly 1 file required", 400
        
        for _, f in request.files.items():
            err = util.upload(f, fs_videos, channel, access)

            if err:
                return err
        return "success!", 200
    else:
        return "unauthorized", 401

@server.route("/download", methods=["GET"])
def download():
    access, err = validate.token(request)

    if err:
        return err
    
    access = json.loads(access)

    if access["admin"]:
        fid_string = request.args.get("fid")
        if not fid_string:
            return "fid is required", 400
        
        try:
            out = fs_srts.get(ObjectId(fid_string))
            return send_file(out, download_name=f'{fid_string}.srt')
        except Exception as e:
            print(e)
            return "Internal server error", 500
    
    return "unauthorized", 401

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080, debug=True)
