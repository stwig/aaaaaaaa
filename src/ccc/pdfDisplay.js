// src/components/CaseList.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

function CaseList() {
    const [cases, setCases] = useState([]);

    useEffect(() => {
        const fetchCases = async () => {
            try {
                const response = await axios.get('/api/cases');
                setCases(response.data);
            } catch (error) {
                console.error('Error fetching cases:', error);
            }
        };

        fetchCases();
    }, []);

    return (
        <div>
            <h2>Cases</h2>
            <ul>
                {cases.map((caseItem, index) => (
                    <li key={index}>
                        <Link to={`/cases/${caseItem.case}`}>{caseItem.case}</Link>
                    </li>
                ))}
            </ul>
            <a href="/">Back</a>

        </div>
    );
}

export default CaseList;



