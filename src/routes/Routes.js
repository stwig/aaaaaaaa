// src/routes/Routes.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import PDFList from '../ccc/pdfDisplay';
import PDFView from '../ccc/PDFViewer';
import FileUpload from '../ccc/FileUpload';

function AppRoutes() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<FileUpload />} />
                <Route path="/cases" element={<PDFList />} />
                <Route path="/cases/:caseId" element={<PDFView />} />
            </Routes>
        </Router>
    );
}

export default AppRoutes;
