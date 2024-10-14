import React, { useState } from 'react';

// Sample data structure for the organization
const initialOrgData = {
  id: 1,
  name: "CEO",
  children: [
    {
      id: 2,
      name: "VP of Operations",
      children: [
        { id: 3, name: "Operations Manager", children: [] },
      ],
    },
    {
      id: 4,
      name: "VP of Engineering",
      children: [
        { id: 5, name: "Engineering Manager", children: [] },
      ],
    },
  ],
};

// Recursive component to render organizational structure
const OrgNode = ({ node, addNode }) => {
  return (
    <div style={{ marginLeft: 20 }}>
      <div>
        {node.name}
        <button onClick={() => addNode(node.id)}>Add Subordinate</button>
      </div>
      {node.children.length > 0 && (
        <div style={{ marginLeft: 20 }}>
          {node.children.map((child) => (
            <OrgNode key={child.id} node={child} addNode={addNode} />
          ))}
        </div>
      )}
    </div>
  );
};

const OrgChart = () => {
  const [orgData, setOrgData] = useState(initialOrgData);

  // Function to add a new node (subordinate)
  const addNode = (parentId) => {
    const nodeName = prompt("Enter the name of the new subordinate");
    if (nodeName) {
      const newNode = {
        id: Date.now(),
        name: nodeName,
        children: [],
      };

      // Recursive function to add the new node at the correct position
      const addNodeRecursive = (node) => {
        if (node.id === parentId) {
          node.children.push(newNode);
        } else if (node.children.length > 0) {
          node.children.forEach(addNodeRecursive);
        }
      };

      // Update the organization data
      const updatedOrgData = { ...orgData };
      addNodeRecursive(updatedOrgData);
      setOrgData(updatedOrgData);
    }
  };

  return (
    <div>
      <h2>Organization Chart</h2>
      <OrgNode node={orgData} addNode={addNode} />
    </div>
  );
};

export default OrgChart;
