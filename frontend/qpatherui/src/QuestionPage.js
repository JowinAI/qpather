import React, { useState, useEffect } from 'react';
import { getChatGPTResponse } from './ChatGPTApi';  // Import the common API function

const ChatGPTQuestionsPage = ({ context, content, instruction }) => {
  const [questionsList, setQuestionsList] = useState([]);
  const [loading, setLoading] = useState(true); // Loading state

  // Use useEffect to call the API when the component mounts
  useEffect(() => {
    const fetchQuestions = async () => {
      const questions = await getChatGPTResponse(context, content, instruction);
      setQuestionsList(questions);
      setLoading(false); // Stop loading after API call
    };

    fetchQuestions();
  }, [context, content, instruction]);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="questions-page">
      <h3>Suggested Questions</h3>
      <div className="grid">
        {questionsList.length > 0 ? (
          questionsList.map((question, index) => (
            <div key={index} className="grid-item">
              {question}
            </div>
          ))
        ) : (
          <p>No questions found</p>
        )}
      </div>
    </div>
  );
};

export default ChatGPTQuestionsPage;
