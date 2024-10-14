import React from 'react';

const Sidebar = ({ setView }) => {
  const recentItems = ["Item 1", "Item 2", "Item 3"];

  return (
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
        <li onClick={() => setView("orgSettings")}>Org Settings</li> {/* Org Settings menu */}
        <li onClick={() => setView("userSettings")}>User Settings</li> {/* User Settings menu */}
        <li onClick={() => setView("orgChart")}>Org Chart</li> {/* New Org Chart menu */}
      </ul>
    </div>
  );
};

export default Sidebar;
