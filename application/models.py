from .database import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    qualification = db.Column(db.String(100))
    dob = db.Column(db.Date)
    role = db.Column(db.Boolean, nullable=False, default=False)  # will store True for admin

    quizes_attempted = db.relationship('Score', backref='user') 
    #If I need always the score along with user then the parameter lazy can be used for speed up

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.Text)

    chapters = db.relationship('Chapter', backref='subject', cascade='all, delete-orphan')


class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)

    quizes = db.relationship('Quiz', backref='chapter', cascade='all, delete-orphan')


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)

    date_of_quiz = db.Column(db.Date, nullable=False)
    time_duration = db.Column(db.Time, nullable=False)  
    remarks = db.Column(db.Text, nullable=True)

    questions = db.relationship('Question', backref='quiz', cascade='all, delete-orphan')
    scores = db.relationship('Score', backref='quiz')


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)

    question_statement = db.Column(db.Text, nullable=False)
    option_1 = db.Column(db.String(255), nullable=False)
    option_2 = db.Column(db.String(255), nullable=False)
    option_3 = db.Column(db.String(255), nullable=False)
    option_4 = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False) #will store the option number
    #will add another column later to store marks of the questions to include the cases where each question may not have the same marks 


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    time_stamp = db.Column(db.DateTime, nullable=False)
    user_score = db.Column(db.Integer, nullable=False)
    total_score = db.Column(db.Integer, nullable=False)