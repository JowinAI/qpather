import React from 'react';
import { Drawer, List, ListItem, ListItemText, ListItemIcon, Toolbar, Typography } from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import GroupIcon from '@mui/icons-material/Group';
import SettingsIcon from '@mui/icons-material/Settings';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import OrgChartIcon from '@mui/icons-material/AccountTree';

const Sidebar = ({ setView }) => {
  return (
    <Drawer variant="permanent">
      <Toolbar>
        <Typography variant="h6" noWrap>
          App Name
        </Typography>
      </Toolbar>
      <List>
        <ListItem button onClick={() => setView('home')}>
          <ListItemIcon>
            <HomeIcon />
          </ListItemIcon>
          <ListItemText primary="Home" />
        </ListItem>
        <ListItem button onClick={() => setView('team')}>
          <ListItemIcon>
            <GroupIcon />
          </ListItemIcon>
          <ListItemText primary="Team Management" />
        </ListItem>
        <ListItem button onClick={() => setView('orgSettings')}>
          <ListItemIcon>
            <SettingsIcon />
          </ListItemIcon>
          <ListItemText primary="Org Settings" />
        </ListItem>
        <ListItem button onClick={() => setView('userSettings')}>
          <ListItemIcon>
            <AccountCircleIcon />
          </ListItemIcon>
          <ListItemText primary="User Settings" />
        </ListItem>
        <ListItem button onClick={() => setView('orgChart')}>
          <ListItemIcon>
            <OrgChartIcon />
          </ListItemIcon>
          <ListItemText primary="Org Chart" />
        </ListItem>
      </List>
    </Drawer>
  );
};

export default Sidebar;
