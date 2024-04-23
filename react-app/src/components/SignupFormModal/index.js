import React, { useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import { useModal } from "../../context/Modal";
import { signUp } from "../../store/session";
import "./SignupForm.css";
import SignupFormModal from "./manual";
function Signup_main() {

  const { closeModal } = useModal();

  return (
    <div className="form_container_signup">
      <h2>Create account</h2>
    </div>
  );
}

export default Signup_main;
