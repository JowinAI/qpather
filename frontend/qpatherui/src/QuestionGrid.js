import React, { useState } from 'react';
import axios from 'axios';

const QuestionGrid = ({ questionsList, setQuestionsList }) => {
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Handle changes in the "Assign To" textbox (comma-separated emails)
  const handleAssignToChange = (index, value) => {
    const updatedQuestions = [...questionsList.Questions];
    updatedQuestions[index].AssignedUsers = value.split(',').map(email => email.trim());
    setQuestionsList({
      ...questionsList,
      Questions: updatedQuestions
    });
  };

  // Handle changes in the question text
  const handleQuestionTextChange = (index, value) => {
    const updatedQuestions = [...questionsList.Questions];
    updatedQuestions[index].questionText = value; // Update question text
    setQuestionsList({
      ...questionsList,
      Questions: updatedQuestions
    });
  };

  // Handle save button to send data to API
  const handleSave = async () => {
    setIsSubmitting(true);

    // Prepare the payload for the API call
    const assignmentsPayload = questionsList.Questions.map((question, index) => ({
      QuestionText: question.questionText,
      AssignedUsers: Array.isArray(question.AssignedUsers) ? question.AssignedUsers : question.AssignedUsers ? question.AssignedUsers.split(",") : [],  // Ensure it's an array
      Order: question.Order || index + 1,  // Ensure the order is set
      CreatedBy: "admin@example.com",  // Replace with actual CreatedBy user
      CreatedAt: new Date().toISOString(),  // Current timestamp
    }));

    // Final payload structure matching the backend schema
    const finalPayload = {
      Goal: questionsList.Goal,  // Include the common Goal
      Assignments: assignmentsPayload, // List of assignments
      DueDate: new Date().toISOString(),
      InitiatedBy: "admin@example.com",
      GoalDescription: questionsList.Goal,
      OrganizationId: 1
    };

    try {
      const apiUrl = `${process.env.REACT_APP_API_BASE_URL}/assignments/bulk-with-responses`;
      const response = await axios.post(apiUrl, finalPayload);
      console.log('Response data:', response.data);
      alert('Assignments and responses successfully created!');
    } catch (error) {
      console.error('Error submitting assignments:', error);
      alert('An error occurred while submitting the data.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle cancel button
  const handleCancel = () => {
    setQuestionsList({
      Goal: null,
      Questions: []
    }); // Reset the list
  };

  return (
    questionsList.Questions.length > 0 && (
      <div className="questions-grid">
        <h3>Suggested Questions for {questionsList.Goal}</h3>
        <table>
          <thead>
            <tr>
              <th>Question</th>
              <th>Assign To (Comma-separated emails)</th>
            </tr>
          </thead>
          <tbody>
            {questionsList.Questions.map((question, index) => (
              <tr key={index}>
                <td>
                  <textarea
                    value={question.questionText}
                    onChange={(e) => handleQuestionTextChange(index, e.target.value)}
                    rows={3}  // Set multiline
                    style={{ width: '400px' }}  // Double the width
                  />
                </td>
                <td>
                  <input
                    type="text"
                    value={question.AssignedUsers ? question.AssignedUsers.join(', ') : ''}
                    placeholder="Enter emails, comma-separated"
                    onChange={(e) => handleAssignToChange(index, e.target.value)}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <button onClick={handleSave} disabled={isSubmitting}>
          {isSubmitting ? 'Saving...' : 'Save'}
        </button>
        <button onClick={handleCancel} disabled={isSubmitting}>
          Cancel
        </button>
      </div>
    )
  );
};

export default QuestionGrid;
