import React, { Component } from "react";
import { Head } from "../../components";
import {
  CardHeader,
  Container,
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
  Label,
  CardFooter
} from "reactstrap";
import { getFriends, addFriend } from "../../utils/ApiWrapper";
import Router, { withRouter } from "next/router";

import "../../static/style.scss";

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
    const { pid } = this.props.router.query;
    this.setState({
      userId: pid
    });
    let friends = await getFriends(pid);
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
    let newFriend = {
      name: this.state.newFriend,
      userId: this.state.userId
    };
    await addFriend(newFriend);
    this.setState({
      modalOpen: false
    });
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
        <Head />
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
            <Button color="primary" onClick={this.createFriend}>
              Submit
            </Button>
          </ModalFooter>
        </Modal>
        <Button className="action-btn" color="primary" onClick={this.openModal}>
          Add New Friend
        </Button>
        <Button className="logout-btn" color="danger">Logout</Button>

        <Row>
          {this.state.friends.map(friend => (
            <Col md="3" key={friend.friendId}>
                <Card className='friend-card'>
                  <CardHeader><h3 align="center">{friend.name}</h3></CardHeader>
                  <CardFooter>
                    <Button className="detail-btn" onClick={() => Router.push(`/friend/${friend.friendId}`)}>Details</Button>
                  </CardFooter>
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
