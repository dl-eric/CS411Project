import React, { Component } from "react";
import { Head } from "../../components";
import { Button, Container, Input } from "reactstrap";
import Dropzone from "react-dropzone";
import { withRouter } from "next/router";
import {
  getFriend,
  changeFriendName,
  sendFile,
  getFiles,
  getTimeStamp
} from "../../utils/ApiWrapper";
import "../../public/style.scss";
import { getPageFiles } from "next/dist/next-server/server/get-page-files";

class FriendDetailPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      friend: {},
      friendId: "",
      fileTimes: [],
      isEditingName: false,
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
    const fileIds = await getFiles(this.state.friend.userId, this.state.friendId)
    let timestamps = []
    for (const fileId of fileIds.files) {
      const timestamp = await getTimeStamp(fileId)
      timestamps.push(timestamp.timestamp)
    }
    this.setState({
      fileTimes: timestamps
    })
  };

  onDrop = async files => {
    let timestamps = this.state.fileTimes
    for (let file of files) {
      const res = await sendFile(file, this.state.friend.userId, this.state.friendId)
      const timestamp = res.response.data.result.timestamp
      timestamps.push(timestamp)
    }
    this.setState({
      fileTimes: timestamps
    })
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
              <li>{fileTime}</li>
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
        </Container>
      </div>
    );
  }
}

export default withRouter(FriendDetailPage);
