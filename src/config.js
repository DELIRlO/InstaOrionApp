const API_URL = import.meta.env.DEV
  ? "http://localhost:5000/api/instagram/download"
  : "https://instaorionapp.onrender.com/api/instagram/download";

export default API_URL;
