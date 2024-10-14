import React, { useState } from 'react';
import { getChatGPTResponse } from './ChatGPTApi';

const QuestionForm = ({ setQuestionsList, setShowQuestionForm }) => {
  const [newQuestion, setNewQuestion] = useState("");
  const [loading, setLoading] = useState(false);

  const context = "The user is asking for guidance. Need to help with answering the right questions to my team members.";
  const instruction = "Please respond with a JSON array of questions to ask others about this content. Limit 5 answers.";

  const handleAnalyzeClick = async () => {
    if (newQuestion.trim()) {
      setLoading(true);
      const questions = await getChatGPTResponse(context, newQuestion, instruction);
      setLoading(false);
      if (questions.length > 0) {
        setQuestionsList(questions);
        // Keep the form visible, do not hide it after analysis
      } else {
        alert("No questions received. Please try again.");
      }
    } else {
      alert("Please enter a valid question.");
    }
  };

  // Handle cancel to return to Start New Question and Open Requests
  const handleCancelClick = () => {
    setNewQuestion(""); // Reset the form input
    setQuestionsList([]); // Clear the questions
    setShowQuestionForm(false); // Hide the form and return to the Start New Question button
  };

  return (
    <div className="new-question-area">
      <textarea
        placeholder="What is in your mind?"
        value={newQuestion}
        onChange={(e) => setNewQuestion(e.target.value)}
      ></textarea>
      <div className="button-group">
        <button className="analyze-btn" onClick={handleAnalyzeClick}>
          {loading ? "Analyzing..." : "Analyze"}
        </button>
        <button className="cancel-btn" onClick={handleCancelClick}>
          Cancel
        </button>
      </div>
    </div>
  );
};

export default QuestionForm;
