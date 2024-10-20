"use client";
import React, { useState } from 'react';


const UploadFlyer = () => {
    const [file, setFile] = useState(null);

    const changeHandler = (e) => {
        let selected = e.target.files[0];
        setFile(selected);
    };
    const handleSubmit = (e) => {
        e.preventDefault();
        console.log('submitted', file);
    };

    return (
        <form onSubmit={handleSubmit}>
            <input type="file" onChange={changeHandler} />
            <button type="submit">Upload</button>
        </form>
    );
};

export default UploadFlyer