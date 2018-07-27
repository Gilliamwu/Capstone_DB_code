from flask_sqlalchemy import SQLAlchemy
import datetime
db = SQLAlchemy()


# Session = sessionmaker(bind=engine)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username

class video_file_id_mapping(db.Model):
    _tablename__ = 'video_file_id_mapping'
    video_location = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    video_id = db.Column(db.Integer, unique=True)
    # TODO: maybe set id default to be the total length of the datavase
    def __init__(self, video_location):
        self.video_location = video_location

    def __repr__(self):
        return "<video_file(video_location='%s',video_id='%s')>" %(self.video_location,self.video_id)

class crack_detection_result(db.Model):
    __tablename__ = 'crack_detection_result'
    __table_args__ = (
        db.PrimaryKeyConstraint('video_id', 'frame_id'),
        {}
    )
    video_id = db.Column(db.Integer, db.ForeignKey("video_file_id_mapping.video_id"), nullable=False) # db.ForeignKey("video_file_id_mapping.video_id"),
    frame_id = db.Column(db.Integer)
    insert_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    frame_loc = db.Column(db.String(80), unique=True)
    detect_flag = db.Column(db.Boolean, nullable=True)
    result_loc = db.Column(db.String(80), unique=True, nullable=True)
    def __init__(self, video_id, frame_id, frame_loc,detect_flag=False,result_loc=None):
        self.video_id = video_id
        self.frame_id = frame_id
        self.frame_loc = frame_loc
        self.detect_flag = detect_flag
        self.result_loc = result_loc
    def __repr__(self):
        return '<video frame for {}, frame loc {}>'.format(self.video_id, self.frame_loc)

class video_processed_frame_info(db.Model):
    __tablename__ = "video_processed_frame_info"
    __table_args__ = (
        db.PrimaryKeyConstraint('video_id'),
    )
    video_id = db.Column(db.Integer, db.ForeignKey("video_file_id_mapping.video_id"), unique=True, nullable=False)
    total_frames = db.Column(db.Integer, default=0)
    processed_frames_n = db.Column(db.Integer, default=0)
    def __init__(self,video_id,total_frames,processed_frames_n=None):
        self.video_id = video_id
        self.total_frames = total_frames
        self.processed_frames_n = processed_frames_n

    def __repr__(self):
        return "<video_processed_frame_info(video_id='%s',total_frames='%s',processed_frames_n='%s')>"\
               % (self.video_id, self.total_frames, self.processed_frames_n)