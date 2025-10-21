body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: url("https://images.unsplash.com/photo-1581092588429-9b6f8d69e51e?auto=format&fit=crop&w=1400&q=80") 
              no-repeat center center fixed;
  background-size: cover;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  margin: 0;
}

/* Overlay for readability */
body::before {
  content: "";
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  z-index: -1;
}

/* Form container */
.container {
  background-color: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(8px);
  padding: 30px 40px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.3);
  width: 320px;
  text-align: center;
}

h1 {
  color: #f1f1f1;
  margin-bottom: 20px;
  font-weight: 600;
}

label {
  display: block;
  text-align: left;
  margin-bottom: 5px;
  font-weight: 500;
  color: #e0e0e0;
}

input[type="text"],
input[type="password"] {
  width: 100%;
  padding: 10px;
  margin-bottom: 15px;
  border: none;
  border-radius: 6px;
  background-color: rgba(255,255,255,0.9);
  font-size: 14px;
}

button {
  width: 100%;
  padding: 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 15px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

button:hover {
  background-color: #0056b3;
}

a {
  color: #00aaff;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

p {
  margin: 10px 0;
  color: #f1f1f1;
}

.error {
  color: #ff7070;
  font-weight: bold;
}
