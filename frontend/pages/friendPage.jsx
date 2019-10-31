import React, { Component } from "react";
import {
  Button,
  Row,
  Col,
  Card,
  CardBody,
  CardTitle,
  Modal,
  ModalBody,
  ModalFooter,
  Form,
  Input,
  FormGroup,
  Label
} from "reactstrap";
import { getFriends } from "../utils/ApiWrapper";
import { withRouter } from "next/router";

class FriendPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      friends: [],
      modalOpen: false
    };
  }

  async componentDidMount() {
    const { pid } = this.props.router.query;
    await this.getFriendsWrapper({ pid });
  }

  getFriendsWrapper = async id => {
    let friends = getFriends(id);
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

  addFriend = () => {
    let friendsArr = this.state.friends;
    friendsArr.push(this.state.newFriend);
    this.setState({
      friends: friendsArr
    });
  };

  handleChange = e => {
    this.setState({
      [e.target.name]: e.target.value
    });
  };

  render() {
    return (
      <div className="app">
        <h1 align="center">Your Friends</h1>
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
            <Button color="primary" onClick={this.addFriend}>
              Submit
            </Button>
          </ModalFooter>
        </Modal>
        <Button color="primary" onClick={this.openModal}>
          Add New Friend
        </Button>
        <Button color="secondary">Logout</Button>

        <Row>
          {this.state.friends.map(friend => (
            <Col md="4" key={friend.id}>
              <Card>
                <CardBody>
                  <CardTitle>{friend.name}</CardTitle>
                </CardBody>
              </Card>
            </Col>
          ))}
        </Row>
      </div>
    );
  }
}

export default withRouter(FriendPage);
