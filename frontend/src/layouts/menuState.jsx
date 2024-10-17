import { useState, createContext, useMemo } from 'react';

const MenuStateContext = createContext(); 

console.log('recreted')

const MenuStateProvider = (props) => {

  const [open, setOpen] = useState(false);
  const value = useMemo(() => ({open, setOpen}), [open])

	return (
			<MenuStateContext.Provider
					value={value}
			>
					{props.children}
			</MenuStateContext.Provider>
	);
}

export { MenuStateContext, MenuStateProvider };