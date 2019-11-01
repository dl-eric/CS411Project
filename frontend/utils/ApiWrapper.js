import axios from "axios";

const BACKEND_URL = "http://52.240.158.249:5000";

export const helloWorld = () =>
  axios
    .get(BACKEND_URL)
    .then(response => {
      console.log(response);
      return response.data;
    })
    .catch(error => {
      console.log(error);
      return null;
    });

export const login = (username, password) =>
  axios
    .post(`${BACKEND_URL}/login`, { username, password })
    .then(response => {
      console.log(response);
      return response;
    })
    .catch(error => {
      console.log(error);
      return error.response;
    });

export const signUp = (username, password) =>
  axios
    .post(`${BACKEND_URL}/signup`, { username, password })
    .then(response => {
      console.log(response);
      return response;
    })
    .catch(error => {
      console.log(error);
      return error.response;
    });

export const addFriend = friend =>
  axios
    .post(`${BACKEND_URL}/friends`, friend)
    .then(response => {
      console.log(response);
      return response;
    })
    .catch(error => {
      console.log(error);
      return error.response;
    });

export const getFriends = userId =>
  axios
    .get(`${BACKEND_URL}/friends?userId=${userId}`)
    .then(response => {
      console.log(response);
      return response.data.result.friends;
    })
    .catch(error => {
      console.log(error);
      return error.response;
    });

export const getFriend = friendId =>
  axios
    .get(`${BACKEND_URL}/friends/${friendId}`)
    .then(response => {
      console.log(response);
      return response.data.result;
    })
    .catch(error => {
      console.log(error);
      return error.response;
    });

export const changeFriendName = (friendId, friend) =>
  axios
    .put(`${BACKEND_URL}/friends/${friendId}`, friend)
    .then(response => {
      console.log(response);
      return response;
    })
    .catch(error => {
      console.log(error);
      return error.response;
    });

export const deleteFriend = friendId =>
  axios
    .delete(`${BACKEND_URL}/friends/${friendId}`)
    .then(response => {
      console.log(response);
      return response;
    })
    .catch(error => {
      console.log(error);
      return error.response;
    });

export const getSentiment = friendId =>
  axios
    .get(`${BACKEND_URL}/sentiments/${friendId}`)
    .then(response => {
      console.log(response);
      return response.data.result;
    })
    .catch(error => {
      console.log(error);
      return error.response;
    });

export const addSentiment = (friendId, sentiment) =>
  axios
    .post(`${BACKEND_URL}/sentiments/${friendId}`, sentiment)
    .then(response => {
      console.log(response);
      return response;
    })
    .catch(error => {
      console.log(error);
      return error.response;
    });

export const updateSentiment = (friendId, sentiment) =>
  axios
    .put(`${BACKEND_URL}/sentiments/${friendId}`, sentiment)
    .then(response => {
      console.log(response);
      return response;
    })
    .catch(error => {
      console.log(error);
      return error.response;
    });
