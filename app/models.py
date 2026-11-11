from sqlalchemy.dialects.postgresql import JSONB

from app.database import db


class Chapter(db.Model):
    __tablename__ = "chapters"

    chapter = db.Column(db.Text, primary_key=True)
    audio = db.Column(db.Text, nullable=True)
    image = db.Column(db.Text, nullable=True)
    speech = db.Column(db.Text, nullable=True)
    title = db.Column(db.Text, nullable=True)
    intro = db.Column(db.Text, nullable=True)
    pronunciation = db.Column(JSONB, nullable=False, default=list)
    pronunciation_intro = db.Column(db.Text, nullable=True)
    reading = db.Column(db.Text, nullable=True)
    reading_intro = db.Column(db.Text, nullable=True)
    vocabulary = db.Column(JSONB, nullable=True)
    vocabulary_intro = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "chapter": self.chapter,
            "audio": self.audio,
            "image": self.image,
            "speech": self.speech,
            "title": self.title,
            "intro": self.intro,
            "pronunciation": self.pronunciation,
            "pronunciationIntro": self.pronunciation_intro,
            "reading": self.reading,
            "readingIntro": self.reading_intro,
            "vocabulary": self.vocabulary,
            "vocabularyIntro": self.vocabulary_intro,
        }