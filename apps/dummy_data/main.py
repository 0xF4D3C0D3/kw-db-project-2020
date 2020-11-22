import itertools

import pandas as pd
import psycopg2
from faker import Faker

import db
from models.class_ import ClassModel
from models.comment import CommentModel
from models.department import DepartmentModel
from models.grade import GradeModel
from models.major import MajorModel
from models.post import PostModel
from models.preclass import PreclassModel
from models.professor import ProfessorModel
from models.scholarship import ScholarshipModel
from models.student import StudentModel

fake = Faker()

try:
    db.execute("SELECT 1 FROM major")
except psycopg2.ProgrammingError:
    db.execute("DROP TABLE IF EXISTS major")
    db.execute(
        """
        CREATE TABLE major ( /*전공에 대한 테이블*/
            id                 CHAR(4)         NOT NULL,      -- 전공 코드
            name               TEXT            NOT NULL,
            PRIMARY KEY(id)
        );
    """
    )

    major_model = MajorModel()
    major_rows = list(itertools.islice(major_model, 30))
    df_major = pd.DataFrame(major_rows, columns=["id", "name"])
    db.insert(df_major, "major")

try:
    db.execute("SELECT 1 FROM department")
except psycopg2.ProgrammingError:
    db.execute("DROP TABLE IF EXISTS department")
    db.execute(
        """
        CREATE TABLE department ( /*학과에 대한 테이블*/
            id              SERIAL,                     -- id
            name            TEXT,                       -- 이름
            place           TEXT,                       -- 장소
            PRIMARY KEY (id)
        );
    """
    )

    department_model = DepartmentModel(fake)
    department_rows = list(itertools.islice(department_model, 30))
    df_department = pd.DataFrame(department_rows, columns=["id", "name", "place"])
    db.insert(df_department, "department")

try:
    db.execute("SELECT 1 FROM professor")
except psycopg2.ProgrammingError:
    db.execute("DROP TABLE IF EXISTS professor")
    db.execute(
        """
        CREATE TABLE professor ( /*교수에 대한 테이블*/
        id               TEXT,                       -- id
        name             TEXT,                       -- 이름
        department_id    INT,                        -- 소속 학과
        PRIMARY KEY (id),
        FOREIGN KEY (department_id) REFERENCES department(id)
        );
    """
    )

    professor_model = ProfessorModel(fake, db.fetch("SELECT id FROM department"))
    professor_rows = list(itertools.islice(professor_model, 30))
    df_professor = pd.DataFrame(professor_rows, columns=["id", "name", "department_id"])
    db.insert(df_professor, "professor")

try:
    db.execute("SELECT 1 FROM class")
except psycopg2.ProgrammingError:
    db.execute("DROP TABLE IF EXISTS class")
    db.execute(
        """
        CREATE TABLE class ( /*과목에 대한 테이블*/
            id              TEXT,                       -- 학정번호
            year            SMALLINT,                   -- 연도
            quarter         SMALLINT,                   -- 학기
            is_completed    BOOLEAN       NOT NULL,     -- 이수 구분
            name            TEXT          NOT NULL,     -- 이름(과목명)
            place           TEXT          NOT NULL,     -- 장소
            period          TEXT          NOT NULL,     -- 시간
            professor       TEXT,                       -- 담당 교수
            credit          SMALLINT      NOT NULL,     -- 학점
            capacity        SMALLINT,                   -- 최대 인원
            is_pass         BOOLEAN       NOT NULL,     -- pass/nonpass 구분
            classification  TEXT          NOT NULL,     -- 이수구분(일선/…)
            department      INT           NOT NULL,     -- 개설학과(소프트웨어학과..)
            PRIMARY KEY (id, year, quarter),
            FOREIGN KEY (professor) REFERENCES professor (id),
            FOREIGN KEY (department) REFERENCES department (id)
        );
    """
    )

    class_model = ClassModel(
        fake,
        db.fetch("SELECT id FROM department"),
        db.fetch("SELECT id FROM professor"),
    )
    class_rows = list(
        itertools.islice(class_model, 30 * 4 * 100)
    )  # 30 years, 100 classes per quarter
    df_class = pd.DataFrame(
        class_rows,
        columns=[
            "id",
            "year",
            "quarter",
            "is_completed",
            "name",
            "place",
            "period",
            "professor",
            "credit",
            "capacity",
            "is_pass",
            "classification",
            "department",
        ],
    )
    db.insert(df_class, "class")

