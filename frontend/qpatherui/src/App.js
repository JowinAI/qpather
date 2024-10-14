import React, { useState } from 'react';
import './App.css';
import Sidebar from './Sidebar';
import TeamManagement from './TeamManagement';
import OrgSettings from './OrgSettings'; // Import OrgSettings component
import UserSettings from './UserSettings'; // Import UserSettings component
import QuestionForm from './QuestionForm';
import QuestionGrid from './QuestionGrid';
import OrgChartPage from './OrgChart'; // Import OrgChart component

function App() {
  const [view, setView] = useState("home"); // Tracks the current view
  const [selectedRequest, setSelectedRequest] = useState(null); // Tracks the selected open request
  const [questionAnswers, setQuestionAnswers] = useState({}); // Stores answers to questions
  const [forwardedQuestions, setForwardedQuestions] = useState([]); // Tracks forwarded questions
  const [assignedUser, setAssignedUser] = useState(""); // Stores assigned user for forwarding
  const [openRequests] = useState(["Request 1", "Request 2", "Request 3"]); // Static open requests
  const [teamMembers] = useState(["User 1", "User 2", "User 3"]); // List of team members for assignment
  const [showQuestionForm, setShowQuestionForm] = useState(false); // Controls visibility of the question form
  const [questionsList, setQuestionsList] = useState([]); // Stores questions for new question flow

  // Handle selecting an open request
  const handleRequestClick = (request) => {
    setSelectedRequest(request);
    setQuestionAnswers({}); // Reset answers when a new request is selected
    setForwardedQuestions([]); // Reset forwarded questions
  };

  // Handle answering a question
  const handleAnswerChange = (questionIndex, value) => {
    setQuestionAnswers({
      ...questionAnswers,
      [questionIndex]: value,
    });
  };

  // Handle forwarding a question
  const handleForwardChange = (questionIndex) => {
    setForwardedQuestions((prev) =>
      prev.includes(questionIndex)
        ? prev.filter((index) => index !== questionIndex) // Remove if already selected
        : [...prev, questionIndex] // Add if not selected
    );
  };

  // Handle saving the responses and forwarding
  const handleSave = () => {
    const answers = Object.entries(questionAnswers).map(([index, answer]) => ({
      question: `Question ${parseInt(index) + 1}`,
      answer,
      forwarded: forwardedQuestions.includes(parseInt(index)),
      assignedTo: forwardedQuestions.includes(parseInt(index)) ? assignedUser : null,
    }));
    console.log("Saved Answers: ", answers);
    alert("Answers saved successfully!");
    // Reset selections after saving
    setSelectedRequest(null);
    setQuestionAnswers({});
    setForwardedQuestions([]);
    setAssignedUser("");
  };

  // Handle "Start New Question" button click
  const handleNewQuestionClick = () => {
    setShowQuestionForm(true); // Show the form when button is clicked
  };

  // Render the main content based on the selected view
  const renderMainContent = () => {
    if (view === "home") {
      return (
        <div className="left-content">
          {/* Show the Start New Question button if form is not visible */}
          {!showQuestionForm && !selectedRequest && (
            <>
              <button className="new-question-btn" onClick={handleNewQuestionClick}>
                Start New Question
              </button>

              {/* Open Requests Section */}
              <div className="open-requests">
                <h3>Open Requests</h3>
                <ul>
                  {openRequests.map((request, index) => (
                    <li key={index} onClick={() => handleRequestClick(request)}>
                      {request}
                    </li>
                  ))}
                </ul>
              </div>
            </>
          )}

          {/* Show Question Form if "Start New Question" button was clicked */}
          {showQuestionForm && !selectedRequest && (
            <>
              <QuestionForm setQuestionsList={setQuestionsList} setShowQuestionForm={setShowQuestionForm} />

              {/* Display the question grid if there are questions returned from ChatGPT API */}
              {questionsList.length > 0 && (
                <QuestionGrid questionsList={questionsList} setQuestionsList={setQuestionsList} />
              )}
            </>
          )}

          {/* Show questions if a request is selected */}
          {selectedRequest && (
            <>
              <h3>{selectedRequest}</h3>
              <ul>
                {["Question 1", "Question 2", "Question 3"].map((question, index) => (
                  <li key={index}>
                    <p>{question}</p>
                    <input
                      type="text"
                      placeholder="Enter your answer"
                      value={questionAnswers[index] || ""}
                      onChange={(e) => handleAnswerChange(index, e.target.value)}
                    />
                    <label>
                      <input
                        type="checkbox"
                        checked={forwardedQuestions.includes(index)}
                        onChange={() => handleForwardChange(index)}
                      />
                      Forward
                    </label>
                  </li>
                ))}
              </ul>

              {/* Dropdown to assign to a user */}
              <div>
                <label>
                  Assign to:
                  <select
                    value={assignedUser}
                    onChange={(e) => setAssignedUser(e.target.value)}
                    disabled={forwardedQuestions.length === 0} // Only enable if there are forwarded questions
                  >
                    <option value="">Select User</option>
                    {teamMembers.map((user, index) => (
                      <option key={index} value={user}>
                        {user}
                      </option>
                    ))}
                  </select>
                </label>
              </div>

              {/* Save button */}
              <button onClick={handleSave}>Save</button>
            </>
          )}
        </div>
      );
    }

    // Render Team Management view
    if (view === "team") {
      return <TeamManagement teamMembers={teamMembers} setTeamMembers={() => {}} setView={setView} />;
    }

    // Render Org Settings view
    if (view === "orgSettings") {
      return <OrgSettings />;
    }

    // Render User Settings view
    if (view === "userSettings") {
      return <UserSettings />;
    }

    // Render Org Chart view
    if (view === "orgChart") {
      return <OrgChartPage />;  // Render the Org Chart component
    }

    return null; // Fallback in case no view matches
  };

  return (
    <div className="app-container">
      {/* Sidebar for navigation */}
      <Sidebar setView={setView} />

      {/* Main content area based on selected view */}
      <div className="main-content">{renderMainContent()}</div>
    </div>
  );
}

export default App;
