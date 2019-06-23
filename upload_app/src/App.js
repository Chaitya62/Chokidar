import React from 'react';
import logo from './logo.svg';
import './App.css';


import { withAuthenticator } from 'aws-amplify-react'
import { Storage } from 'aws-amplify'


class App extends React.Component {
  state = {fileUrl: '', file: '', filename: ''}
  handleChange = e => {
    const file = e.target.files[0]
    this.setState({
      fileUrl: URL.createObjectURL(file),
      file,
      filename: file.name
    })
  }
  saveFile = () => {
    Storage.put(this.state.filename, this.state.file)
    .then(()=>{
      alert("Save success")
      this.setState({fileUrl: '', file: '', filename: ''})
     })
    .catch((err) => {
      console.log('Error', err)
    })
  }

  render(){
  return (
    <div className="App">
    <h2>Upload file for filtering words</h2>
     <input type="file" onChange={this.handleChange} />
      <button onClick={this.saveFile}>Save file</button>
    </div>
  );
}
}

export default withAuthenticator(App, { includeGreetings: true });
