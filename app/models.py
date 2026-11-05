from sqlalchemy.dialects.postgresql import JSONB

from app.database import db


class Chapter(db.Model):
    __tablename__ = "chapters"

    chapter = db.Column(db.Text, primary_key=True)
    category = db.Column(db.Text, primary_key=True)
    audio_url = db.Column(db.Text, nullable=True)
    image = db.Column(db.Text, nullable=True)
    character_presentation = db.Column(db.Text, nullable=True)
    chapter_title = db.Column(db.Text, nullable=True)
    introduction_description = db.Column(db.Text, nullable=True)
    pronunciation_words = db.Column(JSONB, nullable=False, default=list)
    instructions = db.Column(db.Text, nullable=True)
    reading_description = db.Column(db.Text, nullable=True)
    reading_introduction = db.Column(db.Text, nullable=True)
    vocabulary_words = db.Column(JSONB, nullable=True)
    vocabulary_description = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "chapter": self.chapter,
            "category": self.category,
            "audioUrl": self.audio_url,
            "image": self.image,
            "characterPresentation": self.character_presentation,
            "chapterTitle": self.chapter_title,
            "IntroductionDescription": self.introduction_description,
            "pronunciationWords": self.pronunciation_words,
            "instructions": self.instructions,
            "readingDescription": self.reading_description,
            "readingIntroduction": self.reading_introduction,
            "vocabularyWords": self.vocabulary_words,
            "vocabularyDescription": self.vocabulary_description,
        }