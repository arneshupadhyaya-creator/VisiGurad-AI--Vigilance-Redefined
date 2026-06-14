//import {Route,Routes} from 'react-router-dom';//for routing capabilities

//importing components
import Navbar from '../components/navbar.jsx';
import Hero from '../components/hero.jsx';
import Footer from '../components/footer.jsx';

//making an arrow function that returns the home page
const Home = () =>{
    return (//main container for the home page with bacground details and text color
        <div className="bg-zinc-900 min-h-screen flex flex-col">
            <Navbar />
            <Hero />
            <Footer />
        </div>
    );
}

export default Home;