import flask_login
import os
from flask import Flask, render_template, redirect, abort, make_response, jsonify, request, url_for
from data import db_session, api
from data.users import User
from data.companies import Company
from data.tours import Tour
from data.reviews import Review
from forms.user import RegisterForm, LoginForm, RegisterCompanyForm, LoginCompanyForm, EditForm
from forms.tour import AddTourForm
from forms.review import AddReviewForm
from flask_login import LoginManager, login_user, login_required, logout_user
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
image = open("static/image.txt").readline().replace("\n", "")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    return render_template("base.html", title='Главная', img=url_for("static", filename=image))


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form, message="Пароли не совпадают", img=url_for("static", filename=image))
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form, message="Такой пользователь уже есть", img=url_for("static", filename=image))
        user = User(name=form.name.data, email=form.email.data, sex=form.sex.data, birthday=form.birthday.data)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        if form.image.data:
            form.image.data.save(f"static/img/i_{user.id}.jpg")
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form, img=url_for("static", filename=image))


@app.route('/login', methods=['GET', 'POST'])
def login():
    global image
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            f = f"img/i_{flask_login.current_user.id}.jpg"
            if not os.path.exists(f'static/{f}'):
                f = "img/i_base.jpg"
            image = f
            open("static/image.txt", "w").write(f)
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль", form=form, img=url_for("static", filename=image))
    return render_template('login.html', title='Авторизация', form=form, img=url_for("static", filename=image))


