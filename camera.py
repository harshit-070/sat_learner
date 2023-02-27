import cv2
from deepface import DeepFace
from app import db
from app.models import Normalizations


class Video(object):
    def __init__(self, data):
        self.video = cv2.VideoCapture(0)
        self.faceCascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self.a = 0
        self.d = 0
        self.f = 0
        self.h = 0
        self.s = 0
        self.sup = 0
        self.n = 0
        self.length = 0
        self.dic = {
            "angry": self.a,
            "disgust": self.d,
            "fear": self.f,
            "happy": self.h,
            "sad": self.s,
            "surprise": self.sup,
            "neutral": self.n,
        }
        self.normalization = 0
        self.user_id = data

    def __del__(self):
        self.video.release()

    def get_frame(
        self,
    ):
        ret, frame = self.video.read()
        result = DeepFace.analyze(frame, actions=["emotion"], enforce_detection=False)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face = self.faceCascade.detectMultiScale(gray, 1.1, 4)
        for (x, y, w, self.h) in face:
            cv2.rectangle(frame, (x, y), (x + w, y + self.h), (0, 255, 0), 2)

        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(
            frame,
            result["dominant_emotion"],
            (50, 50),
            font,
            3,
            (0, 0, 255),
            cv2.LINE_4,
        )

        if result["dominant_emotion"] == "angry":
            self.length = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
            self.a = self.a + 1
        elif result["dominant_emotion"] == "disgust":
            self.length = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
            self.d = self.d + 1
        elif result["dominant_emotion"] == "fear":
            self.length = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
            self.f = self.f + 1
        elif result["dominant_emotion"] == "happy":
            self.length = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
            self.h = self.h + 1
        elif result["dominant_emotion"] == "sad":
            self.length = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
            self.s = self.s + 1
        elif result["dominant_emotion"] == "surprise":
            self.length = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
            self.sup = self.sup + 1
        elif result["dominant_emotion"] == "neutral":
            self.length = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
            self.n = self.n + 1
        total = self.a + self.d + self.f + self.h + self.s + self.sup + self.n
        self.a = float(self.a * 0.1)
        self.d = float(self.d * 0.7)
        self.f = float(self.f * 0.3)
        self.h = float(self.h)
        self.s = float(self.s * 0.2)
        self.n = float(self.n)
        self.normalization = (
            self.a + self.d + self.f + self.h + self.s + self.n
        ) / total
        normalization = Normalizations.query.filter_by(user_id=self.user_id).first()
        if not normalization:
            normalization = Normalizations(
                user_id=self.user_id,
                current_question=1,
                normalization=0,
                previous_normalization=0,
            )
        if normalization.has_updated == 0:
            normalization.normalization += normalization.previous_normalization
            normalization.has_updated = 1
        normalization.previous_normalization = self.normalization
        db.session.add(normalization)
        db.session.commit()
        ret, jpg = cv2.imencode(".jpg", frame)
        return jpg.tobytes()
