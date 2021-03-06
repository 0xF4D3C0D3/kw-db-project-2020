from flask_login import login_user
from flask_restx import Namespace, Resource, reqparse

import db
from kw_sis_session import User

api = Namespace('login', description='Login related operations')

login_post_parser = reqparse.RequestParser()
login_post_parser.add_argument('student_id', type=str, required=True, location='form')
login_post_parser.add_argument('hashed_pw', type=str, required=True, location='form')


@api.route('')
class Login(Resource):
    @api.expect(login_post_parser)
    def post(self):
        params = login_post_parser.parse_args()

        expected_pw = db.fetch(f"SELECT pw FROM student WHERE id = '{params['student_id']}'")[0]
        if params['hashed_pw'] != expected_pw:
            return {'msg': '잘못된 비밀번호 입니다.'}, 401

        user = User(params['student_id'])
        login_user(user)