@app.route('/register_company', methods=['GET', 'POST'])
def reqister_company():
    form = RegisterCompanyForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register_company.html', title='Регистрация компании', form=form, message="Пароли не совпадают", img=url_for("static", filename=image))
        db_sess = db_session.create_session()
        if db_sess.query(Company).filter(Company.name == form.name.data).first():
            return render_template('register_company.html', title='Регистрация компании', form=form, message="Такая компания уже есть", img=url_for("static", filename=image))
        company = Company(name=form.name.data)
        company.set_password(form.password.data)
        db_sess.add(company)
        db_sess.commit()
        company = db_sess.query(Company).filter(Company.name == form.name.data).first()
        user = flask_login.current_user
        user.access_company += ' ' + str(company.id)
        db_sess.merge(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register_company.html', title='Регистрация компании', form=form, img=url_for("static", filename=image))


@app.route('/login_company', methods=['GET', 'POST'])
def login_company():
    form = LoginCompanyForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        company = db_sess.query(Company).filter(Company.name == form.name.data).first()
        if company and company.check_password(form.password.data):
            user = db_sess.query(User).filter(User.id == flask_login.current_user.id).first()
            if str(company.id) not in user.access_company.split():
                user.access_company = user.access_company + '' + str(company.id)
                db_sess.commit()
                return redirect("/")
            else:
                return render_template('login_company.html', message="Вы уже имеете доступ к данной компании", form=form, img=url_for("static", filename=image))
        return render_template('login_company.html', message="Неправильный логин или пароль", form=form, img=url_for("static", filename=image))
    return render_template('login_company.html', title='Получение доступа к компании', form=form, img=url_for("static", filename=image))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/add_tour',  methods=['GET', 'POST'])
@login_required
def add_tour():
    form = AddTourForm()
    db_sess = db_session.create_session()
    form.set([x.name for x in db_sess.query(User).all()], [x.name for x in db_sess.query(Company).all()])
    if form.validate_on_submit():
        user = flask_login.current_user
        company = db_sess.query(Company).filter(Company.name == form.company_name.data).first()
        if not company:
            return render_template('add_tour.html', title='Добавление тура', form=form, message='Такой компании нет', img=url_for("static", filename=image))
        if str(company.id) not in user.access_company.split():
            return render_template('add_tour.html', title='Добавление тура', form=form, message='У вас нет доступа к этой компании', img=url_for("static", filename=image))
        people = db_sess.query(User).filter(User.name.in_(form.people.data)).all()
        P = str(people[0].id)
        for p in people[1:]:
            P += ',' + str(p.id)
        tour = Tour(title=form.title.data, first_day=form.first_day.data, last_day=form.last_day.data, people=P, company_id=company.id, place=form.place.data)
        db_sess.add(tour)
        db_sess.commit()
        return redirect('/')
    return render_template('add_tour.html', title='Добавление тура', form=form, img=url_for("static", filename=image))


@app.route('/edit_tour/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_tour(id):
    form = AddTourForm()
    form.submit.label.text = 'Сохранить тур'
    db_sess = db_session.create_session()
    form.set([x.name for x in db_sess.query(User).all()], [x.name for x in db_sess.query(Company).all()])
    if request.method == "GET":
        tour = db_sess.query(Tour).filter(Tour.id == id, Tour.company_id.in_(list(map(int, flask_login.current_user.access_company.split())))).first()
        if tour:
            people = db_sess.query(User).filter(User.id.in_(list(map(int, tour.people.split(','))))).all()
            P = []
            for p in people:
                P.append(p.name)
            form.title.data = tour.title
            form.first_day.data = tour.first_day
            form.last_day.data = tour.last_day
            form.people.data = P
            form.company_name.data = db_sess.query(Company).filter(Company.id == tour.company_id).first().name
            form.place.data = tour.place
        else:
            abort(404)
    if form.validate_on_submit():
        user = flask_login.current_user
        company = db_sess.query(Company).filter(Company.name == form.company_name.data).first()
        if not company:
            return render_template('add_tour.html', title='Изменение тура', form=form, message='Такой компании нет', img=url_for("static", filename=image))
        if str(company.id) not in user.access_company.split():
            return render_template('add_tour.html', title='Изменение тура', form=form, message='У вас нет доступа к этой компании', img=url_for("static", filename=image))
        people = db_sess.query(User).filter(User.name.in_(form.people.data)).all()
        P = str(people[0].id)
        for p in people[1:]:
            P += ',' + str(p.id)
        tour.title = form.title.data
        tour.first_day = form.first_day.data
        tour.last_day = form.last_day.data
        tour.people = P
        tour.company_id = company.id
        tour.place = form.place.data
        db_sess.commit()
        return redirect('/')
    return render_template('add_tour.html', title='Изменение тура', form=form, img=url_for("static", filename=image))


@app.route('/delete_tour/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_tour(id):
    db_sess = db_session.create_session()
    tour = db_sess.query(Tour).filter(Tour.id == id, Tour.company_id.in_(list(map(int, flask_login.current_user.access_company.split())))).first()
    if tour:
        db_sess.delete(tour)
        db_sess.commit()
        return redirect("/")
    else:
        abort(404)


@app.route('/tours')
def all_tours():
    acc = ''
    try:
        acc = flask_login.current_user.access_company
    except Exception:
        pass
    db_sess = db_session.create_session()
    tours = db_sess.query(Tour).all()
    K = []
    for t in tours:
        k = ''
        for p in list(map(int, t.people.split(','))):
            if db_sess.query(User).filter(User.id == p).first():
                k += ', ' + db_sess.query(User).filter(User.id == p).first().name
        K.append(k[2:])
    return render_template('show_tours.html', title='Все туры', tours=tours, people=K, acc=acc, img=url_for("static", filename=image))


@app.route('/tours/<int:id>')
def tour_id(id):
    acc = ''
    try:
        acc = flask_login.current_user.access_company
    except Exception:
        pass
    db_sess = db_session.create_session()
    tours = db_sess.query(Tour).filter(Tour.id == id).all()
    if not tours:
        return render_template('show_tours.html', message='Такого тура нет в нашей базе:(', img=url_for("static", filename=image))
    K = []
    for t in tours:
        k = ''
        for p in list(map(int, t.people.split(','))):
            if db_sess.query(User).filter(User.id == p).first():
                k += ', ' + db_sess.query(User).filter(User.id == p).first().name
        K.append(k[2:])
    return render_template('show_tours.html', title=f'Тур {id}', tours=tours, people=K, acc=acc, img=url_for("static", filename=image))


@app.route('/tours/user/<int:id>')
def tour_user(id):
    db_sess = db_session.create_session()
    tours = db_sess.query(Tour).all()
    user = db_sess.query(User).filter(User.id == id).first()
    if not user:
        return render_template('base.html', message='Такого человаека нет в нашей базе:(', img=url_for("static", filename=image))
    K = []
    for t in tours:
        if str(user.id) not in t.people.split(','):
            continue
        k = ''
        for p in list(map(int, t.people.split())):
            if db_sess.query(User).filter(User.id == p).first():
                k += ', ' + db_sess.query(User).filter(User.id == p).first().name
        K.append(k[2:])
    return render_template('show_tours.html', title=f'Туры {user.name}', tours=tours, people=K, acc='', img=url_for("static", filename=image))


@app.route('/tours/place/<string:place>')
def tour_place(place):
    db_sess = db_session.create_session()
    tours = db_sess.query(Tour).filter(Tour.place == place).all()
    K = []
    for t in tours:
        k = ''
        for p in list(map(int, t.people.split())):
            if db_sess.query(User).filter(User.id == p).first():
                k += ', ' + db_sess.query(User).filter(User.id == p).first().name
        K.append(k[2:])
    return render_template('show_tours.html', title=f'Туры в {place}', tours=tours, people=K, acc='', img=url_for("static", filename=image))


@app.route('/tours/company/<int:id>')
def tour_company(id):
    db_sess = db_session.create_session()
    tours = db_sess.query(Tour).filter(Tour.company_id == id).all()
    company = db_sess.query(Company).filter(Company.id == id).first()
    if not company:
        return render_template('show_tours.html', message='Такой компании нет в нашей базе:(', img=url_for("static", filename=image))
    K = []
    for t in tours:
        k = ''
        for p in list(map(int, t.people.split(','))):
            if db_sess.query(User).filter(User.id == p).first():
                k += ', ' + db_sess.query(User).filter(User.id == p).first().name
        K.append(k[2:])
    return render_template('show_tours.html', title=f'Туры компании {company.name}', tours=tours, people=K, acc='', img=url_for("static", filename=image))


@app.route('/reviews')
def all_reviews():
    db_sess = db_session.create_session()
    reviews = db_sess.query(Review).all()
    return render_template('show_reviews.html', title='Все отзывы', reviews=reviews, img=url_for("static", filename=image))


@app.route('/reviews/tour/<int:id>')
def review_tour(id):
    db_sess = db_session.create_session()
    tour = db_sess.query(Tour).filter(Tour.id == id).first()
    reviews = db_sess.query(Review).filter(Review.tour_id == id).all()
    k = ''
    for p in list(map(int, tour.people.split(','))):
        if db_sess.query(User).filter(User.id == p).first():
            k += ', ' + db_sess.query(User).filter(User.id == p).first().name
    return render_template('tour_reviews.html', title=f'Отзывы на тур {tour.title}', reviews=reviews, people=k[2:], tour=tour, img=url_for("static", filename=image))


@app.route('/add_review/', methods=['GET', 'POST'])
@login_required
def add_review():
    form = AddReviewForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = flask_login.current_user
        tour = db_sess.query(Tour).filter(Tour.title == form.tour_name.data).first()
        if not tour:
            return render_template('add_review.html', title='Добавление отзыва', form=form, message='Такого тура нет', img=url_for("static", filename=image))
        if str(user.id) not in tour.people.split(','):
            return render_template('add_review.html', title='Добавление отзыва', form=form, message='Вы не были в этом туре', img=url_for("static", filename=image))
        review = Review(user_id=user.id, tour_id=tour.id, grade=form.grade.data, comment=form.comment.data)
        db_sess.add(review)
        db_sess.commit()
        return redirect('/')
    return render_template('add_review.html', title='Добавление отзыва', form=form, img=url_for("static", filename=image))


@app.route('/add_review/tour/<int:id>', methods=['GET', 'POST'])
@login_required
def add_review_tour(id):
    form = AddReviewForm()
    db_sess = db_session.create_session()
    if db_sess.query(Tour).filter(Tour.id == id).first():
        form.tour_name.data = db_sess.query(Tour).filter(Tour.id == id).first().title
    else:
        form.tour_name.data = f'Тура с id {id} нет в базе'
    if form.validate_on_submit():
        user = flask_login.current_user
        tour = db_sess.query(Tour).filter(Tour.title == form.tour_name.data).first()
        if not tour:
            return render_template('add_review.html', title='Добавление отзыва', form=form, message='Такого тура нет', img=url_for("static", filename=image))
        if str(user.id) not in tour.people.split(','):
            return render_template('add_review.html', title='Добавление отзыва', form=form, message='Вы не были в этом туре', img=url_for("static", filename=image))
        review = Review(user_id=user.id, tour_id=tour.id, grade=form.grade.data, comment=form.comment.data)
        db_sess.add(review)
        db_sess.commit()
        return redirect('/')
    return render_template('add_review.html', title='Добавление отзыва', form=form, img=url_for("static", filename=image))


@app.route('/edit_review/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_review(id):
    form = AddReviewForm()
    form.submit.label.text = 'Сохранить отзыв'
    db_sess = db_session.create_session()
    review = db_sess.query(Review).filter(Review.id == id, Review.user == flask_login.current_user).first()
    if request.method == "GET":
        if review:
            form.tour_name.data = review.tour.title
            form.grade.data = str(review.grade)
            form.comment.data = review.comment
        else:
            abort(404)
    if form.validate_on_submit():
        user = flask_login.current_user
        tour = db_sess.query(Tour).filter(Tour.title == form.tour_name.data).first()
        if not tour:
            return render_template('add_review.html', title='Изменение отзыва', form=form, message='Такого тура нет', img=url_for("static", filename=image))
        if str(user.id) not in tour.people.split(','):
            return render_template('add_review.html', title='Изменение отзыва', form=form, message='Вы не были в этом туре', img=url_for("static", filename=image))
        review.user_id = user.id
        review.tour_id = tour.id
        review.grade = form.grade.data
        review.comment = form.comment.data
        db_sess.commit()
        return redirect('/')
    return render_template('add_review.html', title='Изменение отзыва', form=form, img=url_for("static", filename=image))


@app.route('/delete_review/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_review(id):
    db_sess = db_session.create_session()
    review = db_sess.query(Review).filter(Review.id == id, Review.user == flask_login.current_user).first()
    if review:
        db_sess.delete(review)
        db_sess.commit()
        return redirect("/")
    else:
        abort(404)


@app.route('/account')
def account():
    user = flask_login.current_user
    db_sess = db_session.create_session()
    C = []
    for c in db_sess.query(Company).all():
        if str(c.id) in user.access_company.split():
            C.append(c)
    return render_template('account.html', title='Аккаунт', user=user, companies=C, img=url_for("static", filename=image))


@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    form = EditForm()
    form.submit.label.text = 'Сохранить'
    db_sess = db_session.create_session()
    if id != flask_login.current_user.id:
        return render_template('edit_user.html', title='Изменение данных аккаунта', form=form, img=url_for("static", filename=image), message="У вас нет доступа")
    user = db_sess.query(User).filter(User.id == id).first()
    if request.method == "GET":
        if user:
            form.email.data = user.email
            form.name.data = user.name
            form.sex.data = user.sex
            form.birthday.data = user.birthday
        else:
            abort(404)
    if form.validate_on_submit() and user.check_password(form.password.data):
        if id != flask_login.current_user.id:
            return render_template('edit_user.html', title='Изменение данных аккаунта', form=form, img=url_for("static", filename=image), message="У вас нет доступа")
        user.email = form.email.data
        user.name = form.name.data
        user.sex = form.sex.data
        user.birthday = form.birthday.data
        db_sess.commit()
        form.image.data.save(f"static/img/i_{user.id}.jpg")
        return redirect('/')
    return render_template('edit_user.html', title='Изменение данных аккаунта', form=form, img=url_for("static", filename=image))


@app.route('/users')
def all_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    K = []
    for u in users:
        k = ''
        for c in list(map(int, u.access_company.split())):
            if db_sess.query(Company).filter(Company.id == c).first():
                k += ', ' + db_sess.query(Company).filter(Company.id == c).first().name
        K.append(k[2:])
    return render_template('show_users.html', title='Все пользователи', users=users, companies=K, img=url_for("static", filename=image))


@app.route('/companies')
def all_companies():
    db_sess = db_session.create_session()
    companies = db_sess.query(Company).all()
    K = []
    for c in companies:
        k = ''
        for u in db_sess.query(User).all():
            if str(c.id) in u.access_company.split():
                k += ', ' + u.name
        K.append(k[2:])
    return render_template('show_companies.html', title='Все компании', users=K, companies=companies, img=url_for("static", filename=image))


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


def main():
    db_session.global_init("db/new.db")
    app.register_blueprint(api.blueprint)
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
