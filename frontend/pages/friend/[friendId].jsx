import React, { Component } from "react";
import { Head } from "../../components";
import { Button, Container, Input } from "reactstrap";
import Dropzone from "react-dropzone";
import { withRouter } from "next/router";
import { getFriend, changeFriendName } from "../../utils/ApiWrapper";

class FriendDetailPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      friend: {},
      isEditingName: false,
      sentiment: "Happy",
      files: "File1"
    };
  }

  async componentDidMount() {
    await this.getFriendWrapper();
  }

  getFriendWrapper = async () => {
    const { friendId } = this.props.router.query;
    console.log(friendId);
    this.setState({
      friendId
    });
    let friend = await getFriend(friendId);
    console.log(friend);
    this.setState({
      friend
    });
  };

  onDrop = files => {
    this.setState({
      sentiment: files[0].name
    });
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
    await this.getFriendWrapper();
    this.cancelEditName();
  };

  cancelEditName = () => {
    this.setState({
      isEditingName: false
    });
  };

  render() {
    return (
      <div className="app">
        <Container fluid>
          <Head />
          <h1 align="center">{this.state.friend.name}</h1>
          <Button color="primary" onClick={this.editName}>
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
          <h4>Sentiment: {this.state.sentiment}</h4>
          <h4>Files: {this.state.files}</h4>
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
        </Container>
      </div>
    );
  }
}

export default withRouter(FriendDetailPage);
