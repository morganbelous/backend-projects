import json
from db import db, Assignment, Course, User
from flask import Flask, request

app = Flask(__name__)
db_filename = 'cms.db'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % db_filename
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/')
@app.route('/api/courses/')
def get_courses():
    courses = Course.query.all()
    res = {'success': True, 'data': [c.serialize() for c in courses]}
    return json.dumps(res), 200

@app.route('/api/courses/', methods = ['POST'])
def create_course():
    post_body = json.loads(request.data)
    code = post_body.get('code', '')
    name = post_body.get('name', '')
    course = Course(
        name = name,
        code = code
    )
    db.session.add(course)
    db.session.commit()
    return json.dumps({'success': True, 'data': course.serialize()}), 200

@app.route('/api/course/<int:course_id>/')
def get_course(course_id):
    course = Course.query.filter_by(id=course_id).first()
    if not course:
        return json.dumps({'success': False, 'error': 'Course not found'}), 404
    return json.dumps({'success': True, 'data': course.serialize()}), 200

@app.route('/api/users/', methods = ['POST'])
def create_user():
    post_body = json.loads(request.data)
    name = post_body.get('name')
    netid = post_body.get('netid')
    user = User(
        name= name,
        netid = netid,
    )
    db.session.add(user)
    db.session.commit()
    return json.dumps({'success': True, 'data': user.serialize()}), 200

@app.route('/api/user/<int:user_id>/')
def get_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return json.dumps({'success': False, 'error': 'User not found'})
    return json.dumps({'success': True, 'data': user.serialize()}), 200

@app.route('/api/course/<int:course_id>/add/', methods = ['POST'])
def add_user_to_course(course_id):
    course = Course.query.filter_by(id=course_id).first()
    if not course:
        return json.dumps({'success': False, 'error': 'Course not found'})
    post_body = json.loads(request.data)
    type = post_body.get('type', '')
    user_id = post_body.get('user_id', '')
    user = User.query.filter_by(id=user_id).first()
    if type == "instructor":
        user.courses_i.append(course)
        course.instructors.append(user)
    if type == "student":
        user.courses_s.append(course)
        course.students.append(user)
    db.session.commit()
    return json.dumps({'success': True, 'data': course.serialize()}), 200

@app.route('/api/course/<int:course_id>/assignment/', methods = ['POST'])
def create_assignment(course_id):
    course = Course.query.filter_by(id=course_id).first()
    if not course:
        return json.dumps({'success': False, 'error': 'Course not found'}), 404
    post_body= json.loads(request.data)
    assignment = Assignment(
        title=post_body.get('title', ''),
        due_date=post_body.get('due_date', ''),
        course_id = course_id
    )
    course.assignments.append(assignment)
    db.session.add(assignment)
    db.session.commit()
    return json.dumps({'success': True, 'data': assignment.serialize()}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
