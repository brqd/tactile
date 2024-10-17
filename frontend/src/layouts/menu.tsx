import * as React from 'react';
import { styled, useTheme, Theme, CSSObject } from '@mui/material/styles';
import Divider from '@mui/material/Divider';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import InboxIcon from '@mui/icons-material/MoveToInbox';
import MailIcon from '@mui/icons-material/Mail';
import { Link } from 'react-router-dom';

interface MenuProps{
    open: boolean
}



export default function Menu({open}: MenuProps) {
  return (
    <>
      <List>
      {['Inbox', 'Starred', 'Send email', 'Drafts'].map((text, index) => (
          <ListItem key={text} disablePadding sx={{ display: 'block' }}>
          <ListItemButton
              sx={[
              {
                  minHeight: 48,
                  px: 2.5,
              },
              open
                  ? {
                      justifyContent: 'initial',
                  }
                  : {
                      justifyContent: 'center',
                  },
              ]}
          >
              <ListItemIcon
              sx={[
                  {
                  minWidth: 0,
                  justifyContent: 'center',
                  },
                  open
                  ? {
                      mr: 3,
                      }
                  : {
                      mr: 'auto',
                      },
              ]}
              >
              {index % 2 === 0 ? <InboxIcon /> : <MailIcon />}
              </ListItemIcon>
              <ListItemText
              primary={text}
              sx={[
                  open
                  ? {
                      opacity: 1,
                      }
                  : {
                      opacity: 0,
                      },
              ]}
              />
          </ListItemButton>
          </ListItem>
      ))}
      </List>
      <Divider />
      <List>
      {['All mail', 'Trash', 'Spam'].map((text, index) => (
          <ListItem key={text} disablePadding sx={{ display: 'block' }}>
          <ListItemButton
              component={Link}
              to='lorem'
              sx={[
              {
                  minHeight: 48,
                  px: 2.5,
              },
              open
                  ? {
                      justifyContent: 'initial',
                  }
                  : {
                      justifyContent: 'center',
                  },
              ]}
          >
              <ListItemIcon
              sx={[
                  {
                  minWidth: 0,
                  justifyContent: 'center',
                  },
                  open
                  ? {
                      mr: 3,
                      }
                  : {
                      mr: 'auto',
                      },
              ]}
              >              
              {index % 2 === 0 ? <InboxIcon /> : <MailIcon />}
              </ListItemIcon>
              <ListItemText
              primary={text}
              sx={[
                  open
                  ? {
                      opacity: 1,
                      }
                  : {
                      opacity: 0,
                      },
              ]}
              />
          </ListItemButton>
          </ListItem>
      ))}
      </List>        
    </>
  )

}