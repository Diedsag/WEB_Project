import flask
from flask import jsonify, make_response
from . import db_session
from .users import User
from .companies import Company
blueprint = flask.Blueprint('api', __name__, template_folder='templates')


@blueprint.route('/api/users')
def get_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return jsonify({'users': [item.to_dict(only=('id', 'name', 'birthday', 'sex', 'email', 'created_date')) for item in users]})


@blueprint.route('/api/users/<int:id>', methods=['GET'])
def get_one_users(id):
    db_sess = db_session.create_session()
    users = db_sess.query(User).get(id)
    if not users:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify({'user': users.to_dict(only=('id', 'name', 'birthday', 'sex', 'email', 'created_date'))})


@blueprint.route('/api/companies')
def get_companies():
    db_sess = db_session.create_session()
    companies = db_sess.query(Company).all()
    X = {'companies': []}
    for item in companies:
        k = ''
        for u in db_sess.query(User).all():
            if str(item.id) in u.access_company.split():
                k += ', ' + u.name
        X['companies'].append({'id': item.id, 'name': item.name, 'created_date': item.created_date, 'users': k[2:]})
    return jsonify(X)


@blueprint.route('/api/companies/<int:id>', methods=['GET'])
def get_one_companies(id):
    db_sess = db_session.create_session()
    companies = db_sess.query(Company).all()
    if not companies:
        return make_response(jsonify({'error': 'Not found'}), 404)
    X = {}
    for item in companies:
        k = ''
        for u in db_sess.query(User).all():
            if str(item.id) in u.access_company.split():
                k += ', ' + u.name
        X['company'] = {'id': item.id, 'name': item.name, 'created_date': item.created_date, 'users': k[2:]}
    return jsonify(X)
