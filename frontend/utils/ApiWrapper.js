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
      console.log("failed");
      return null;
    });
