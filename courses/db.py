from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

association_table_instructors = db.Table('association_i', db.Model.metadata,
    db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
)

association_table_students = db.Table('association_s', db.Model.metadata,
    db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
)

class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    assignments = db.relationship('Assignment', cascade='delete')
    instructors = db.relationship('User', secondary=association_table_instructors, back_populates='courses_i')
    students = db.relationship('User', secondary=association_table_students, back_populates='courses_s')

    def __init__(self, **kwargs):
        self.code = kwargs.get('code', '')
        self.name = kwargs.get('name', '')
        self.assignments = []

    def serialize(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'assignments': [a.serialize() for a in self.assignments],
            'instructors': [i.serialize() for i in self.instructors],
            'students': [s.serialize() for s in self.students]
        }

class User(db.Model):
    __tablename__='user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    netid = db.Column(db.String, nullable=False)
    courses_i = db.relationship('Course', secondary=association_table_instructors, back_populates='instructors')
    courses_s = db.relationship('Course', secondary=association_table_students, back_populates='students')


    def __init__(self, **kwargs):
        self.name = kwargs.get('name', '')
        self.netid = kwargs.get('netid', '')

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'netid': self.netid,
            'courses': []
        }

class Assignment(db.Model):
    __tablename__ = 'assignment'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    due_date = db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    def __init__(self, **kwargs):
        self.title = kwargs.get('title', '')
        self.due_date = kwargs.get('due_date', '')

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'due_date': self.due_date,
            'course': self.course_id
        }
