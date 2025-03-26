from flask import Flask
from application.database import db

from flask import render_template, request, redirect, url_for, session, flash
from sqlalchemy.exc import IntegrityError

from application.models import * #because we are creating the database here as of now
from datetime import datetime    #imported for registration(so can insert the dob in the db)



app = Flask(__name__)
app.secret_key = 'your_secret_key' #need this for the flash function
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///quiz_master_v1.sqlite3"

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
    return render_template("test.html", user_name="test", password="pass", name="abra ca dabra", qualification="metrix", dob="28-11-2002")

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
        return redirect(url_for('login'))
    else:        

        subjects= Subject.query.all()

        return render_template("admin_dashboard.html")

@app.route('/admin_dashboard/<int:curr_login_id>/create_subject', methods=['GET','POST'])
def create_subject(curr_login_id):
    if not is_admin(curr_login_id):
        flash("You are not authorized","danger")
        return redirect(url_for('login'))
    else:
        if request.method=='POST':
            subject_name=request.form["subject_name"]
            subject_description=request.form["subject_description"]
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




@app.route('/user/<int:curr_login_id>/user_dashboard')
def user_dashboard(curr_login_id):
    return render_template("user_dashboard.html",curr_login_id=curr_login_id)



if __name__=='__main__':
    app.run()