/**
 * @file The home page.
 */

import React, { Component } from "react";
import { Head } from "../components";
import Router from "next/router";

import "../public/style.scss";

export default class App extends Component {
  componentDidMount() {
    Router.push("/login");
  }

  /**
   * Renders the component.
   */
  render() {
    return (
      <div className="App">
        <Head />
        <p>Hello World!</p>
      </div>
    );
  }
}
