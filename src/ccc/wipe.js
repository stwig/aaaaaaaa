// src/components/WipeButton.js
import React from 'react';
import axios from 'axios';

function WipeButton() {
    const handleWipe = async () => {
        try {
            const response = await axios.delete('/api/wipe');
            alert(response.data.message);
        } catch (error) {
            console.error('Error wiping database and files:', error);
            alert('Error wiping database and files');
        }
    };

    return (
        <button onClick={handleWipe}>Wipe File Database</button>
    );
}

export default WipeButton;
