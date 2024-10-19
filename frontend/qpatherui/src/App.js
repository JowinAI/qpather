import React, { useState } from 'react';
import { Button, Checkbox, FormControl, FormControlLabel, InputLabel, MenuItem, Select, TextField, Typography, List, ListItem, ListItemText, Box, CssBaseline, Container } from '@mui/material';
import { Col, Row } from 'react-bootstrap';
import Sidebar from './Sidebar';
import TeamManagement from './TeamManagement';
import OrgSettings from './OrgSettings';
import UserSettings from './UserSettings';
import QuestionForm from './QuestionForm';
import QuestionGrid from './QuestionGrid';
import OrgChartPage from './OrgChart';
import './App.css';

function App() {
  const [view, setView] = useState("home");
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [questionAnswers, setQuestionAnswers] = useState({});
  const [forwardedQuestions, setForwardedQuestions] = useState([]);
  const [assignedUser, setAssignedUser] = useState("");
  const [openRequests] = useState(["Request 1", "Request 2", "Request 3"]);
  const [teamMembers] = useState(["User 1", "User 2", "User 3"]);
  const [showQuestionForm, setShowQuestionForm] = useState(false);
  const [questionsList, setQuestionsList] = useState({
    Goal: null,
    Questions: [],
    GoalDescription: null,
  });

  // Handle selecting an open request
  const handleRequestClick = (request) => {
    setSelectedRequest(request);
    setQuestionAnswers({});
    setForwardedQuestions([]);
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
    setSelectedRequest(null);
    setQuestionAnswers({});
    setForwardedQuestions([]);
    setAssignedUser("");
  };

  // Handle "Start New Question" button click
  const handleNewQuestionClick = () => {
    setShowQuestionForm(true);
  };

  const renderMainContent = () => {
    if (view === "home") {
      return (
        <Container>
          {!showQuestionForm && !selectedRequest && (
            <>
              <Button variant="contained" color="primary" onClick={handleNewQuestionClick}>
                New Goal
              </Button>
              <Typography variant="h6">Open Requests</Typography>
              <List>
                {openRequests.map((request, index) => (
                  <ListItem button="true" key={index} onClick={() => handleRequestClick(request)}>
                    <ListItemText primary={request} />
                  </ListItem>
                ))}
              </List>
            </>
          )}

          {showQuestionForm && !selectedRequest && (
            <>
              <QuestionForm setQuestionsList={setQuestionsList} setShowQuestionForm={setShowQuestionForm} />
              {questionsList.Questions.length > 0 && (
                <QuestionGrid questionsList={questionsList} setQuestionsList={setQuestionsList} />
              )}
            </>
          )}

          {selectedRequest && (
            <>
              <Typography variant="h6">{selectedRequest}</Typography>
              <List>
                {["Question 1", "Question 2", "Question 3"].map((question, index) => (
                  <ListItem key={index}>
                    <ListItemText primary={question} />
                    <TextField
                      label="Enter your answer"
                      value={questionAnswers[index] || ""}
                      onChange={(e) => setQuestionAnswers({ ...questionAnswers, [index]: e.target.value })}
                    />
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={forwardedQuestions.includes(index)}
                          onChange={() => setForwardedQuestions(prev =>
                            prev.includes(index) ? prev.filter((i) => i !== index) : [...prev, index]
                          )}
                        />
                      }
                      label="Forward"
                    />
                  </ListItem>
                ))}
              </List>
              <FormControl fullWidth>
                <InputLabel>Assign to</InputLabel>
                <Select
                  value={assignedUser}
                  onChange={(e) => setAssignedUser(e.target.value)}
                  disabled={forwardedQuestions.length === 0}
                >
                  <MenuItem value="">
                    <em>Select User</em>
                  </MenuItem>
                  {teamMembers.map((user, index) => (
                    <MenuItem key={index} value={user}>
                      {user}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <Button variant="contained" color="primary" onClick={handleSave}>
                Save
              </Button>
            </>
          )}
        </Container>
      );
    }

    if (view === "team") {
      return <TeamManagement teamMembers={teamMembers} setTeamMembers={() => { }} setView={setView} />;
    }

    if (view === "orgSettings") {
      return <OrgSettings />;
    }

    if (view === "userSettings") {
      return <UserSettings />;
    }

    if (view === "orgChart") {
      return <OrgChartPage />;
    }

    return null;
  };

  return (
    <Container fluid>
      <Row>
        <Col md={20} className="sidebar-column">
          <Sidebar setView={setView} />
        </Col>
        <Col md={20} style={{ marginTop: '20px' }}> {/* Add top margin to avoid sticking to top */}
          <Box className="content-box" style={{ paddingLeft: '5px' }}> {/* Padding for the left alignment */}
            {renderMainContent()}
          </Box>
        </Col>
      </Row>
    </Container>
  );
}

export default App;
