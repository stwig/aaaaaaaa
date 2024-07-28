
import React, { useState } from 'react';
import axios from 'axios';

function FileUpload() {
    const [files, setFiles] = useState([]);
    const [caseField, setCaseField] = useState('');
    const [descriptions, setDescriptions] = useState({});
    const [questions, setQuestions] = useState({});
    const [answers, setAnswers] = useState({});

    const handleFileChange = (event) => {
        setFiles(Array.from(event.target.files));
    };

    const handleFieldChange = (e, fieldType, fileName) => {
        const { value } = e.target;
        if (fieldType === 'description') {
            setDescriptions({ ...descriptions, [fileName]: value });
        } else if (fieldType === 'question') {
            setQuestions({ ...questions, [fileName]: value });
        } else if (fieldType === 'answer') {
            setAnswers({ ...answers, [fileName]: value });
        }
    };

    const handleSubmit = async (event) => {
        event.preventDefault();

        const formData = new FormData();
        files.forEach((file) => {
            formData.append('files[]', file);
            formData.append(`description_${file.name}`, descriptions[file.name] || '');
            formData.append(`question_${file.name}`, questions[file.name] || '');
            formData.append(`answer_${file.name}`, answers[file.name] || '');
        });
        formData.append('case', caseField);

        try {
            await axios.post('/api/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            alert('Files uploaded successfully');
        } catch (error) {
            console.error('Error uploading files:', error);
            alert('Error uploading files');
        }
    };

    return (
        <form onSubmit={handleSubmit}>
           
            <input type="file" multiple onChange={handleFileChange} />
            {files.map((file) => (
                <div key={file.name}>
                    <h3>{file.name}</h3>
                    <input
                        type="text"
                        placeholder="Description"
                        onChange={(e) => handleFieldChange(e, 'description', file.name)}
                    />
                    <input
                        type="text"
                        placeholder="Question"
                        onChange={(e) => handleFieldChange(e, 'question', file.name)}
                    />
                    <input
                        type="text"
                        placeholder="Answer"
                        onChange={(e) => handleFieldChange(e, 'answer', file.name)}
                    />
                </div>
            ))}
            <input
                type="text"
                placeholder="Case"
                value={caseField}
                onChange={(e) => setCaseField(e.target.value)}
            />
            <button type="submit">Upload</button>
            <a href="/cases">to List</a>
        </form>
    );
}

export default FileUpload;

