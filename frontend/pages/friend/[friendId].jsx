import React, { Component } from "react";
import { Head } from "../../components";
import { Button, Container, Input } from "reactstrap";
import Dropzone from "react-dropzone";
import { withRouter } from "next/router";
import Unzipper from "unzipper";
import {
  getFriend,
  changeFriendName,
  getSentiment,
  sendFile
} from "../../utils/ApiWrapper";
import "../../public/style.scss";

class FriendDetailPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      friend: {},
      friendId: "",
      sentiment: {},
      isEditingName: false,
      newFile: ""
    };
  }

  async componentDidMount() {
    await this.getDataWrapper();
  }

  getDataWrapper = async () => {
    const { friendId } = this.props.router.query;
    console.log(friendId);
    this.setState({
      friendId
    });
    const friend = await getFriend(friendId);
    this.setState({
      friend
    });
  };

  onDrop = async files => {
    for (let file of files) {
      await sendFile(file, this.state.friend.userId, this.state.friendId);
    }
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

  getFriendSentiment = async () => {
    const response = await getSentiment(this.state.userId, this.state.friendId);
    const dir = await Unzipper.Open.buffer(response);
    console.log(dir);
  };

  render() {
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
          <Button onClick={this.getFriendSentiment}>getFriendSentiment</Button>
        </Container>
      </div>
    );
  }
}

export default withRouter(FriendDetailPage);
