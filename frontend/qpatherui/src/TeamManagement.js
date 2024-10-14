import React, { useState } from 'react';

const TeamManagement = ({ teamMembers, setTeamMembers, setView }) => {
  const [newTeamMember, setNewTeamMember] = useState({ name: "", email: "", department: "", capabilities: "" });
  const departments = ["Finance", "Operations", "Technology", "Purchase"];

  const handleAddTeamMember = () => {
    setTeamMembers([...teamMembers, newTeamMember]);
    setNewTeamMember({ name: "", email: "", department: "", capabilities: "" });
  };

  return (
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
  );
};

export default TeamManagement;
