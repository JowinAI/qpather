import React, { useState } from 'react';

const UserSettings = () => {
  const [isEditing, setIsEditing] = useState(false);

  const [userSettings, setUserSettings] = useState({
    role: ['Team Lead'],
    businessObjective: ['Increase Revenue'],
    challenges: ['Talent Retention'],
    kpis: ['Customer Satisfaction'],
    teamRoles: ['Developer', 'Manager'],
    priorityLevel: 'Urgent',
    complexityLevel: 'High',
    targetOutcome: ['Operational Improvement'],
    communicationStyle: 'Formal',
    goalTimeframe: '3 Months',
  });

  // Handle edit toggle
  const toggleEdit = () => {
    setIsEditing(!isEditing);
  };

  // Handle input change (in edit mode)
  const handleInputChange = (field, value) => {
    setUserSettings({
      ...userSettings,
      [field]: value,
    });
  };

  return (
    <div className="user-settings">
      <h3>User Settings</h3>
      {!isEditing ? (
        <>
          <p><strong>Role of User:</strong> {userSettings.role.join(', ')}</p>
          <p><strong>Business Objective:</strong> {userSettings.businessObjective.join(', ')}</p>
          <p><strong>Current Challenges:</strong> {userSettings.challenges.join(', ')}</p>
          <p><strong>Key Performance Indicators (KPIs):</strong> {userSettings.kpis.join(', ')}</p>
          <p><strong>Team Member Roles:</strong> {userSettings.teamRoles.join(', ')}</p>
          <p><strong>Priority Level:</strong> {userSettings.priorityLevel}</p>
          <p><strong>Level of Complexity:</strong> {userSettings.complexityLevel}</p>
          <p><strong>Target Outcome:</strong> {userSettings.targetOutcome.join(', ')}</p>
          <p><strong>Communication Style:</strong> {userSettings.communicationStyle}</p>
          <p><strong>Goal Timeframe:</strong> {userSettings.goalTimeframe}</p>
          <button onClick={toggleEdit}>Edit</button>
        </>
      ) : (
        <>
          <label>
            <strong>Role of User:</strong>
            <input type="text" value={userSettings.role.join(', ')} onChange={(e) => handleInputChange('role', e.target.value.split(', '))} />
          </label>
          <label>
            <strong>Business Objective:</strong>
            <input type="text" value={userSettings.businessObjective.join(', ')} onChange={(e) => handleInputChange('businessObjective', e.target.value.split(', '))} />
          </label>
          <label>
            <strong>Current Challenges:</strong>
            <input type="text" value={userSettings.challenges.join(', ')} onChange={(e) => handleInputChange('challenges', e.target.value.split(', '))} />
          </label>
          <label>
            <strong>Key Performance Indicators (KPIs):</strong>
            <input type="text" value={userSettings.kpis.join(', ')} onChange={(e) => handleInputChange('kpis', e.target.value.split(', '))} />
          </label>
          <label>
            <strong>Team Member Roles:</strong>
            <input type="text" value={userSettings.teamRoles.join(', ')} onChange={(e) => handleInputChange('teamRoles', e.target.value.split(', '))} />
          </label>
          <label>
            <strong>Priority Level:</strong>
            <select value={userSettings.priorityLevel} onChange={(e) => handleInputChange('priorityLevel', e.target.value)}>
              <option value="Urgent">Urgent</option>
              <option value="Normal">Normal</option>
              <option value="Low Priority">Low Priority</option>
            </select>
          </label>
          <label>
            <strong>Level of Complexity:</strong>
            <select value={userSettings.complexityLevel} onChange={(e) => handleInputChange('complexityLevel', e.target.value)}>
              <option value="Low">Low</option>
              <option value="Medium">Medium</option>
              <option value="High">High</option>
            </select>
          </label>
          <label>
            <strong>Target Outcome:</strong>
            <input type="text" value={userSettings.targetOutcome.join(', ')} onChange={(e) => handleInputChange('targetOutcome', e.target.value.split(', '))} />
          </label>
          <label>
            <strong>Communication Style:</strong>
            <select value={userSettings.communicationStyle} onChange={(e) => handleInputChange('communicationStyle', e.target.value)}>
              <option value="Formal">Formal</option>
              <option value="Casual">Casual</option>
              <option value="Concise">Concise</option>
            </select>
          </label>
          <label>
            <strong>Goal Timeframe:</strong>
            <select value={userSettings.goalTimeframe} onChange={(e) => handleInputChange('goalTimeframe', e.target.value)}>
              <option value="1 Month">1 Month</option>
              <option value="3 Months">3 Months</option>
            </select>
          </label>
          <button onClick={toggleEdit}>Save</button>
        </>
      )}
    </div>
  );
};

export default UserSettings;
