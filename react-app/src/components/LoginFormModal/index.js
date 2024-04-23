import React, { useState } from "react";
import { login } from "../../store/session";
import { useDispatch } from "react-redux";
import { useModal } from "../../context/Modal";
import "./LoginForm.css";
import { useHistory } from "react-router-dom";

function LoginFormModal() {

  return (
    <div className="form_container_login">
      Login Form Modal
    </div>
  );
}

export default LoginFormModal;
