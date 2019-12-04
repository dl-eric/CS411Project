import React, { Component } from "react";
import { Head } from "../../components";
import { Button, Container, Input } from "reactstrap";
import Dropzone from "react-dropzone";
import { withRouter } from "next/router";
import ReactWordcloud from "react-wordcloud";
import {
  getFriend,
  changeFriendName,
  sendFile,
  getFiles,
  getSentiment
} from "../../utils/ApiWrapper";
import "../../public/style.scss";
import { Resizable } from "re-resizable";

class FriendDetailPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      friend: {},
      friendId: "",
      fileTimes: [],
      isEditingName: false,
      counts: null,
      person: null,
      sentiment: null
    };
  }

  async componentDidMount() {
    await this.getDataWrapper();
  }

  getDataWrapper = async () => {
    const { friendId } = this.props.router.query;
    this.setState({
      friendId
    });
    const friend = await getFriend(friendId);
    this.setState({
      friend
    });
    const timestamps = await getFiles(this.state.friend.userId, this.state.friendId)
    this.setState({
      fileTimes: timestamps
    })
    const response = await getSentiment(
      this.state.friend.userId,
      this.state.friendId
    );
    const { counts } = response;
    this.setState({
      counts
    });
  };

  onDrop = async files => {
    let timestamps = this.state.fileTimes
    for (let file of files) {
      const res = await sendFile(
        file,
        this.state.friend.userId,
        this.state.friendId
      );
      const timestamp = res.response.data.result.timestamp;
      timestamps.push(timestamp);
    }
    this.setState({
      fileTimes: timestamps
    });
    await this.getDataWrapper();
  };

  handleChange = e => {
    this.setState({
      [e.target.name]: e.target.value
    });
  };

  editName = () => {
    this.setState({
      isEditingName: true
    });
  };

  changeName = async () => {
    const newFriend = {
      name: this.state.newName
    };
    await changeFriendName(this.state.friend.friendId, newFriend);
    await this.getDataWrapper();
    this.cancelEditName();
  };

  cancelEditName = () => {
    this.setState({
      isEditingName: false
    });
  };

  render() {
    const resizeStyle = {
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      border: "solid 1px #ddd",
      background: "#f0f0f0"
    };
    return (
      <div className="app">
        <Container fluid>
          <Head title={this.state.friend.name} />
          <h1 align="center">{this.state.friend.name}</h1>
          <Button
            className="action-btn"
            color="primary"
            onClick={this.editName}
          >
            Edit Name
          </Button>
          {this.state.isEditingName && (
            <>
              <Input
                name="newName"
                label="New Name"
                onChange={this.handleChange}
              />
              <Button onClick={this.changeName}>Submit</Button>
              <Button onClick={this.cancelEditName}>Cancel</Button>
            </>
          )}
          <h4>Uploaded Files:</h4>
          <ul>
            {this.state.fileTimes.map(fileTime => (
              <li key={fileTime._id}>{fileTime}</li>
            ))}
          </ul>
          <h4>Upload File</h4>
          <Dropzone onDrop={this.onDrop}>
            {({ getRootProps, getInputProps }) => (
              <section>
                <div {...getRootProps()}>
                  <input {...getInputProps()} />
                  <p>Drag 'n' drop some files here, or click to select files</p>
                </div>
              </section>
            )}
          </Dropzone>

          {this.state.counts &&
            Object.keys(this.state.counts).map(person => (
              <>
                <Button
                  onClick={() =>
                    this.setState({ person, sentiment: "Positive" })
                  }
                >
                  {person} - Positive
                </Button>
                <Button
                  onClick={() =>
                    this.setState({ person, sentiment: "Negative" })
                  }
                >
                  {person} - Negative
                </Button>
              </>
            ))}
          {this.state.person && (
            <>
              <h3>
                {this.state.person} - {this.state.sentiment}
                <Resizable style={resizeStyle}>
                  <ReactWordcloud
                    words={
                      this.state.counts[this.state.person][
                        this.state.sentiment === "Positive" ? "pos" : "neg"
                      ]
                    }
                  />
                </Resizable>
              </h3>
            </>
          )}
        </Container>
      </div>
    );
  }
}

export default withRouter(FriendDetailPage);
