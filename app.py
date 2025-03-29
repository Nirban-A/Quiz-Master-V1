from flask import Flask
from application.database import db

from flask import render_template, request, redirect, url_for, session, flash
from sqlalchemy.exc import IntegrityError

from application.models import * #because we are creating the database here as of now
from datetime import datetime, date    #imported for registration(so can insert the dob in the db) and also to for the deadline of quiz



app = Flask(__name__)
app.secret_key = 'your_secret_key' #need this for the flash function
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///quiz_master_v1.sqlite3"
app.config["TEMPLATES_AUTO_RELOAD"]=True

#we are initialising the SQLalchemy object db (which initialises the db) with the flask application app
db.init_app(app) 

with app.app_context():
    db.create_all()

    admin = User.query.filter_by(username="admin@email.com").first()
    if not admin:
        admin_user = User(
            username="admin@email.com",
            password="quiz123", 
            full_name="Quiz Master",
            role=True  # As admin
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created!")

@app.route("/")
def test():
    #return render_template("test.html")
    return redirect(url_for('login'))

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method=='POST':
        username=request.form["username"]
        password=request.form["password"]
        name=request.form["name"]
        qualification=request.form["qualification"]
        dob=request.form["dob"]
        if dob:
            try:
                dob = datetime.strptime(dob, '%Y-%m-%d').date()  # Convert to Python date
            except:
                pass
        else:
            dob = None

#the following two lines are only for testing purposes
        print("details ------ \n")
        print(username, password, name, qualification, dob)  #for debugging purposes

        try:
            new_user=User(username=username, password=password, full_name=name, qualification=qualification, dob=dob, role=False) #dob=dob, omitting it ony during the testing
            db.session.add(new_user)
            db.session.commit()

            flash("You have registered successfully",'success')
            print("Registration Successful")  #for debugging purposes
            return redirect(url_for('login'))
        
        except IntegrityError:
            db.session.rollback()
            error_message="Username (email) already exists"
            flash(error_message,'danger')
            print(error_message) #for debugging purposes
            return redirect(url_for('register'))

    return render_template("register.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        username=request.form["username"]
        password=request.form["password"]
        print(username, password) #for testing only

        user=User.query.filter(User.username==username).first()
        if user:
            #the following line is for debugging only
            print(f"Found User: {user.username}, Role: {user.role}, Password {password}, DB_Password: {user.password}")

            if user.password==password:
                session['user_id']=user.id
                return redirect(url_for('dashboard',curr_login_id=user.id))

            else:
                error_message="Incorrect password. Please try again."
                flash(error_message, "danger")
                print(error_message)  #remove this line later. For debugging purposes
                return redirect(url_for('login'))

        else:
            error_message="Email does not exist. Please register."
            flash(error_message, "danger")
            print(error_message)  #remove this line later. For debugging purposes
        return redirect(url_for('login'))

    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


#function to check if the current user is really admin
def is_admin(curr_login_id):
    if "user_id" in session and session['user_id']==curr_login_id:
        user=User.query.get(curr_login_id) 
        return user.role
    return False 


@app.route('/dashboard/<int:curr_login_id>', methods=['GET'])
def dashboard(curr_login_id):
    if request.method=='GET':
        if 'user_id' in session and session['user_id']==curr_login_id:
            user=User.query.get(curr_login_id)
            if user.role:
                return redirect(url_for('admin_dashboard',curr_login_id=curr_login_id))
            else:
                return redirect(url_for('user_dashboard',curr_login_id=curr_login_id))


@app.route('/admin_dashboard/<int:curr_login_id>')
def admin_dashboard(curr_login_id):
    if not is_admin(curr_login_id):
        flash("You are not authorized","danger")
        return redirect(url_for('logout'))
 
    subjects= Subject.query.all()
    return render_template("admin_dashboard.html",subjects=subjects)

@app.route('/admin_dashboard/score/<int:curr_login_id>')
def score_dashboard(curr_login_id):
    if not is_admin(curr_login_id):
        flash("You are not authorized","danger")
        return redirect(url_for('logout'))
 
    scores= Score.query.all()
    return render_template("admin_dashboard_scores.html",scores=scores)

@app.route('/admin_dashboard/<int:curr_login_id>/create_subject', methods=['GET','POST'])
def create_subject(curr_login_id):
    if not is_admin(curr_login_id):
        flash("You are not authorized","danger")
        return redirect(url_for('logout'))
    
    if request.method=='POST':
        subject_name=request.form["subject_name"].strip()
        subject_description=request.form["subject_description"].strip()
        print(subject_name, subject_description)

        try:
            new_subject=Subject(name=subject_name,description=subject_description)
            db.session.add(new_subject)
            db.session.commit()

            print("new subject addition Successful")  #for debugging purposes
            return redirect(url_for('admin_dashboard',curr_login_id=curr_login_id))
    
        except IntegrityError:
            db.session.rollback()
            error_message="Subject already exists"
            flash(error_message,'danger')
            print(error_message) #for debugging purposes
            return redirect(url_for('create_subject',curr_login_id=curr_login_id))

    return render_template("create_subject.html",curr_login_id=curr_login_id)


@app.route('/admin_dashboard/<int:curr_login_id>/update_subject/<int:subject_id>', methods=['GET','POST'])
def update_subject(curr_login_id,subject_id):
    if not is_admin(curr_login_id):
        flash("You are not authorized","danger")
        return redirect(url_for('logout'))

    subject=Subject.query.get_or_404(subject_id)
    if request.method=='POST':
        try:
            subject.name=request.form["subject_name"].strip()
            subject.description=request.form["subject_description"].strip()
            print("updated",subject.name, subject.description)
            db.session.commit()

            print("subject updation Successful")  #for debugging purposes
            return redirect(url_for('admin_dashboard',curr_login_id=curr_login_id))
    
        except IntegrityError:
            db.session.rollback()
            error_message="Subject already exists"
            flash(error_message,'danger')
            print(error_message) #for debugging purposes
            return redirect(url_for('update_subject',curr_login_id=curr_login_id,subject_id=subject.id))

    return render_template("update_subject.html",curr_login_id=curr_login_id,subject=subject)


@app.route('/admin_dashboard/<int:curr_login_id>/delete_subject/<int:subject_id>', methods=['GET','POST'])
def delete_subject(curr_login_id,subject_id):
    if not is_admin(curr_login_id):
        flash("You are not authorized","danger")
        return redirect(url_for('logout'))

    subject=Subject.query.get_or_404(subject_id)
    if request.method=='POST':
        try:
            db.session.delete(subject)
            db.session.commit()

            print("subject deletion Successful")  #for debugging purposes
            return redirect(url_for('admin_dashboard',curr_login_id=curr_login_id))
        

    #have to deleted after testing    
        except IntegrityError:
            db.session.rollback()
            error_message="Subject already exists"
            flash(error_message,'danger')
            print(error_message) #for debugging purposes
            return redirect(url_for('delete_subject',curr_login_id=curr_login_id,subject_id=subject.id))
        
    return render_template("delete_subject.html",curr_login_id=curr_login_id,subject=subject)


@app.route('/admin_dashboard/<int:curr_login_id>/create_chapter/<int:subject_id>', methods=['GET','POST'])
def create_chapter(curr_login_id,subject_id):
    if not is_admin(curr_login_id):
        flash("You are not authorized","danger")
        return redirect(url_for('logout'))

    subject=Subject.query.get_or_404(subject_id)
    if request.method=='POST':
        chapter_name=request.form["chapter_name"].strip()
        chapter_description=request.form["chapter_description"].strip()
        print(chapter_name, chapter_description) #for debugging purposes

        try:
            new_chapter=Chapter(name=chapter_name,description=chapter_description,subject_id=subject_id)
            db.session.add(new_chapter)
            db.session.commit()

            print("new chapter addition Successful")  #for debugging purposes
            return redirect(url_for('admin_dashboard',curr_login_id=curr_login_id))
    
        except IntegrityError:
            db.session.rollback()
            error_message="Chapter already exists"
            flash(error_message,'danger')
            print(error_message) #for debugging purposes
            return redirect(url_for('create_chapter',curr_login_id=curr_login_id,subject_id=subject_id))

    return render_template("create_chapter.html",curr_login_id=curr_login_id,subject=subject)


@app.route('/admin_dashboard/<int:curr_login_id>/update_/<int:chapter_id>', methods=['GET','POST'])
def update_chapter(curr_login_id,chapter_id):
    if not is_admin(curr_login_id):
        flash("You are not authorized","danger")
        return redirect(url_for('logout'))

    chapter=Chapter.query.get_or_404(chapter_id)
    if request.method=='POST':
        try:
            chapter.name=request.form["chapter_name"].strip()
            chapter.description=request.form["chapter_description"].strip()
            print("updated",chapter.name, chapter.description)
            db.session.commit()

            print("chapter updation Successful")  #for debugging purposes
            return redirect(url_for('admin_dashboard',curr_login_id=curr_login_id))
    
        except IntegrityError:
            db.session.rollback()
            error_message="Chapter already exists"
            flash(error_message,'danger')
            print(error_message) #for debugging purposes
            return redirect(url_for('update_chapter',curr_login_id=curr_login_id,chapter_id=chapter.id))

    return render_template("update_chapter.html",curr_login_id=curr_login_id,chapter=chapter)


@app.route('/admin_dashboard/<int:curr_login_id>/delete_chapter/<int:chapter_id>', methods=['GET','POST'])
def delete_chapter(curr_login_id,chapter_id):
    if not is_admin(curr_login_id):
        flash("You are not authorized","danger")
        return redirect(url_for('logout'))

    chapter=Chapter.query.get_or_404(chapter_id)
    if request.method=='POST':
        try:
            db.session.delete(chapter)
            db.session.commit()

            print("Chapter deletion Successful")  #for debugging purposes
            return redirect(url_for('admin_dashboard',curr_login_id=curr_login_id))
        
        #have to deleted after testing
        except IntegrityError:
            db.session.rollback()
            flash("Something went wrong, Try again",'danger')
            return redirect(url_for('delete_chapter',curr_login_id=curr_login_id,chapter_id=chapter.id))

    return render_template("delete_chapter.html",curr_login_id=curr_login_id,chapter=chapter)

@app.route('/admin_dashboard/<int:curr_login_id>/quiz/quiz_dashboard')
def quiz_dashboard(curr_login_id):
    if not is_admin(curr_login_id):
        flash("You are not authorized","danger")
        return redirect(url_for('logout'))
    
    quizes=Quiz.query.all()

    return render_template("quiz_dashboard.html",quizes=quizes)


@app.route('/admin_dashboard/<int:curr_login_id>/quiz/create_quiz/sub_choice', methods=['GET','POST'])
def create_quiz_choose_subject(curr_login_id):
    if not is_admin(curr_login_id):
        flash("You are not authorized","danger")
        return redirect(url_for('logout'))

    subjects= Subject.query.all()
    if request.method=='POST':
        subject_id=request.form["subject"]
        return redirect(url_for('create_quiz', curr_login_id=session['user_id'], subject_id=subject_id))
    
    return render_template("create_quiz_sub_choice.html",curr_login_id=curr_login_id,subjects=subjects)



@app.route('/admin_dashboard/<int:curr_login_id>/quiz/create_quiz/<int:subject_id>', methods=['GET','POST'])
def create_quiz(curr_login_id,subject_id):
    if not is_admin(curr_login_id):
        flash("You are not authorized","danger")
        return redirect(url_for('logout'))

    subject=Subject.query.get_or_404(subject_id)
    if request.method=='POST':

        chapter_id=request.form["chapter_id"]
        quiz_remarks=request.form["quiz_remarks"].strip()
        quiz_date=request.form["date_of_quiz"]
        quiz_duration=request.form["time_of_quiz"]

        if quiz_date:
            try:
                quiz_date = datetime.strptime(quiz_date, '%Y-%m-%d').date()  # Convert to Python date
            except:
                pass
        else:
            quiz_date = None
                        
        # Convert the string to a datetime.time object
        if quiz_duration:
            quiz_duration = datetime.strptime(quiz_duration, "%H:%M").time()
        else:
            quiz_duration = None 
        
        print(chapter_id,quiz_date, quiz_remarks, quiz_duration) #for debugging purposes

        try:
            new_quiz=Quiz(chapter_id=chapter_id,date_of_quiz=quiz_date,time_duration=quiz_duration,remarks=quiz_remarks)
            db.session.add(new_quiz)
            db.session.commit()

            print("new Quiz addition Successful")  #for debugging purposes
            return redirect(url_for('quiz_dashboard',curr_login_id=curr_login_id))
    
    #there should not be any issue of integrity error
        except IntegrityError:
            db.session.rollback()
            flash("Something went wrong, Try again",'danger')
            return redirect(url_for('create_chapter',curr_login_id=curr_login_id,subject_id=subject_id))

    return render_template("create_quiz.html",curr_login_id=curr_login_id,subject=subject)


@app.route('/admin_dashboard/<int:curr_login_id>/quiz/delete_quiz/<int:quiz_id>', methods=['GET','POST'])
def delete_quiz(curr_login_id,quiz_id):
    if not is_admin(curr_login_id):
        flash("You are not authorized","danger")
        return redirect(url_for('logout'))

    quiz=Quiz.query.get_or_404(quiz_id)
    if request.method=='POST':
        try:
            db.session.delete(quiz)
            db.session.commit()

            print("Quiz deletion Successful")  #for debugging purposes
            return redirect(url_for('quiz_dashboard',curr_login_id=curr_login_id))
    
    #have to deleted after testing
        except IntegrityError:
            db.session.rollback()
            flash("Something went wrong, Try again",'danger')
            return redirect(url_for('delete_quiz',curr_login_id=curr_login_id,quiz_id=quiz_id))
        
    return render_template("delete_quiz.html",curr_login_id=curr_login_id,quiz_id=quiz_id)

@app.route('/admin_dashboard/<int:curr_login_id>/quiz/update_quiz/sub_choice/<int:quiz_id>', methods=['GET','POST'])
def update_quiz_choose_subject(curr_login_id,quiz_id):
    if not is_admin(curr_login_id):
        flash("You are not authorized","danger")
        return redirect(url_for('logout'))

    subjects= Subject.query.all()
    if request.method=='POST':
        subject_id=request.form["subject"]
        return redirect(url_for('update_quiz', curr_login_id=session['user_id'], subject_id=subject_id,quiz_id=quiz_id))
    
    return render_template("update_quiz_sub_choice.html",curr_login_id=curr_login_id,subjects=subjects,quiz_id=quiz_id)

@app.route('/admin_dashboard/<int:curr_login_id>/quiz/update_quiz/<int:subject_id>/<int:quiz_id>', methods=['GET','POST'])
def update_quiz(curr_login_id,subject_id,quiz_id):
    if not is_admin(curr_login_id):
        flash("You are not authorized","danger")
        return redirect(url_for('logout'))

    subject=Subject.query.get_or_404(subject_id)
    quiz=Quiz.query.get_or_404(quiz_id)
    if request.method=='POST':        
        try:
            quiz.chapter_id=request.form["chapter_id"]
            quiz.remarks=request.form["quiz_remarks"].strip()

            if request.form["date_of_quiz"]:
                try:
                    quiz.date_of_quiz = datetime.strptime(request.form["date_of_quiz"], '%Y-%m-%d').date()  # Convert to Python date
                except:
                    pass
            else:
                quiz.date_of_quiz = None

                   # Convert the string to a datetime.time object
            if request.form["time_of_quiz"]:
                quiz.time_duration = datetime.strptime(request.form["time_of_quiz"], "%H:%M").time()
            else:
                quiz.time_duration= None 

            print(quiz.chapter_id,quiz.date_of_quiz, quiz.remarks, quiz.time_duration) #for debugging purposes
            db.session.commit()
            print("Quiz updation Successful")  #for debugging purposes
            return redirect(url_for('quiz_dashboard',curr_login_id=curr_login_id))
    
    #there should not be any issue of integrity error
        except IntegrityError:
            db.session.rollback()
            flash("Something went wrong, Try again",'danger')
            return redirect(url_for('update_quiz',curr_login_id=curr_login_id,subject_id=subject_id,quiz_id=quiz_id))

    return render_template("update_quiz.html",curr_login_id=curr_login_id,subject=subject,quiz_id=quiz_id)


@app.route('/admin_dashboard/<int:curr_login_id>/quiz/questions/<int:quiz_id>', methods=['GET','POST'])
def question_dashboard(curr_login_id,quiz_id):
    if not is_admin(curr_login_id):
        flash("You are not authorized","danger")
        return redirect(url_for('logout'))

    quiz=Quiz.query.get_or_404(quiz_id)

    return render_template("question_dashboard.html",curr_login_id=curr_login_id,quiz=quiz)

@app.route('/admin_dashboard/<int:curr_login_id>/quiz/create_question/<int:quiz_id>', methods=['GET','POST'])
def create_question(curr_login_id,quiz_id):
    if not is_admin(curr_login_id):
        flash("You are not authorized","danger")
        return redirect(url_for('logout'))

    if request.method=='POST':
        question_statement=request.form["question_statement"].strip()
        option_1=request.form["option_1"].strip()
        option_2=request.form["option_2"].strip()
        option_3=request.form["option_3"].strip()
        option_4=request.form["option_4"].strip()
        correct_option=int(request.form["correct_option"])

        try:
            new_question=Question(quiz_id=quiz_id,statement=question_statement,option_1=option_1,option_2=option_2,option_3=option_3,option_4=option_4, correct_option=correct_option ) 
            db.session.add(new_question)
            db.session.commit()

            print("Question Addition Successful")  #for debugging purposes
            return redirect(url_for('question_dashboard', curr_login_id=curr_login_id, quiz_id=quiz_id))
        
        except IntegrityError:
            db.session.rollback()
            error_message="Username (email) already exists"
            flash(error_message,'danger')
            print(error_message) #for debugging purposes
            return redirect(url_for('create_question', curr_login_id=curr_login_id, quiz_id=quiz_id))
    return render_template("create_question.html",curr_login_id=curr_login_id,quiz_id=quiz_id)


@app.route('/admin_dashboard/<int:curr_login_id>/quiz/update_question/<int:question_id>', methods=['GET','POST'])
def update_question(curr_login_id,question_id):
    if not is_admin(curr_login_id):
        flash("You are not authorized","danger")
        return redirect(url_for('logout'))

    question=Question.query.get_or_404(question_id)
    if request.method=='POST':
        try:
            question.statement=request.form["question_statement"].strip()
            question.option_1=request.form["option_1"].strip()
            question.option_2=request.form["option_2"].strip()
            question.option_3=request.form["option_3"].strip()
            question.option_4=request.form["option_4"].strip()
            question.correct_option=int(request.form["correct_option"])
            db.session.commit()

            print("Question Updation Successful")  #for debugging purposes
            return redirect(url_for('question_dashboard', curr_login_id=curr_login_id, quiz_id=question.quiz.id))

#should be removed before final as should not occurr       
        except IntegrityError:
            db.session.rollback()
            error_message="Username (email) already exists"
            flash(error_message,'danger')
            print(error_message) #for debugging purposes
            return redirect(url_for('update_question', curr_login_id=curr_login_id, question_id=question_id))
        
    return render_template("update_question.html",curr_login_id=curr_login_id,question=question)


@app.route('/admin_dashboard/<int:curr_login_id>/quiz/delete_question/<int:question_id>', methods=['GET','POST'])
def delete_question(curr_login_id,question_id):
    if not is_admin(curr_login_id):
        flash("You are not authorized","danger")
        return redirect(url_for('logout'))

    question=Question.query.get_or_404(question_id)
    quiz_id=question.quiz.id
    if request.method=='POST':
        try:
            db.session.delete(question)
            db.session.commit()

            print("Question deletion Successful")  #for debugging purposes
            return redirect(url_for('question_dashboard', curr_login_id=curr_login_id, quiz_id=quiz_id))
    
    #have to deleted after testing
        except IntegrityError:
            db.session.rollback()
            flash("Something went wrong, Try again",'danger')
            return redirect(url_for('delete_question',curr_login_id=curr_login_id,question_id=question_id))
        
    return render_template("delete_question.html",curr_login_id=curr_login_id,quiz_id=quiz_id)

@app.route('/admin_dashboard/users/<int:curr_login_id>')
def admin_dashboard_users(curr_login_id):
    if not is_admin(curr_login_id):
        flash("You are not authorized","danger")
        return redirect(url_for('logout'))
 
    users= User.query.all()
    return render_template("admin_dashboard_users.html",users=users)

@app.route('/admin_dashboard/edit_user/<int:curr_login_id>/<int:user_id>', methods=['GET', 'POST'])
def edit_user(curr_login_id,user_id):
    if not is_admin(curr_login_id):
        flash("You are not authorized","danger")
        return redirect(url_for('logout'))
    
    user=User.query.get_or_404(user_id)
    if request.method=='POST':
        try:
            user.username=request.form["username"].strip()
            user.password=request.form["password"]
            user.full_name=request.form["name"].strip()
            user.qualification=request.form["qualification"].strip()

            db.session.commit()
            print("User updation Successful")  #for debugging purposes
            return redirect(url_for('admin_dashboard_users',curr_login_id=curr_login_id))

        
        except IntegrityError:
            db.session.rollback()
            flash("Given email id is already registered")
            return redirect(url_for('edit_user',curr_login_id=curr_login_id,user_id=user_id))

    return render_template("update_user.html",user=user)

@app.route('/admin_dashboard/delete_user/<int:curr_login_id>/<int:user_id>', methods=['GET','POST'])
def delete_user(curr_login_id,user_id):
    if not is_admin(curr_login_id):
        flash("You are not authorized","danger")
        return redirect(url_for('logout'))

    user=User.query.get_or_404(user_id)
    if request.method=='POST':
        try:
            db.session.delete(user)
            db.session.commit()
            print("Question deletion Successful")  #for debugging purposes
            return redirect(url_for('admin_dashboard_users',curr_login_id=curr_login_id))
    
    #have to deleted after testing
        except IntegrityError:
            db.session.rollback()
            flash("Something went wrong, Try again",'danger')
            return redirect(url_for('delete_user',curr_login_id=curr_login_id,user_id=user_id))
        
    return render_template("delete_user.html",curr_login_id=curr_login_id,user=user)


#function to check if the current user is authorised
def is_user(curr_login_id):
    if "user_id" in session and session['user_id']==curr_login_id:
        user=User.query.get(curr_login_id) 
        return True
    return False 

@app.route('/user/<int:curr_login_id>/user_dashboard')
def user_dashboard(curr_login_id):
    if not is_user(curr_login_id):
        flash("You are not authorized","danger")
        return redirect(url_for('logout'))
    user = User.query.get(session['user_id'])
    quizes=Quiz.query.all()
    todays_date=date.today()
    return render_template("user_dashboard.html",user=user,quizes=quizes,todays_date=todays_date)


from datetime import datetime

@app.route('/user/<int:curr_login_id>/exam_portal/<int:quiz_id>', methods=['GET', 'POST'])
def exam_portal(curr_login_id, quiz_id):
    if not is_user(curr_login_id):
        flash("You are not authorized", "danger")
        return redirect(url_for('logout'))
    
    quiz = Quiz.query.get_or_404(quiz_id)

    if request.method == 'POST':
        user_score = 0
        total_score = len(quiz.questions)  

        for question in quiz.questions:
            selected_option = request.form.get(f'answer_{question.id}')  
            
            if selected_option and int(selected_option) == question.correct_option:
                user_score += 1  # Increase score for correct answers

        # Store the score in the database
        new_score = Score(
            quiz_id=quiz.id,
            user_id=curr_login_id,
            time_stamp=datetime.now(),
            user_score=user_score,
            total_score=total_score
        )
        db.session.add(new_score)
        db.session.commit()

        print(f"Your answers have been submitted! Score: {user_score}/{total_score}", "success")
        return redirect(url_for('user_dashboard', curr_login_id=curr_login_id))

    return render_template("exam_portal.html", quiz=quiz)






if __name__=='__main__':
    app.run(debug=True)