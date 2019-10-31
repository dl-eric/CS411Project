import React, { Component } from "react";
import { Head } from "../components";
import { Button, Form, FormGroup, Input } from "reactstrap";

//import Router from "next/router";

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
      errorMessage: ""
    };
  }

  updateUsername = event => this.setState({ username: event.target.value });

  updatePassword = event => this.setState({ password: event.target.value });

  handleLogin = async () => {
    this.setState({ errorMessage: "" });

    const loginResponse = await login(this.state.username, this.state.password);

    if (loginResponse.status === 200) {
      //Router.push(`/friendPage/${loginResponse.id}`);
      console.log("successful log in");
    } else {
      console.log(loginResponse);
      let errorMessage = "";
      switch (loginResponse.status) {
        case 400:
          errorMessage = "Invalid log in request";
          break;
        case 401:
          errorMessage = "Incorrect password";
          break;
        case 404:
          errorMessage = "User not found";
          break;
        case 500:
          errorMessage = "Internal server error";
          break;
      }
      this.setState({ errorMessage });
    }
  };

  handlesignUp = async () => {
    this.setState({ errorMessage: "" });

    const signUpResponse = await signUp(
      this.state.username,
      this.state.password
    );

    if (signUpResponse.status === 200) {
      console.log("successful sign up");
      //Router.push(`/friendPage/${signUpSuccess.id}`);
    } else {
      let errorMessage = "";
      switch (signUpResponse.status) {
        case 400:
          errorMessage = "Invalid sign up request";
          break;
        case 409:
          errorMessage = "Username already taken";
          break;
        case 500:
          errorMessage = "Internal server error";
          break;
      }
      this.setState({ errorMessage });
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
          <Button onClick={this.handlesignUp}>Sign up</Button>
          <p>{this.state.errorMessage}</p>
        </Form>
      </div>
    );
  }
}
