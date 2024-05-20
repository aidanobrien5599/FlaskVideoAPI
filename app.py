from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with

app = Flask(__name__)
api = Api(app) #wrapping our app in an API object
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class VideoDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #has to always have a name, max of 100 characgers
    name = db.Column(db.String(100), nullable=False)
    views = db.Column(db.Integer, nullable=False)
    likes = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
         return f"Video(name={self.name}, views={self.views}, likes={self.likes})"
    


#automatically parses through the request that is sent
video_put_args = reqparse.RequestParser()
#these need to be sent through the request
#help is the error message if the arg is not sent
video_put_args.add_argument("name", type=str, help="Name of the video is required", required=True)
video_put_args.add_argument("views", type=int, help="Views of the video is required", required=True)
video_put_args.add_argument("likes", type=int, help="Likes of the video is required", required=True)

#these are the same except they are patched
video_patch_args = reqparse.RequestParser()
video_put_args.add_argument("name", type=str, help="Name of the video")
video_put_args.add_argument("views", type=int, help="Views of the video")
video_put_args.add_argument("likes", type=int, help="Likes of the video")

videos = {}

#this will prevent the swever from crashing if an invald ID is sent
def abort_if_video_id_doesnt_exist(video_id):
    if video_id not in videos:
        #need to have status code
        abort(404, message="Video id is not valid..")
        
def abort_if_video_id_exists(video_id):
    if video_id in videos:
        #need to have status code 409 means object exists
        abort(409, message="Video already exists with that ID.")

resource_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'views': fields.Integer,
    'likes': fields.Integer 
}

#making a class that is a resource
#this resource will have a few methods that we can override
class Video(Resource):
    
    #to return something
    #marshal_with serializes the response with the resource_fields
    @marshal_with(resource_fields)
    def get(self, video_id):
        result = VideoDB.query.filter_by(id=video_id).first()
        ##catches case where video_id doesnt exist
        if not result:
            abort(404, message="Coulsnt find video with that ID")
        return result
        
    #creating a new video
    @marshal_with(resource_fields)
    def put(self, video_id):
        #try catch in case of bad data input or duplicate id
        try:
            args = video_put_args.parse_args()
            #make sure we dont create two videos with the same ID
            video = VideoDB(id=video_id, name=args['name'], views=args['views'], likes = args['likes'])
            db.session.add(video)
            db.session.commit()
            #return 201, which is a code that means it was created
            return video, 201
        except Exception:
            #make sure to abort the request
            abort(409, message="Video id taken...")
            print("Something went wrong")
    
    def delete(self, video_id):
        video = VideoDB.query.filter_by(id=video_id).first()
        ##catches case where video_id doesnt exist
        if not video:
            abort(404, message="Coulsnt find video with that ID")
        db.session.delete(video)
        db.session.commit()
        #return 204, which means deleted successfully
        return '', 204
    
    @marshal_with(resource_fields)
    def patch(self, video_id):
        args = video_patch_args.parse_args()
        
        result = VideoDB.query.filter_by(id=video_id).first()
        if not result:
            abort(404, message="Coulsnt find video with that ID")
        for key, value in args.items():
            if value is not None:
                setattr(result, key, value)
        db.session.commit()
        return result, 200
        

#registering it as a resource in the API
#wants the user to send some string after hello world
api.add_resource(Video, "/video/<int:video_id>")

if __name__ == '__main__':
    app.run(debug=True)