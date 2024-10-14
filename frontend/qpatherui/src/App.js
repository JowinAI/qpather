import React, { useState } from 'react';
import './App.css';
import Sidebar from './Sidebar';
import TeamManagement from './TeamManagement';
import ContextManagement from './ContextManagement';
import QuestionForm from './QuestionForm';
import QuestionGrid from './QuestionGrid';

function App() {
  const [view, setView] = useState("home"); // Tracks the current view
  const [questionsList, setQuestionsList] = useState([]);
  const [teamMembers, setTeamMembers] = useState([]); // Stores team members
  const [contextText, setContextText] = useState(""); // Stores context text
  const [openQuestions] = useState(["Question 1", "Question 2", "Question 3"]); // Static open requests for now

  // State to control visibility of the question form
  const [showQuestionForm, setShowQuestionForm] = useState(false);

  // Handle "Start New Question" button click
  const handleNewQuestionClick = () => {
    setShowQuestionForm(true); // Show the form when button is clicked
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <Sidebar setView={setView} />

      {/* Main content */}
      <div className="main-content">
        {view === "home" && (
          <div className="left-content">
            {/* Start New Question button */}
            {!showQuestionForm && (
              <>
                <button className="new-question-btn" onClick={handleNewQuestionClick}>
                  Start New Question
                </button>

                {/* Open Requests */}
                <div className="open-questions">
                  <h3>Open Requests</h3>
                  <ul>
                    {openQuestions.map((question, index) => (
                      <li key={index}>{question}</li>
                    ))}
                  </ul>
                </div>
              </>
            )}

            {/* Question Form (only shown when the user clicks "Start New Question") */}
            {showQuestionForm && (
              <>
                <QuestionForm setQuestionsList={setQuestionsList} setShowQuestionForm={setShowQuestionForm} />

                {/* Questions Grid (only shown if there are questions returned from ChatGPT API) */}
                {questionsList.length > 0 && (
                  <QuestionGrid questionsList={questionsList} setQuestionsList={setQuestionsList} />
                )}
              </>
            )}
          </div>
        )}

        {/* Team Management View */}
        {view === "team" && (
          <TeamManagement teamMembers={teamMembers} setTeamMembers={setTeamMembers} setView={setView} />
        )}

        {/* Context Management View */}
        {view === "context" && (
          <ContextManagement contextText={contextText} setContextText={setContextText} setView={setView} />
        )}
      </div>
    </div>
  );
}

export default App;
