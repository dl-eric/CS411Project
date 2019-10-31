/**
 * @file The home page.
 */

import React, { Component } from "react";
import { Head } from "../components";
import { bindActionCreators } from "redux";
import { connect } from "react-redux";
import { setExample } from "../redux/actions";
import Router from "next/router";

import { helloWorld } from "../utils/ApiWrapper";

// import "../static/style.scss";

/**
 * Fetches Redux state and assigns it to props.
 * @param state the Redux state.
 * @returns the fetched state props.
 */
const mapStateToProps = state => ({
  example: state.example
});

/**
 * Fetchs Redux actions and assigns them to props.
 * @param dispatch the Redux dispatch.
 * @returns the fetched action props.
 */
const mapDispatchToProps = dispatch =>
  bindActionCreators({ setExample }, dispatch);

/**
 * The home page.
 */
export default connect(
  mapStateToProps,
  mapDispatchToProps
)(
  class App extends Component {
    constructor(props) {
      super(props);
      this.state = {
        newExample: this.props.example,
        message: null,
        hello: null
      };
    }

    async componentDidMount() {
      Router.push("/login");
      const hello = await helloWorld();
      console.log("hello: ", hello);
      if (hello) {
        this.setState({ hello: hello });
      }
    }

    /**
     * Called when the input text changes.
     * Sets this.state.newExample to the inputted text.
     */
    updateExample = event => {
      this.setState({ newExample: event.target.value });
    };

    /**
     * Called when the submit button is clicked.
     * Passes in the current value of this.state.newExample to this.props.setExample.
     */
    handleSubmit = () => this.props.setExample(this.state.newExample);

    /**
     * An example function for loading data.
     */
    loadMessage = async () => {
      /**
       * A helper method for sleeping for a designated length of time time.
       * @param ms the milliseconds to sleep for.
       */
      function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
      }
      const timeOut = 2000;
      await sleep(timeOut);
      this.setState({ message: "Loaded!" });
    };

    /**
     * Renders the component.
     */
    render() {
      return (
        <div className="App">
          <Head />
          {this.state.hello}
        </div>
      );
    }
  }
);
