import * as React from 'react';
import { styled, useTheme, Theme, CSSObject } from '@mui/material/styles';
import { Typography } from '@mui/material';

export default function Empty() {
    const theme = useTheme();
    // const [open, setOpen] = React.useState(false);


    return (
        <Typography sx={{ marginBottom: 2 }}>
        This page intentionally stay EMPTY
        </Typography>
    )

}