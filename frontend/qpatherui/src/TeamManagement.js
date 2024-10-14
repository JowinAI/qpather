import React, { useState, useEffect } from 'react';
import axios from 'axios';

const TeamManagement = ({ setView }) => {
  const [teamMembers, setTeamMembers] = useState([]); // Stores all team members
  const [newTeamMember, setNewTeamMember] = useState({ name: "", email: "", department: "", capabilities: "" }); // Stores new team member input
  const [changes, setChanges] = useState({ added: [], updated: [], deleted: [] }); // Tracks changes (additions, updates, deletions)
  const departments = ["Finance", "Operations", "Technology", "Purchase"]; // Predefined departments

  // Fetch team members from API when the component mounts
  useEffect(() => {
    const fetchTeamMembers = async () => {
      try {
        const response = await axios.get('/team/get');
        setTeamMembers(response.data);
      } catch (error) {
        console.error('Error fetching team members:', error);
      }
    };
    fetchTeamMembers();
  }, []);

  // Handle adding a new team member
  const handleAddTeamMember = () => {
    if (!newTeamMember.name || !newTeamMember.email || !newTeamMember.department) {
      alert('Please fill in all fields.');
      return;
    }

    const newMember = { ...newTeamMember, id: Date.now() }; // Assign a temporary ID for new members
    setTeamMembers([...teamMembers, newMember]);
    setChanges({ ...changes, added: [...changes.added, newMember] }); // Track as added
    setNewTeamMember({ name: "", email: "", department: "", capabilities: "" }); // Reset input fields
  };

  // Handle deleting a team member
  const handleDeleteTeamMember = (id) => {
    setTeamMembers(teamMembers.filter((member) => member.id !== id)); // Remove from the list
    if (changes.added.some((member) => member.id === id)) {
      // If the deleted member was just added, remove from added list
      setChanges({
        ...changes,
        added: changes.added.filter((member) => member.id !== id),
      });
    } else {
      // Otherwise, track as deleted
      setChanges({
        ...changes,
        deleted: [...changes.deleted, { id }],
      });
    }
  };

  // Handle editing team members
  const handleEditTeamMember = (id, field, value) => {
    const updatedTeam = teamMembers.map((member) =>
      member.id === id ? { ...member, [field]: value } : member
    );
    setTeamMembers(updatedTeam);

    // Track as updated (if it is not newly added)
    if (!changes.added.some((member) => member.id === id)) {
      setChanges({
        ...changes,
        updated: updatedTeam.filter((member) => member.id === id),
      });
    }
  };

  // Handle saving changes to the server (added, updated, and deleted members)
  const handleSave = async () => {
    try {
      const response = await axios.post('/team/save', changes);
      console.log('Changes saved:', response.data);
      // Reset changes after successful save
      setChanges({ added: [], updated: [], deleted: [] });
    } catch (error) {
      console.error('Error saving team members:', error);
    }
  };

  return (
    <div className="team-management">
      <h3>Team Management</h3>

      {/* Input form for adding a new team member */}
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

      {/* List of team members with edit and delete options */}
      <h3>Team Members</h3>
      <ul>
        {teamMembers.map((member) => (
          <li key={member.id}>
            <input
              type="text"
              value={member.name}
              onChange={(e) => handleEditTeamMember(member.id, 'name', e.target.value)}
            />
            <input
              type="email"
              value={member.email}
              onChange={(e) => handleEditTeamMember(member.id, 'email', e.target.value)}
            />
            <select
              value={member.department}
              onChange={(e) => handleEditTeamMember(member.id, 'department', e.target.value)}
            >
              {departments.map((dept, index) => (
                <option key={index} value={dept}>
                  {dept}
                </option>
              ))}
            </select>
            <input
              type="text"
              value={member.capabilities}
              onChange={(e) => handleEditTeamMember(member.id, 'capabilities', e.target.value)}
            />
            <button onClick={() => handleDeleteTeamMember(member.id)}>Delete</button>
          </li>
        ))}
      </ul>

      {/* Save button (only show if there are changes) */}
      {(changes.added.length > 0 || changes.updated.length > 0 || changes.deleted.length > 0) && (
        <button onClick={handleSave}>Save</button>
      )}

      {/* Back button (navigates to the home view) */}
      <button onClick={() => setView('home')}>Back</button>
    </div>
  );
};

export default TeamManagement;
