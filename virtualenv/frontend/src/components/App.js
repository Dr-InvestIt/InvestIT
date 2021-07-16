import React, { Component } from "react";
import { render } from "react-dom";
import HomePage from './HomePage';

export default class App extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return <div><HomePage></HomePage></div>;
    }
}

const appDiv = document.getElementById("app");
render(<App name="user"/>, appDiv);

// function App() {
//     return (
//         <div className="App">
//             <header className="App-header">
//                 <p>
//                     Stock
//                 </p>
//             </header>
//         </div>
//     );
// }

// export default App;