import React, { useState } from "react";
import { login } from "../../store/session";
import { useDispatch } from "react-redux";
import { useModal } from "../../context/Modal";
import "./LoginForm.css";
import { useHistory } from "react-router-dom";
import google from "./google.png";
function LoginFormModal() {
  const baseUrl =
    process.env.NODE_ENV === "production" ? "" : "http://localhost:5000";

  return (
    <div className="google_image_container">
      <h2>Log In</h2>
      <a href={`${baseUrl}/api/auth/oauth_login`}>
        <img src={google} alt="Google OAuth Login Button" id="google" />
      </a>
    </div>
  );
}

export default LoginFormModal;
