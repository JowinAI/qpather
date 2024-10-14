import React, { useState } from 'react';
import './App.css';
import { getChatGPTResponse } from './ChatGPTApi'; // Assuming you've defined this function to call ChatGPT API

function App() {
  const [recentItems] = useState(["Item 1", "Item 2", "Item 3"]);
  const [openQuestions] = useState(["Question 1", "Question 2", "Question 3"]);
  const [showQuestionForm, setShowQuestionForm] = useState(false);
  const [newQuestion, setNewQuestion] = useState("");
  const [questionsList, setQuestionsList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [view, setView] = useState("home"); // Used to track the current view (home, team, context)
  const [teamMembers, setTeamMembers] = useState([]); // Stores the team members
  const [contextText, setContextText] = useState(""); // Stores context text
  const [newTeamMember, setNewTeamMember] = useState({ name: "", email: "", department: "", capabilities: "" });

  const departments = ["Finance", "Operations", "Technology", "Purchase"];
  const users = ["User 1", "User 2", "User 3"];
  const context = "The user is asking for guidance. Need to help with answering the right questions to my team members.";
  const instruction = "Please respond with a JSON array of questions to ask others about this content. Limit 5 answers.";

  const handleNewQuestionClick = () => {
    setShowQuestionForm(true); 
  };

  const handleCancelClick = () => {
    setShowQuestionForm(false);
    setNewQuestion("");
    setQuestionsList([]);
  };

  const handleAnalyzeClick = async () => {
    if (newQuestion.trim()) {
      setLoading(true);
      const questions = await getChatGPTResponse(context, newQuestion, instruction);
      setLoading(false);
      if (questions.length > 0) {
        setQuestionsList(questions);
      } else {
        alert("No questions received. Please try again.");
      }
    } else {
      alert("Please enter a valid question.");
    }
  };

  const handleAddTeamMember = () => {
    setTeamMembers([...teamMembers, newTeamMember]);
    setNewTeamMember({ name: "", email: "", department: "", capabilities: "" });
  };

  const handleContextSave = () => {
    alert("Context saved: " + contextText);
    setView("home");
  };

  const handleContextCancel = () => {
    setContextText("");
    setView("home");
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className="sidebar">
        <h3>Recent Items</h3>
        <ul>
          {recentItems.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>

        <h3>Settings</h3>
        <ul>
          <li onClick={() => setView("team")}>Team</li>
          <li onClick={() => setView("context")}>Context</li>
        </ul>
      </div>

      {/* Main content */}
      <div className="main-content">
        {view === "home" && (
          <div className="left-content">
            {!showQuestionForm && (
              <>
                <button className="new-question-btn" onClick={handleNewQuestionClick}>
                  Start New Question
                </button>

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

            {showQuestionForm && (
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
            )}

            {questionsList.length > 0 && (
              <div className="questions-grid">
                <h3>Suggested Questions</h3>
                <table>
                  <thead>
                    <tr>
                      <th>Question</th>
                      <th>Assign To</th>
                    </tr>
                  </thead>
                  <tbody>
                    {questionsList.map((question, index) => (
                      <tr key={index}>
                        <td>
                          <input
                            type="text"
                            value={question}
                            onChange={(e) => {
                              const updatedQuestions = [...questionsList];
                              updatedQuestions[index] = e.target.value;
                              setQuestionsList(updatedQuestions);
                            }}
                          />
                        </td>
                        <td>
                          <select
                            onChange={(e) => {
                              const updatedQuestions = [...questionsList];
                              updatedQuestions[index].assignedTo = e.target.value;
                              setQuestionsList(updatedQuestions);
                            }}
                          >
                            <option value="">Select User</option>
                            {users.map((user, i) => (
                              <option key={i} value={user}>
                                {user}
                              </option>
                            ))}
                          </select>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Team Management View */}
        {view === "team" && (
          <div className="team-management">
            <h3>Team Management</h3>
            <div>
              <input
                type="text"
                placeholder="Name"
                value={newTeamMember.name}
                onChange={(e) => setNewTeamMember({ ...newTeamMember, name: e.target.value })}
              />
              <input
                type="email"
                placeholder="Email"
                value={newTeamMember.email}
                onChange={(e) => setNewTeamMember({ ...newTeamMember, email: e.target.value })}
              />
              <select
                value={newTeamMember.department}
                onChange={(e) => setNewTeamMember({ ...newTeamMember, department: e.target.value })}
              >
                <option value="">Select Department</option>
                {departments.map((dept, index) => (
                  <option key={index} value={dept}>
                    {dept}
                  </option> 
                ))}
              </select>
              <input
                type="text"
                placeholder="Capabilities"
                value={newTeamMember.capabilities}
                onChange={(e) => setNewTeamMember({ ...newTeamMember, capabilities: e.target.value })}
              />
              <button onClick={handleAddTeamMember}>Add Team Member</button>
            </div>
            <h3>Team Members</h3>
            <ul>
              {teamMembers.map((member, index) => (
                <li key={index}>
                  {member.name} - {member.email} - {member.department} - {member.capabilities}
                </li>
              ))}
            </ul>
            <button onClick={() => setView("home")}>Back</button>
          </div>
        )}

        {/* Context View */}
        {view === "context" && (
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
        )}
      </div>
    </div>
  );
}

export default App;
