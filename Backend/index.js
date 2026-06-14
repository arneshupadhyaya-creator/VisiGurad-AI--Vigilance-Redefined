const express = require('express');// Import the Express library
const cors = require('cors');// Import the CORS middleware

const app = express();// Create an Express application

app.use(cors());// Use the CORS middleware
app.use(express.json());// Use the JSON middleware to parse JSON request bodies

const port = 3000; // Define the port number

app.get("/api/user",(req,res)=>{
    res.json({
        name: "John Doe",
        age: 30,
        email: "hello@gmail.com"
    });
});//defie the root url and send a reponse

app.listen(port, () => {
    console.log(`Server is running on port https://${port}`);
});// Start the server and listen on the defined port