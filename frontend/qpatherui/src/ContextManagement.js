import React from 'react';

const ContextManagement = ({ contextText, setContextText, setView }) => {
  const handleContextSave = () => {
    alert("Context saved: " + contextText);
    setView("home");
  };

  const handleContextCancel = () => {
    setContextText("");
    setView("home");
  };

  return (
    <div className="context-management">
      <h3>Context</h3>
      <textarea
        placeholder="Enter context here..."
        value={contextText}
        onChange={(e) => setContextText(e.target.value)}
      ></textarea>
      <div className="button-group">
        <button onClick={handleContextSave}>Save</button>
        <button onClick={handleContextCancel}>Cancel</button>
      </div>
    </div>
  );
};

export default ContextManagement;
