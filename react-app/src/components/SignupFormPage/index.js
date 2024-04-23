import React, { useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import { useModal } from "../../context/Modal";
import { signUp } from "../../store/session";
import "./SignupForm.css";
import Signup_form from "./manualSignUp";
import './SignupForm.css'
function Signup_main() {

  const { closeModal } = useModal();

  return (
    <div className="form_container_signup">
      SignUp
    </div>
  );
}

export default Signup_main;
