import React, { useState } from 'react';
import { Button, Checkbox, FormControl, FormControlLabel, InputLabel, MenuItem, Select, TextField, Typography, Container, List, ListItem, ListItemText, Box, CssBaseline } from '@mui/material';
import { styled, ThemeProvider, createTheme } from '@mui/material/styles';
import './App.css';
import Sidebar from './Sidebar';
import TeamManagement from './TeamManagement';
import OrgSettings from './OrgSettings'; // Import OrgSettings component
import UserSettings from './UserSettings'; // Import UserSettings component
import QuestionForm from './QuestionForm';
import QuestionGrid from './QuestionGrid';
import OrgChartPage from './OrgChart'; // Import OrgChart component

const drawerWidth = 240;

const Root = styled('div')(({ theme }) => ({
  display: 'flex',
}));

const Drawer = styled('div')(({ theme }) => ({
  width: drawerWidth,
  flexShrink: 0,
}));

const DrawerPaper = styled('div')(({ theme }) => ({
  width: drawerWidth,
}));

const Content = styled('main')(({ theme }) => ({
  flexGrow: 1,
  padding: theme.spacing(3),
  marginLeft: drawerWidth,
}));

const Toolbar = styled('div')(({ theme }) => theme.mixins.toolbar);
const theme = createTheme();

function App() {
  const [view, setView] = useState("home"); // Tracks the current view
  const [selectedRequest, setSelectedRequest] = useState(null); // Tracks the selected open request
  const [questionAnswers, setQuestionAnswers] = useState({}); // Stores answers to questions
  const [forwardedQuestions, setForwardedQuestions] = useState([]); // Tracks forwarded questions
  const [assignedUser, setAssignedUser] = useState(""); // Stores assigned user for forwarding
  const [openRequests] = useState(["Request 1", "Request 2", "Request 3"]); // Static open requests
  const [teamMembers] = useState(["User 1", "User 2", "User 3"]); // List of team members for assignment
  const [showQuestionForm, setShowQuestionForm] = useState(false); // Controls visibility of the question form
  const [questionsList, setQuestionsList] = useState({
    Goal: null,  // Default Goal to null, can be updated later
    Questions: [] , // Empty array for Questions
    GoalDescription:null
  });

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
                      onChange={(e) => handleAnswerChange(index, e.target.value)}
                    />
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={forwardedQuestions.includes(index)}
                          onChange={() => handleForwardChange(index)}
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
    <Root>
      <CssBaseline />
      <Drawer>
        <Sidebar setView={setView} />
      </Drawer>
      <Content>
        <Toolbar />
        {renderMainContent()}
      </Content>
    </Root>
  );
}

export default App;