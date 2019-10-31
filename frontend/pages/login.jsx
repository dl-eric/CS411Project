/**
 * @file The home page.
 */

import React, { Component } from "react";
import { Head } from "../components";
import { Button, Form, FormGroup, Input } from "reactstrap";

import Router from "next/router";

import { login, register } from "../utils/ApiWrapper";

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
      failedRegister: false
    };
  }

  updateUsername = event => this.setState({ username: event.target.value });

  updatePassword = event => this.setState({ password: event.target.value });

  handleLogin = async () => {
    this.setState({ failedRegister: false });
    const loginSuccess = await login(this.state.username, this.state.password);
    if (loginSuccess !== null) {
      this.setState({ username: "", password: "", failedLogin: false });
      Router.push(`/friendsPage/${loginSuccess.id}`);
    } else {
      this.setState({ failedLogin: true });
    }
  };

  handleRegister = async () => {
    this.setState({ failedLogin: false });
    const registerSuccess = await register(
      this.state.username,
      this.state.password
    );
    if (registerSuccess !== null) {
      this.setState({ username: "", password: "", failedRegister: false });
      Router.push(`/friendsPage/${registerSuccess.id}`);
    } else {
      this.setState({ failedRegister: true });
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
          <Button onClick={this.handleRegister}>Register</Button>
          {this.state.failedLogin && <p>Log in attempt failed!</p>}
          {this.state.failedRegister && <p>Register attempt failed!</p>}
        </Form>
      </div>
    );
  }
}
