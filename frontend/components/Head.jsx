/**
 * @file A modular extension to Next's Head component.
 */

import React, { Component } from "react";
import NextHead from "next/head";

/**
 * Injects information into the <head> tag.
 */
export default class Head extends Component {
  /**
   * Renders the component.
   */
  render() {
    return (
      <NextHead>
        <meta charSet="UTF-8" />
        <meta
          name="description"
          content={this.props.description || "CS 411 Final Project"}
        />
        <meta name="keywords" content={this.props.keywords || ""} />
        <meta
          name="author"
          content="Alice Fang, Arpan Laha, Eric Lee, Hyunsoo Lee"
        />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <link
          rel="stylesheet"
          href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css"
          integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T"
          crossOrigin="anonymous"
        />
        <title>
          {`${
            this.props.title ? `${this.props.title} | ` : ""
          }CS 411 Final Project`}
        </title>
      </NextHead>
    );
  }
}
