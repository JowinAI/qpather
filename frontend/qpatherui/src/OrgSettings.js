import React, { useState } from 'react';

const OrgSettings = () => {
  const [isEditing, setIsEditing] = useState(false);

  const [orgSettings, setOrgSettings] = useState({
    businessSector: 'Technology',
    companySize: 'Medium',
    teamStructure: ['Engineering', 'Marketing'],
    geographicFocus: ['North America', 'APAC'],
    historicalData: 'No data uploaded',
  });

  // Handle edit toggle
  const toggleEdit = () => {
    setIsEditing(!isEditing);
  };

  // Handle input change (in edit mode)
  const handleInputChange = (field, value) => {
    setOrgSettings({
      ...orgSettings,
      [field]: value,
    });
  };

  return (
    <div className="org-settings">
      <h3>Org Settings</h3>
      {!isEditing ? (
        <>
          <p><strong>Business Sector:</strong> {orgSettings.businessSector}</p>
          <p><strong>Company Size:</strong> {orgSettings.companySize}</p>
          <p><strong>Team Structure:</strong> {orgSettings.teamStructure.join(', ')}</p>
          <p><strong>Geographic Focus:</strong> {orgSettings.geographicFocus.join(', ')}</p>
          <p><strong>Historical Data:</strong> {orgSettings.historicalData}</p>
          <button onClick={toggleEdit}>Edit</button>
        </>
      ) : (
        <>
          <label>
            <strong>Business Sector:</strong>
            <select value={orgSettings.businessSector} onChange={(e) => handleInputChange('businessSector', e.target.value)}>
              <option value="Technology">Technology</option>
              <option value="Finance">Finance</option>
              <option value="Healthcare">Healthcare</option>
            </select>
          </label>
          <label>
            <strong>Company Size:</strong>
            <select value={orgSettings.companySize} onChange={(e) => handleInputChange('companySize', e.target.value)}>
              <option value="Small">Small</option>
              <option value="Medium">Medium</option>
              <option value="Large">Large</option>
            </select>
          </label>
          <label>
            <strong>Team Structure:</strong>
            <input type="text" value={orgSettings.teamStructure.join(', ')} onChange={(e) => handleInputChange('teamStructure', e.target.value.split(', '))} />
          </label>
          <label>
            <strong>Geographic Focus:</strong>
            <input type="text" value={orgSettings.geographicFocus.join(', ')} onChange={(e) => handleInputChange('geographicFocus', e.target.value.split(', '))} />
          </label>
          <label>
            <strong>Historical Data:</strong>
            <input type="text" value={orgSettings.historicalData} onChange={(e) => handleInputChange('historicalData', e.target.value)} />
          </label>
          <button onClick={toggleEdit}>Save</button>
        </>
      )}
    </div>
  );
};

export default OrgSettings;
