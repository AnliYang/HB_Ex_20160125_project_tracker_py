"""Hackbright Project Tracker.

A front-end for a database that allows users to work with students, class
projects, and the grades students receive in class projects.
"""
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import sys

db = SQLAlchemy()


def connect_to_db(app):
    """Connect the database to our Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///hackbright'
    db.app = app
    db.init_app(app)


def get_student_by_github(github):
    """Given a github account name, print information about the matching student."""

    QUERY = """
        SELECT first_name, last_name, github
        FROM Students
        WHERE github = :github
        """
    db_cursor = db.session.execute(QUERY, {'github': github})
    row = db_cursor.fetchone()
    print "Student: %s %s\nGithub account: %s" % (row['first_name'], row['last_name'], row['github'])


def make_new_student(first_name, last_name, github):
    """Add a new student and print confirmation.

    Given a first name, last name, and GitHub account, add student to the
    database and print a confirmation message.
    """
    
    QUERY = """
        INSERT INTO Students VALUES (:first_name, :last_name, :github)"""
    db.session.execute(QUERY, {'first_name': first_name,
                                           'last_name': last_name,
                                           'github': github})
    db.session.commit()

    print "Successfully added student: %s %s" % (first_name, last_name)


def get_project_by_title(title):
    """Given a project title, print information about the project."""
    
    QUERY = """
        SELECT description
        FROM Projects
        WHERE title = :title
        """
    db_cursor = db.session.execute (QUERY, {'title': title})
    row = db_cursor.fetchone()
    print "%s Project Description: %s" %(title, row[0])


def get_grade_by_github_title(github, title):
    """Print grade student received for a project."""
    
    QUERY = """
        SELECT grade, first_name
        FROM Grades
            JOIN Students ON (Grades.student_github = Students.github)
        WHERE student_github = :github
            AND project_title = :title
        """
    db_cursor = db.session.execute (QUERY, {'title': title, 'github': github})
    row = db_cursor.fetchone()
    print "Grade for %s on %s project: %s" %(row['first_name'], title, row['grade'])    


def assign_grade(github, title, grade):
    """Assign a student a grade on an assignment and print a confirmation."""
    
    QUERY = """
        INSERT INTO Grades VALUES (:github, :title, :grade)"""
    db.session.execute(QUERY, {'github': github,
                               'title': title,
                               'grade': grade})
    db.session.commit()

    print "Successfully added grade for %s on %s project." % (github, title)


def get_all_grades_for_stud(github):
    """Return all grades for a single student.

    Prints one line per project, with that project's title and grade."""

    QUERY = """
        SELECT project_title, grade 
        FROM grades
        WHERE student_github = :github
        """
    db_cursor = db.session.execute (QUERY, {'github': github})
    results = db_cursor.fetchall()
    for stud in range(0,len(results)):
        print results[stud][0], results[stud][1]


def testy(first_name):
    """dummy function for writing tests"""

    QUERY = """
        SELECT github 
        FROM students
        WHERE first_name = :first_name
        """
    db_cursor = db.session.execute (QUERY, {'first_name': first_name})
    results = db_cursor.fetchone()
    print results[0]


def handle_input():
    """Main loop.

    Repeatedly prompt for commands, performing them, until 'quit' is received as a
    command."""

    command = None

    while command != "quit":
        input_string = raw_input("HBA Database> ")
        tokens = input_string.split()
        command = tokens[0]
        args = tokens[1:]

        try:
            if command == "student":
                github = args[0]
                get_student_by_github(github)

            elif command == "new_student":
                first_name, last_name, github = args   # unpack!
                make_new_student(first_name, last_name, github)

            elif command == "project":
                title = args[0]
                get_project_by_title(title)

            elif command == "get_grade":
                github, title = args
                get_grade_by_github_title(github, title)

            elif command == "ass_grade":
                github, title, grade = args
                assign_grade(github, title, grade)

            elif command == "stud_grade":
                github = args[0]
                get_all_grades_for_stud(github)

            elif command == "test":
                first_name = args[0]
                testy(first_name)

            else:
                if command != "quit":
                    print "Invalid Entry. Try again."

        except:
            e = sys.exc_info()[0]
            print " NEW Invalid Entry. Try again."


if __name__ == "__main__":
    app = Flask(__name__)
    connect_to_db(app)

    handle_input()

    db.session.close()
