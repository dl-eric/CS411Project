import React, { Component } from "react";
import { Head } from "../components";
import { Button, Form, FormGroup, Input, Container, Modal, ModalHeader, ModalBody, ModalFooter, Alert } from "reactstrap";

import Router from "next/router";

import { login, signUp } from "../utils/ApiWrapper";

import "../public/style.scss";

/**
 * The home page.
 */
export default class Login extends Component {
  constructor(props) {
    super(props);
    this.state = {
      username: "",
      password: "",
      confirmPassword: "",
      errorMessage: "",
      modal: false
    };
    this.toggle = this.toggle.bind(this)
    this.handleKeyPress = this.handleKeyPress.bind(this)
  }

  updateUsername = event => this.setState({ username: event.target.value });

  updatePassword = event => this.setState({ password: event.target.value });

  updateConfirmPassword = event => this.setState({ confirmPassword: event.target.value });

  handleLogin = async () => {
    this.setState({ errorMessage: "" });

    const loginResponse = await login(this.state.username, this.state.password);

    if (loginResponse.status === 200) {
      Router.push(`/dashboard/${loginResponse.data.result.userId}`);
    } else {
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

  handleSignUp = async () => {
    this.setState({ errorMessage: "" });

    if (this.state.password !== this.state.confirmPassword) {
      this.setState({ errorMessage: "Passwords do not match" })
      return;
    }

    const signUpResponse = await signUp(
      this.state.username,
      this.state.password
    );

    if (signUpResponse.status === 200) {
      Router.push(`/dashboard/${signUpResponse.data.result.userId}`);
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

  handleKeyPress = event => {
    if (event.key == "Enter") {
      this.state.modal ? this.handleSignUp() : this.handleLogin();
    }
  }

  toggle() {
    this.setState({ modal: !this.state.modal, errorMessage: "" })
  }

  /**
   * Renders the component.
   */
  render() {
    return (
      <div className="App" onKeyPress={this.handleKeyPress}>
        <Container fluid className="login-container">
          <Head />
          <h1 align="center">Login</h1>
          <Modal isOpen={this.state.modal}>
            <ModalHeader>Sign up</ModalHeader>
            <ModalBody>
              <Form onSubmit={this.handleSignUp}>
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
                <FormGroup>
                  <Input
                    type="password"
                    placeholder="confirm password"
                    onChange={this.updateConfirmPassword}
                  />
                </FormGroup>
              </Form>
            </ModalBody>
            <ModalFooter>
              <Button
                color="primary"
                className="login-btn"
                onClick={this.handleSignUp}
              >
                Submit
            </Button>
              <Button
                className="login-btn"
                onClick={this.toggle}
              >
                Close
            </Button>
              {this.state.errorMessage &&
                <Alert className='alert' color='danger'>{this.state.errorMessage}</Alert>
              }
            </ModalFooter>
          </Modal>
          <Form onSubmit={this.handleLogin}>
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

          </Form>
          <Button
            color="success"
            className="login-btn"
            onClick={this.handleLogin}
          >
            Log in
            </Button>
          <Button
            color="primary"
            className="login-btn"
            onClick={this.toggle}
          >
            Sign up
            </Button>
          {this.state.errorMessage &&
            <Alert className='alert' color='danger'>{this.state.errorMessage}</Alert>
          }
        </Container>
      </div >
    );
  }
}
