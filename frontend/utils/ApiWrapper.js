import axios from "axios";

const BACKEND_URL = "http://52.240.158.249:5000/";

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
  username === password ? { id: 1 } : null;

export const register = (username, password) =>
  username !== "username" && username === password ? { id: 2 } : null;

export const getFriends = userID => [
  { name: "Alice", id: `${userID}1` },
  { name: "Arpan", id: `${userID}2` },
  { name: "Hyunsoo", id: `${userID}3` },
  { name: "Eric", id: `${userID}4` }
];

export const addFriend = (name, userID) => ({
  id: 5,
  name: name,
  userID: userID
});

export const getSentiments = id => [
  { id: id, sentiment: "happy" },
  { id: id, sentiment: "sad" }
];

export const editFriend = (id, name) => ({
  id: id,
  name: name
});

export const addSentiment = (id, sentiment) => ({
  id: id,
  sentiment: sentiment
});

export const deleteSentiment = (id, sentiment) =>
  [{ id: id, sentiment: "happy" }, { id: id, sentiment: "sad" }].filter(
    entry => entry.id !== id && entry.sentiment !== sentiment
  );