try:
    db.execute("SELECT 1 FROM student")
except psycopg2.ProgrammingError:
    db.execute("DROP TABLE IF EXISTS student")
    db.execute(
        """
        CREATE TABLE student ( /*학생에 대한 테이블*/
        id                   CHAR(10)         NOT NULL,      -- 학번
        name                 VARCHAR(30),      -- 이름
        major_id             CHAR(20)         NOT NULL,      -- 학과
        year                 SMALLINT         NOT NULL,      -- 입학 년도
        semester             SMALLINT         NOT NULL,      -- 입학 학기
        phone                VARCHAR(15),      -- 핸드폰
        email                VARCHAR(50),      -- 이메일
        professor_id         TEXT             NOT NULL,      -- 지도 교수
        pw                   TEXT,
        PRIMARY KEY(id),                                     -- 기본키는 학번
        FOREIGN KEY(major_id) REFERENCES major(id),
        FOREIGN KEY(professor_id) REFERENCES professor(id)
    );
    """
    )

    student_model = StudentModel(
        fake,
        db.fetch("SELECT id FROM major"),
        db.fetch("SELECT id FROM professor"),
    )
    student_rows = list(
        itertools.islice(student_model, 30 * 30 * 50)
    )  # 30 years, 50 students per major
    df_student = pd.DataFrame(
        student_rows,
        columns=[
            "id",
            "name",
            "major_id",
            "year",
            "semester",
            "phone",
            "email",
            "professor_id",
            "pw",
        ],
    )
    db.insert(df_student, "student")

try:
    db.execute("SELECT 1 FROM post")
except psycopg2.ProgrammingError:
    db.execute("DROP TABLE IF EXISTS post")
    db.execute(
        """
        CREATE TABLE post ( /*게시글에 대한 테이블*/
        id          SERIAL        NOT NULL, -- 게시글 번호
        title       CHAR(200)     NOT NULL, -- 제목
        content     VARCHAR(2000) NOT NULL, -- 내용
        like_       INT           NOT NULL  DEFAULT 0, -- 좋아요
        hate        INT           NOT NULL  DEFAULT 0, -- 싫어요
        hits        INT           NOT NULL  DEFAULT 0, -- 조회수
        is_notice   BOOLEAN       NOT NULL, -- T -> 공지, F -> 일반
        class_id    TEXT          NOT NULL, -- 어떤 과목의 게시판인지
        year        SMALLINT      NOT NULL, -- 몇년도의 과목인지
        quarter     SMALLINT      NOT NULL, -- 몇학기의 과목인지
        author                    TEXT        NOT NULL,
        created_time              TIMESTAMP   NOT NULL,
        PRIMARY KEY(id),               -- 기본키는 게시글 번호
        FOREIGN KEY(class_id, year, quarter) REFERENCES class(id, year, quarter)
    );
    """
    )

    post_model = PostModel(
        fake,
        db.fetch("SELECT id, year, quarter FROM class"),
        db.fetch("SELECT id FROM student"),
    )
    post_rows = list(
        itertools.islice(post_model, 30 * 365 * 5)
    )  # 30 years, 5 posts per day
    df_post = pd.DataFrame(
        post_rows,
        columns=[
            "id",
            "title",
            "content",
            "like_",
            "hate",
            "hits",
            "is_notice",
            "class_id",
            "year",
            "quarter",
            "author",
            "created_time",
        ],
    )
    db.insert(df_post, "post")

try:
    db.execute("SELECT 1 FROM comment")
