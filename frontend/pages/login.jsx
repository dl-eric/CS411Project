import React, { Component } from "react";
import { Head } from "../components";
import { Button, Form, FormGroup, Input } from "reactstrap";

import Router from "next/router";

import { login, signUp } from "../utils/ApiWrapper";

import "../static/style.scss";

/**
 * The home page.
 */
export default class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      username: "",
      password: "",
      failedLogin: false,
      faileSignUp: false
    };
  }

  updateUsername = event => this.setState({ username: event.target.value });

  updatePassword = event => this.setState({ password: event.target.value });

  handleLogin = async () => {
    this.setState({ faileSignUp: false });
    const loginSuccess = await login(this.state.username, this.state.password);
    if (loginSuccess !== null) {
      this.setState({ username: "", password: "", failedLogin: false });
      Router.push(`/friendPage/${loginSuccess.id}`);
    } else {
      this.setState({ failedLogin: true });
    }
  };

  handlesignUp = async () => {
    this.setState({ failedLogin: false });
    const signUpSuccess = await signUp(
      this.state.username,
      this.state.password
    );
    if (signUpSuccess !== null) {
      this.setState({ username: "", password: "", faileSignUp: false });
      Router.push(`/friendPage/${signUpSuccess.id}`);
    } else {
      this.setState({ faileSignUp: true });
    }
  };

  /**
   * Renders the component.
   */
  render() {
    return (
      <div className="App">
        <Head />
        <Form>
          <FormGroup>
            <Input placeholder="username" onChange={this.updateUsername} />
          </FormGroup>
          <FormGroup>
            <Input
              type="password"
              placeholder="password"
              onChange={this.updatePassword}
            />
          </FormGroup>
          <Button onClick={this.handleLogin}>Log in</Button>
          <Button onClick={this.handlesignUp}>signUp</Button>
          {this.state.failedLogin && <p>Log in attempt failed!</p>}
          {this.state.faileSignUp && <p>Sign up attempt failed!</p>}
        </Form>
      </div>
    );
  }
}
