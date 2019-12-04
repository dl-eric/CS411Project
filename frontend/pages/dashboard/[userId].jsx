import React, { Component } from "react";
import { Head } from "../../components";
import {
  Container,
  Button,
  Row,
  Col,
  Card,
  Modal,
  ModalBody,
  ModalFooter,
  Form,
  Input,
  FormGroup,
  Label,
  CardBody
} from "reactstrap";
import { getFriends, addFriend, deleteFriend } from "../../utils/ApiWrapper";

import Router, { withRouter } from "next/router";

import "../../public/style.scss";

class FriendPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      friends: [],
      modalOpen: false,
      userId: 0
    };
  }

  async componentDidMount() {
    await this.getFriendsWrapper();
  }

  getFriendsWrapper = async () => {
    const { userId } = this.props.router.query;
    this.setState({
      userId
    });
    let friends = await getFriends(userId);
    this.setState({
      friends
    });
  };

  openModal = () => {
    this.setState({
      modalOpen: true
    });
  };

  closeModal = () => {
    this.setState({
      modalOpen: false
    });
  };

  createFriend = async () => {
    const newFriend = {
      name: this.state.newFriend,
      userId: this.state.userId
    };

    await addFriend(newFriend);
    this.setState({
      modalOpen: false
    });
    await this.getFriendsWrapper();
  };

  removeFriend = async friendId => {
    await deleteFriend(friendId);
    await this.getFriendsWrapper();
  };

  handleChange = e => {
    this.setState({
      [e.target.name]: e.target.value
    });
  };

  render() {
    return (
      <div className="app">
        <Container fluid>
          <Head title="Dashboard" />
          <h1 align="center">Your Chatrooms</h1>
          <Modal isOpen={this.state.modalOpen}>
            <ModalBody>
              <Form>
                <FormGroup>
                  <Label>Name</Label>
                  <Input
                    name="newFriend"
                    placeholder="Enter Name"
                    onChange={this.handleChange}
                    onKeyPress={this.handleKeyPress}
                  />
                </FormGroup>
              </Form>
            </ModalBody>
            <ModalFooter>
              <Button color="secondary" onClick={this.closeModal}>
                Cancel
              </Button>
              <Button color="primary" onClick={this.createFriend}>
                Submit
              </Button>
            </ModalFooter>
          </Modal>
          <Button
            className="action-btn"
            color="primary"
            onClick={this.openModal}
          >
            Add New Chatroom
          </Button>
          <Button className="logout-btn" color="danger" onClick={() => Router.push('/login')}>
            Logout
          </Button>

          <Row>
            {this.state.friends.map(friend => (
              <Col md="3" key={friend.friendId}>
                <Card className="friend-card">
                  <CardBody>
                    <h3 align="center">{friend.name}</h3>
                    <div className='card-btns'>
                      <Button
                        className="detail-btn"
                        color="secondary"
                        onClick={() => Router.push(`/friend/${friend.friendId}`)}
                      >
                        Details
                      </Button>
                      <Button
                        className="detail-btn"
                        color="danger"
                        onClick={() => {
                          this.removeFriend(friend.friendId);
                        }}
                      >
                      Delete
                    </Button>
                    </div>
                    </CardBody>
                </Card>
              </Col>
            ))}
          </Row>
        </Container>
      </div>
    );
  }
}

export default withRouter(FriendPage);
