import React, { useState } from "react";
import { login, demoLogin } from "../../store/session";
import { useDispatch } from "react-redux";
import { useModal } from "../../context/Modal";
import "./LoginForm.css";
import { useHistory } from "react-router-dom";
import google from "./google.png";
import { API_BASE_URL } from "../../config";
function LoginFormModal() {
  const dispatch = useDispatch();
  const { closeModal } = useModal();
  const [errors, setErrors] = useState([]);

  const handleDemoLogin = async () => {
    const data = await dispatch(demoLogin());
    if (data) {
      setErrors(data);
    } else {
      closeModal();
    }
  };

  return (
    <div className="google_image_container">
      <h2>Log In</h2>
      <a href={`${API_BASE_URL}/api/auth/oauth_login`}>
        <img src={google} alt="Google OAuth Login Button" id="google" />
      </a>
      {process.env.NODE_ENV !== "production" && (
        <>
          <button type="button" onClick={handleDemoLogin} className="demo_login_button">
            Continue as Demo
          </button>
          <ul>
            {errors.map((error, idx) => (
              <li key={idx}>{error}</li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}

export default LoginFormModal;
