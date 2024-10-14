import React from 'react';

const QuestionGrid = ({ questionsList, setQuestionsList }) => {
  const users = ["User 1", "User 2", "User 3"];

  const handleAssignToChange = (index, value) => {
    const updatedQuestions = [...questionsList];
    updatedQuestions[index].assignedTo = value;
    setQuestionsList(updatedQuestions);
  };

  return (
    questionsList.length > 0 && (
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
                    onChange={(e) => handleAssignToChange(index, e.target.value)}
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
    )
  );
};

export default QuestionGrid;
