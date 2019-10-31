import React, { Component } from "react";
import { Head } from "../components";
import { 
    Button, 
    Container, 
    Input
 } from 'reactstrap'
import Dropzone from 'react-dropzone'

class FriendPage extends Component {
    constructor(props) {
      super(props)
      this.state = {
        name: 'Alice',
        isEditingName: false,
        sentiment: 'Happy',
        files: 'File1',
      }
    }

    onDrop = (files) => {
        this.setState({
            sentiment: files[0].name
        })
    }

    handleChange = e => {
        this.setState({
          [e.target.name]: e.target.value,
        })
    }

    editName = () => {
        this.setState({
            isEditingName: true
        })
    }

    changeName = () => {
        this.setState({
            name: this.state.newName,
            isEditingName: false
        })
    }

    cancelEditName = () => {
        this.setState({
            isEditingName: false
        })
    }

    render() {
        return (
            <div className='app'>
                <Container fluid>
                <Head/>
                <h1 align='center'>{this.state.name}</h1>
                <Button color='primary' onClick={this.editName}>Edit Name</Button>
                {this.state.isEditingName && 
                    <>
                        <Input name='newName' label="New Name" onChange={this.handleChange}/>
                        <Button onClick={this.changeName}>Submit</Button>
                        <Button onClick={this.cancelEditName}>Cancel</Button>
                    </>
                }
                <h4>Sentiment: {this.state.sentiment}</h4>
                <h4>Files: {this.state.files}</h4>
                <h4>Upload File</h4>
                <Dropzone onDrop={this.onDrop}>
                    {({getRootProps, getInputProps}) => (
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
        )
    }
}

export default FriendPage
