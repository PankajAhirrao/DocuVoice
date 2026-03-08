// Login.jsx
import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FileText, ArrowLeft, Loader2 } from 'lucide-react';
import './Login.css';
import axios from 'axios';

const Login = () => {
  const apiUrl = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/").replace(/\/?$/, "/");
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  
  // Simulate toast functionality without external dependency
  const toast = ({ title, description, variant }) => {
    console.log(`${title}: ${description} ${variant ? `(${variant})` : ''}`);
    // You could implement a custom toast component here if needed
  };

  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);
  

const handleSubmit = async (e) => {
  e.preventDefault();

  if (!username || !password) {
    toast({
      title: "Error",
      description: "Please fill in all fields",
      variant: "destructive",
    });
    return;
  }

  setIsLoading(true);

  try {
    // 🔥 SEND JSON (NOT FormData)
    const response = await axios.post(`${apiUrl}users/login/`, {
      username: username,
      password: password,
    });

    // 🔥 VALIDATE TOKEN
    if (!response.data?.token) {
      throw new Error("Invalid credentials");
    }

    // 🔥 SAVE TOKEN CORRECTLY
    localStorage.setItem("authToken", response.data.token);
    localStorage.setItem("user", JSON.stringify(response.data.user));

    toast({
      title: "Success",
      description: "You have successfully logged in.",
    });

    // Navigate to main dashboard (root route)
    navigate("/");
  } catch (error) {
    toast({
      title: "Login Failed",
      description:
        error.response?.data?.error || error.message || "Something went wrong",
      variant: "destructive",
    });
  } finally {
    setIsLoading(false);
  }
};


  // const handleSubmit = async (e) => {
  //   e.preventDefault();
    
  //   if (!username || !password) {
  //     toast({
  //       title: "Error",
  //       description: "Please fill in all fields",
  //       variant: "destructive"
  //     });
  //     return;
  //   }
  
  //   setIsLoading(true);
  
  //   try {
  //     const formData = new FormData();
  //     formData.append("username", username);
  //     formData.append("password", password);
      
  //     const response = await axios.post(apiUrl + "users/login/", formData);
      
  //     if (!response.data.token) {
  //       throw new Error(response.data.error || "Invalid credentials");
  //     }
  
  //     localStorage.setItem("authToken", response.data.token);
  //     localStorage.setItem("user", JSON.stringify(response.data.user));
  
  //     setTimeout(() => {
  //       setIsLoading(false);
  //       toast({
  //         title: "Success",
  //         description: "You have successfully logged in.",
  //       });
  //       navigate("/dashboard");
  //     }, 1500);
  //   } catch (error) {
  //     setIsLoading(false);
  //     toast({
  //       title: "Login Failed",
  //       description: error.response?.data?.error || error.message,
  //       variant: "destructive",
  //     });
  //   }
  // };
  

  return (
    <div className="login-page">
      <div className="login-container">
        <Link to="/" className="back-link">
          <ArrowLeft size={16} className="back-arrow" />
          <span>Back to Home</span>
        </Link>
        
        <div className="login-wrapper">
          <div className="login-form">
            <div className="logo-section">
              <Link to="/" className="logo-link">
                <div className="logo-icon">
                  <FileText size={20} />
                </div>
                <span className="logo-text">LegiFy</span>
              </Link>
            </div>
            
            <div className="card">
              <div className="card-header">
                <h2 className="card-title">Sign in</h2>
                <p className="card-description">
                  Enter your username and password to access your account
                </p>
              </div>
              
              <div className="card-content">
                <form onSubmit={handleSubmit} className="form">
                  <div className="form-group">
                    <label htmlFor="username">Username</label>
                    <input 
                      id="email" 
                      type="text" 
                      placeholder="name@example.com" 
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      autoComplete="name"
                      required
                    />
                  </div>
                  
                  <div className="form-group">
                    <div className="password-header">
                      <label htmlFor="password">Password</label>
                      <Link to="/forgot-password" className="forgot-password">
                        Forgot password?
                      </Link>
                    </div>
                    <input 
                      id="password" 
                      type="password" 
                      placeholder="••••••••" 
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      autoComplete="current-password"
                      required
                    />
                  </div>
                  
                  <div className="checkbox-group">
                    <input
                      type="checkbox"
                      id="remember"
                      checked={rememberMe}
                      onChange={(e) => setRememberMe(e.target.checked)}
                    />
                    <label htmlFor="remember">Remember me</label>
                  </div>
                  
                  <button 
                    type="submit" 
                    className="submit-btn"
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <span className="loading">
                        <Loader2 size={16} className="spinner" />
                        Signing in...
                      </span>
                    ) : "Sign in"}
                  </button>
                </form>
                
                <div className="signup-link">
                  <p>
                    Don't have an account?{" "}
                    <Link to="/register" className="signup">
                      Sign up
                    </Link>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
