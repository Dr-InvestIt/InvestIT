import React, { Component } from "react";
import { render } from "react-dom";
import HomePage from './HomePage';

export default class App extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return <div>
            <select>
                <option value ="Volatility">Volatility</option>
                <option value="Efficient">Efficient Frontier</option>
                <option selected value="select">Choose the graph</option>
            </select>
            <HomePage></HomePage>
            <p>Hello { this.props.name }</p>
        </div>;
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