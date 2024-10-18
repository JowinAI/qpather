import React, { useState } from 'react';
import { getChatGPTResponse } from './ChatGPTApi';

const QuestionForm = ({ setQuestionsList, setShowQuestionForm }) => {
  const [newQuestion, setNewQuestion] = useState("");
  const [loading, setLoading] = useState(false);

  const context = "The user is asking for guidance. Need to help with answering the right questions to my team members.";
  const instruction = "Please respond with a JSON array of questions to ask others about this content. Limit 5 answers.";

  const handleAnalyzeClick = async () => {
    alert('hi1');
    if (newQuestion.trim()) {
      setLoading(true);
      const questions = await getChatGPTResponse(context, newQuestion, instruction);
      
      // Common goal for all questions
      const commonGoal = "Answer the questions to help forecast sales trends.";

      const questionsListNew = questions.map((question, index) => {
        return {
          questionText: question,
          Order: index + 1, // Dynamic index, starting from 1
          AssignedUsers: "" // Empty string for AssignedUsers
        };
      });
  
      // Create the final object that contains the Goal and questions list
      const finalPayload = {
        Goal: commonGoal,
        Questions: questionsListNew,
        GoalDescription: commonGoal
      };
  
      setLoading(false);
      
      // Only set questionsList if there are questions
      if (questions.length > 0) {
        setQuestionsList(finalPayload);
        
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
