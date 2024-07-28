import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, Link } from 'react-router-dom';

function PDFView() {
    const { caseId } = useParams();
    const [pdfs, setPdfs] = useState([]);
    const [selectedPdf, setSelectedPdf] = useState(null);
    const [userAnswer, setUserAnswer] = useState('');
    const [existingAnswers, setExistingAnswers] = useState([]);
    const [feedback, setFeedback] = useState('');

    useEffect(() => {
        const fetchPdfs = async () => {
            try {
                const response = await axios.get(`/api/pdfs?case=${caseId}`);
                setPdfs(response.data);
            } catch (error) {
                console.error('Error fetching PDFs:', error);
            }
        };

        if (caseId) {
            fetchPdfs();
        }
    }, [caseId]);

    const handlePdfClick = async (pdf) => {
        setSelectedPdf(pdf);

        try {
            // Fetch existing answers for the selected PDF
            const response = await axios.get(`/api/pdfs/${pdf.id}/answers`);
            setExistingAnswers(response.data);
        } catch (error) {
            console.error('Error fetching answers:', error);
        }
    };

    const handleSubmitAnswer = async () => {
        if (selectedPdf) {
            try {
                const userId = 'testuser'; // Hardcoded for testing purposes
                const response = await axios.post(`/api/pdfs/${selectedPdf.id}/answer`, {
                    answer: userAnswer
                });

                const { is_correct, correct_answer } = response.data;
                if (is_correct) {
                    setFeedback('Your answer is correct!');
                } else {
                    setFeedback(`Your answer is incorrect. The correct answer is: ${correct_answer}`);
                }

                // Refresh existing answers
                handlePdfClick(selectedPdf);

                setUserAnswer('');
            } catch (error) {
                console.error('Error submitting answer:', error);
                setFeedback('An error occurred while submitting the answer.');
            }
        }
    };

    return (
        <div style={{ display: 'flex' }}>
            <div style={{ flex: 1 }}>
                <h2>PDFs for Case: {caseId}</h2>
                <ul>
                    {pdfs.length > 0 ? (
                        pdfs.map((pdf) => (
                            <li key={pdf.id}>
                                <button onClick={() => handlePdfClick(pdf)}>
                                    {pdf.filename}
                                </button>
                            </li>
                        ))
                    ) : (
                        <p>No PDFs found for this case.</p>
                    )}
                </ul>
                <Link to="/">Back to Cases</Link>
            </div>
            <div style={{ flex: 1, paddingLeft: '20px' }}>
                {selectedPdf && (
                    <div>
                        <h3>Details for: {selectedPdf.filename}</h3>
                        <p><strong>Description:</strong> {selectedPdf.description}</p>
                        <p><strong>Question:</strong> {selectedPdf.question}</p>
                        <a href={`data:application/pdf;base64,${selectedPdf.content}`} download>
                            Download PDF
                        </a>
                        <div>
                            <h4>Submit Answer:</h4>
                            <textarea
                                value={userAnswer}
                                onChange={(e) => setUserAnswer(e.target.value)}
                                placeholder="Enter your answer here"
                            />
                            <button onClick={handleSubmitAnswer}>
                                Submit Answer
                            </button>
                            {feedback && <p>{feedback}</p>}
                        </div>
                        <div>
                            <h4>Previous Answers:</h4>
                            <ul>
                                {existingAnswers.length > 0 ? (
                                    existingAnswers.map((answer, index) => (
                                        <li key={index}>
                                            <strong>User:</strong> {answer.user_id} <br />
                                            <strong>Answer:</strong> {answer.answer}
                                        </li>
                                    ))
                                ) : (
                                    <p>No previous answers for this PDF.</p>
                                )}
                            </ul>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default PDFView;
