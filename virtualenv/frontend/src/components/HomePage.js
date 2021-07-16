import React, { Component } from "react";
import { render } from "react-dom";
import { BrowserRouter as Router, Switch, Route, Link, Redirect } from "react-router-dom";

export default class HomePage extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <Router>
                <Switch>
                    <Route exact path='/'>
                        <h1>This is the home page</h1>
                    </Route>
                    <Route path='/stocks'>
                        <h1>This is the stocks page</h1>
                    </Route>
                </Switch>
            </Router>
        )
    }
}