except psycopg2.ProgrammingError:
    db.execute("DROP TABLE IF EXISTS comment")
    db.execute(
        """
        CREATE TABLE comment ( /*댓글에 대한 테이블*/
        id                        SERIAL     NOT NULL, -- id
        comment_id                INT,                 -- 댓글 id
        post_id                   INT,                 -- 게시글 id
        content                   TEXT       NOT NULL, -- 내용
        like_                     INT        NOT NULL, -- 좋아요
        hate                      INT        NOT NULL, -- 싫어요
        author                    TEXT       NOT NULL,
        created_time              TIMESTAMP  NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY (comment_id) REFERENCES comment(id),
        FOREIGN KEY (post_id)   REFERENCES post(id)
    );
    """
    )

    comment_model = CommentModel(
        fake,
        db.fetch("SELECT id, created_time FROM post"),
        db.fetch("SELECT id FROM student"),
    )
    comment_rows = list(
        itertools.islice(comment_model, 30 * 365 * 10)
    )  # 30 years, 10 comments per day
    df_comment = pd.DataFrame(
        comment_rows,
        columns=[
            "id",
            "comment_id",
            "post_id",
            "content",
            "like_",
            "hate",
            "author",
            "created_time",
        ],
    )
    db.insert(df_comment, "comment")

try:
    db.execute("SELECT 1 FROM grade")
except psycopg2.ProgrammingError:
    db.execute("DROP TABLE IF EXISTS grade")
    db.execute(
        """
        CREATE TABLE grade ( /* 수강/성적에 대한 테이블 */
            student_id              CHAR(10)      NOT NULL, -- 학생의 유일한 번호 학번
            class_id                TEXT          NOT NULL, -- 과목의 유일한 번호 학정번호
            year                    SMALLINT      NOT NULL, -- 수강 연도
            quarter                 SMALLINT      NOT NULL, -- 수강 학기
            retake                  BOOLEAN,                -- 재수강여부
            grade                   VARCHAR(15),            -- 받게된 성적
            PRIMARY KEY (student_id, class_id, year, quarter),
            FOREIGN KEY (class_id, year, quarter) REFERENCES class(id, year, quarter),
            FOREIGN KEY (student_id)   REFERENCES student(id)
        );
    """
    )

    grade_model = GradeModel(
        fake,
        db.fetch("SELECT id, year, quarter FROM class"),
        db.fetch("SELECT id FROM student"),
    )
    grade_rows = list(
        itertools.islice(grade_model, 3 * len(df_student))
    )  # 4 years, 15 courses per quarter for each student,
    # but it would be too large so only 3 courses per student
    df_grade = pd.DataFrame(
        grade_rows,
        columns=["student_id", "class_id", "year", "quarter", "retake", "grade"],
    )
    db.insert(df_grade, "grade")

try:
    db.execute("SELECT 1 FROM prerequisite_class")
except psycopg2.ProgrammingError:
    db.execute("DROP TABLE IF EXISTS prerequisite_class")
    db.execute(
        """
        CREATE TABLE prerequisite_class ( /*선후수과목에 대한 테이블*/
        pre_class_id               TEXT,                 -- 선후수과목은 학정번호를 참조
        class_id                   TEXT        NOT NULL, -- 학정번호
        PRIMARY KEY (pre_class_id, class_id)
    );
    """
    )

    preclass_model = PreclassModel(
        db.fetch("SELECT id FROM class WHERE year=2020 AND quarter=2")
    )
    preclass_rows = list(preclass_model)
    df_preclass = pd.DataFrame(
        preclass_rows,
        columns=["pre_class_id", "class_id"],
    )
    db.insert(df_preclass, "prerequisite_class")

try:
    db.execute("SELECT 1 FROM scholarship")
except psycopg2.ProgrammingError:
    db.execute("DROP TABLE IF EXISTS scholarship")
    db.execute(
        """
        CREATE TABLE scholarship ( /*장학금에 대한 테이블*/
            year                   SMALLINT    NOT NULL,
            semester               SMALLINT    NOT NULL,
            won                    INT         NOT NULL, 
            PRIMARY KEY (year, semester)
        );
    """
    )

    scholarship_model = ScholarshipModel()
    scholarship_rows = list(itertools.islice(scholarship_model, 30))
    df_scholarship = pd.DataFrame(
        scholarship_rows,
        columns=["year", "semester", "won"],
    )
    db.insert(df_scholarship, "scholarship")
