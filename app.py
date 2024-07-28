from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import base64
from models import db, PDF, User

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pdfs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()
    # Initialize user if not already present
    if not User.query.get('testuser'):
        user = User(username='testuser')
        db.session.add(user)
        db.session.commit()

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Define the UserAnswer model
class UserAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), nullable=False)  # Use username or a unique identifier
    pdf_id = db.Column(db.Integer, db.ForeignKey('pdf.id'), nullable=False)
    answer = db.Column(db.String(255), nullable=False)

    pdf = db.relationship('PDF', backref=db.backref('user_answers', lazy=True))

@app.route('/api/upload', methods=['POST'])
def upload_pdfs():
    if 'files[]' not in request.files:
        return jsonify({"message": "No files part"}), 400

    files = request.files.getlist('files[]')

    if len(files) == 0:
        return jsonify({"message": "No selected files"}), 400

    case_field = request.form.get('case')
    pdf_ids = []
    try:
        for file in files:
            if file.filename == '':
                continue

            content = file.read()
            metadata = {
                "size": len(content),
                "type": file.content_type
            }
            description = request.form.get(f'description_{file.filename}')
            question = request.form.get(f'question_{file.filename}')
            answer = request.form.get(f'answer_{file.filename}')

            new_pdf = PDF(
                filename=file.filename,
                content=content,
                pdf_metadata=metadata,
                description=description,
                question=question,
                case_field=case_field,
                answer=answer
            )
            db.session.add(new_pdf)
            pdf_ids.append(new_pdf.id)

        # Update User's PDF list
        user = User.query.get('testuser')
        if user:
            user.pdf_ids = list(set(user.pdf_ids or [] + pdf_ids))
            db.session.commit()
        else:
            user = User(username='testuser', pdf_ids=pdf_ids)
            db.session.add(user)
            db.session.commit()

        return jsonify({"message": "Files uploaded successfully"}), 200
    except Exception as e:
        return jsonify({"message": f"Error uploading files: {str(e)}"}), 500

@app.route('/api/cases', methods=['GET'])
def list_cases():
    try:
        # Query distinct case fields
        cases = db.session.query(PDF.case_field).distinct().all()
        case_list = [{'case': case[0]} for case in cases if case[0] is not None]
        return jsonify(case_list), 200
    except Exception as e:
        return jsonify({"message": f"Error retrieving cases: {str(e)}"}), 500

@app.route('/api/pdfs', methods=['GET'])
def get_pdfs_by_case():
    case_id = request.args.get('case')  # Get the case ID from query parameters
    if not case_id:
        return jsonify({"message": "Case ID is required"}), 400

    try:
        pdfs = PDF.query.filter_by(case_field=case_id).all()  # Filter PDFs by case ID
        pdf_list = [
            {
                "id": pdf.id,
                "filename": pdf.filename,
                "content": base64.b64encode(pdf.content).decode('utf-8'),  # Encode binary content to Base64
                "description": pdf.description,
                "question": pdf.question,
                "answer": pdf.answer,
                "pdf_metadata": pdf.pdf_metadata
            } for pdf in pdfs
        ]
        return jsonify(pdf_list), 200
    except Exception as e:
        return jsonify({"message": f"Error retrieving PDFs: {str(e)}"}), 500

@app.route('/api/pdfs/<int:pdf_id>', methods=['GET'])
def get_pdf(pdf_id):
    try:
        pdf = PDF.query.get_or_404(pdf_id)
        pdf_content = base64.b64encode(pdf.content).decode('utf-8')  # Encode binary content to Base64
        return jsonify({
            "filename": pdf.filename,
            "content": pdf_content,
            "description": pdf.description,
            "question": pdf.question,
            "answer": pdf.answer,
            "pdf_metadata": pdf.pdf_metadata
        }), 200
    except Exception as e:
        return jsonify({"message": f"Error retrieving PDF: {str(e)}"}), 500

@app.route('/api/pdfs/<int:pdf_id>/answer', methods=['POST'])
def submit_answer(pdf_id):
    user_id = 'testuser'  # Hardcoded for testing purposes
    user_answer = request.json.get('answer')

    if user_answer is None:
        return jsonify({"message": "No answer provided"}), 400

    try:
        pdf = PDF.query.get_or_404(pdf_id)
        is_correct = user_answer == pdf.answer

        # Save the user's answer
        existing_answer = UserAnswer.query.filter_by(user_id=user_id, pdf_id=pdf_id).first()
        if existing_answer:
            existing_answer.answer = user_answer
        else:
            new_answer = UserAnswer(user_id=user_id, pdf_id=pdf_id, answer=user_answer)
            db.session.add(new_answer)

        db.session.commit()

        return jsonify({"is_correct": is_correct, "correct_answer": pdf.answer}), 200
    except Exception as e:
        return jsonify({"message": f"Error submitting answer: {str(e)}"}), 500

@app.route('/api/pdfs/<int:pdf_id>/answers', methods=['GET'])
def get_user_answers(pdf_id):
    user_id = 'testuser'  # Hardcoded for testing purposes
    try:
        answers = UserAnswer.query.filter_by(pdf_id=pdf_id, user_id=user_id).all()
        answers_list = [{"user_id": answer.user_id, "answer": answer.answer} for answer in answers]
        return jsonify(answers_list), 200
    except Exception as e:
        return jsonify({"message": f"Error retrieving answers: {str(e)}"}), 500

@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({"message": "Pong"})

@app.route('/api/wipe', methods=['DELETE'])
def wipe_database():
    # Delete all records from the database
    try:
        PDF.query.delete()  # Delete all records from the PDF table
        UserAnswer.query.delete()  # Delete all records from the UserAnswer table
        db.session.commit()
    except Exception as e:
        return jsonify({"message": f"Error wiping database: {str(e)}"}), 500

    # Remove all files from the upload directory
    try:
        upload_folder = app.config['UPLOAD_FOLDER']
        for filename in os.listdir(upload_folder):
            file_path = os.path.join(upload_folder, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
    except Exception as e:
        return jsonify({"message": f"Error deleting files: {str(e)}"}), 500

    return jsonify({"message": "Database and files wiped successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
