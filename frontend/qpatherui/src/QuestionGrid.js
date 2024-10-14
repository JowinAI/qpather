import React, { useState } from 'react';

const QuestionGrid = ({ questions, handleBackClick }) => {
  // Sample list of users to assign questions to
  const [assignments, setAssignments] = useState(
    questions.map(() => ({ assignedTo: "" }))
  );

  // Handler to update the assigned user for a specific question
  const handleAssignmentChange = (index, assignedTo) => {
    const updatedAssignments = [...assignments];
    updatedAssignments[index].assignedTo = assignedTo;
    setAssignments(updatedAssignments);
  };

  return (
    <div className="question-grid-container">
      <h3>Suggested Questions</h3>
      <table className="question-grid">
        <thead>
          <tr>
            <th>Question</th>
            <th>Assign To</th>
          </tr>
        </thead>
        <tbody>
          {questions.map((question, index) => (
            <tr key={index}>
              <td>{question}</td>
              <td>
                <select
                  value={assignments[index].assignedTo}
                  onChange={(e) => handleAssignmentChange(index, e.target.value)}
                >
                  <option value="">Select User</option>
                  <option value="User 1">User 1</option>
                  <option value="User 2">User 2</option>
                  <option value="User 3">User 3</option>
                </select>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <button className="back-btn" onClick={handleBackClick}>
        Back
      </button>
    </div>
  );
};

export default QuestionGrid;
