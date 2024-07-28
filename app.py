from flask import Flask, request, jsonify
#from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from models import db, PDF, User
import base64

app = Flask(__name__)
#CORS(app)

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

############################################################################################################
#upload
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
            user.pdf_ids.extend(pdf_ids)
            db.session.commit()
        else:
            user = User(username='testuser', pdf_ids=pdf_ids)
            db.session.add(user)
            db.session.commit()

        return jsonify({"message": "Files uploaded successfully"}), 200
    except Exception as e:
        return jsonify({"message": f"Error uploading files: {str(e)}"}), 500

#cases puilll
@app.route('/api/cases', methods=['GET'])
def list_cases():
    try:
        # Query distinct case fields
        cases = db.session.query(PDF.case_field).distinct().all()
        case_list = [{'case': case[0]} for case in cases if case[0] is not None]
        #print(cases)
        return jsonify(case_list), 200
    except Exception as e:
        return jsonify({"message": f"Error retrieving cases: {str(e)}"}), 500
    
##############################################################################################
#pdfs (ALL) pull
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

#specific pdf pull
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
    try:
        pdf = PDF.query.get_or_404(pdf_id)
        user_answer = request.json.get('answer')

        if user_answer is None:
            return jsonify({"message": "No answer provided"}), 400

        is_correct = user_answer == pdf.answer

        # Here you could store the user's answer if needed
        # For now, just return whether the answer is correct or not
        print(pdf.answer)
        return jsonify({"is_correct": is_correct, "correct_answer": pdf.answer}), 200
    except Exception as e:
        return jsonify({"message": f"Error submitting answer: {str(e)}"}), 500

##############################################################################################################################
#foir testing
@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({"message": "Pong"})

##############################################################################################################################

if __name__ == '__main__':
    app.run(debug=True)
