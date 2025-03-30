from datetime import date
from extensions import db
from .user import User
from .course import Subject, Chapter, Quiz
from .question import Question, Option


def init_db(app):
    """Initialize the database and create tables"""
    db.init_app(app)
    with app.app_context():
        print("Creating database tables...")
        db.create_all()

        admin_email = "admin@quiz.com"
        admin_pass = "admin123"

        existing_admin = User.query.filter_by(email=admin_email).first()

        if not existing_admin:
            print(f"Admin user ({admin_email}) not found. Creating...")
            admin = User(
                email=admin_email,
                full_name="Admin User",
                role="admin",
                dob=date(1990, 1, 1),
            )
            admin.set_password(admin_pass)
            db.session.add(admin)
            db.session.commit()
            print(f"Admin user ({admin_email}) created successfully.")
        else:
            print(f"Admin user ({admin_email}) already exists.")

        # --- Seed Student User ---
        student_email = "student@quiz.com"
        student_pass = "student123"
        existing_student = User.query.filter_by(email=student_email).first()

        if not existing_student:
            student = User(
                email=student_email,
                full_name="Student User",
                role="student",
                dob=date(2002, 5, 15),
            )
            student.set_password(student_pass)
            db.session.add(student)
        else:
            print(f"Student user ({student_email}) already exists.")

        # --- Seed Subject ---
        subject_name = "Basic Python"
        seeded_subject = Subject.query.filter_by(name=subject_name).first()
        if not seeded_subject:
            print(f"Subject '{subject_name}' not found. Creating...")
            seeded_subject = Subject(
                name=subject_name,
                description="Fundamentals of the Python programming language.",
            )
            db.session.add(seeded_subject)
            print(f"Subject '{subject_name}' queued for creation.")
            # We need to flush to get the ID for the chapter if committing at end
            db.session.flush()
        else:
            print(f"Subject '{subject_name}' already exists.")

        # --- Seed Chapter (requires Subject) ---
        chapter_name = "Data Types"
        seeded_chapter = Chapter.query.filter_by(
            name=chapter_name, subject_id=seeded_subject.id
        ).first()
        if not seeded_chapter and seeded_subject:
            print(f"Chapter '{chapter_name}' not found. Creating...")
            seeded_chapter = Chapter(
                name=chapter_name,
                description="Integers, Floats, Strings, Booleans, Lists, Dictionaries.",
                subject_id=seeded_subject.id,
            )
            db.session.add(seeded_chapter)
            print(f"Chapter '{chapter_name}' queued for creation.")
            db.session.flush()
        elif seeded_chapter:
            print(f"Chapter '{chapter_name}' already exists.")
        else:
            print(
                f"Skipping chapter seeding as subject '{subject_name}' wasn't found/created."
            )

        # --- Seed Quiz (requires Chapter) ---
        quiz_title = "Python Data Types Quiz"
        seeded_quiz = Quiz.query.filter_by(
            title=quiz_title, chapter_id=seeded_chapter.id if seeded_chapter else None
        ).first()
        if not seeded_quiz and seeded_chapter:
            print(f"Quiz '{quiz_title}' not found. Creating...")
            seeded_quiz = Quiz(
                title=quiz_title,
                description="Test your knowledge of basic Python data types.",
                chapter_id=seeded_chapter.id,
                time_duration=10,
                remarks="Focus on definitions and usage.",
                is_published=True,
            )
            db.session.add(seeded_quiz)
            print(f"Quiz '{quiz_title}' queued for creation.")
            db.session.flush()
        elif seeded_quiz:
            print(f"Quiz '{quiz_title}' already exists.")
        else:
            print(
                f"Skipping quiz seeding as chapter '{chapter_name}' wasn't found/created."
            )

        # --- Seed Questions and Options (requires Quiz) ---
        if seeded_quiz and not Question.query.filter_by(quiz_id=seeded_quiz.id).first():
            print(f"Seeding questions for Quiz ID: {seeded_quiz.id}...")

            q1_text = "Which data type is used to store whole numbers?"
            q1 = Question(
                quiz_id=seeded_quiz.id,
                question_text=q1_text,
                points=1,
            )
            db.session.add(q1)
            db.session.flush()
            opt1_1 = Option(question_id=q1.id, option_text="float", is_correct=False)
            opt1_2 = Option(question_id=q1.id, option_text="int", is_correct=True)
            opt1_3 = Option(question_id=q1.id, option_text="str", is_correct=False)
            opt1_4 = Option(question_id=q1.id, option_text="bool", is_correct=False)
            db.session.add_all([opt1_1, opt1_2, opt1_3, opt1_4])
            print(f"  - Added Question: '{q1_text}' with options.")

            q2_text = "What is the boolean value of an empty string ('')?"
            q2 = Question(
                quiz_id=seeded_quiz.id,
                question_text=q2_text,
                points=2,
            )
            db.session.add(q2)
            db.session.flush()
            # Options for Q2
            opt2_1 = Option(question_id=q2.id, option_text="True", is_correct=False)
            opt2_2 = Option(question_id=q2.id, option_text="False", is_correct=True)
            opt2_3 = Option(question_id=q2.id, option_text="None", is_correct=False)
            db.session.add_all([opt2_1, opt2_2, opt2_3])
            print(f"  - Added Question: '{q2_text}' with options.")

        elif seeded_quiz:
            print(f"Questions for Quiz ID: {seeded_quiz.id} already exist.")
        else:
            print("Skipping question seeding as quiz wasn't found/created.")

        try:
            db.session.commit()
            print("All pending changes committed successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Error during commit: {e}")
            print("Changes rolled back.")

        print("--- Database Initialization Complete ---")

        db.session.commit()
