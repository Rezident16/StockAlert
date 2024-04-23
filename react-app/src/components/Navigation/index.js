import React, { useEffect } from "react";
import { NavLink } from "react-router-dom";
import { useSelector } from "react-redux";
import ProfileButton from "./ProfileButton";
import "./Navigation.css";
import LoginFormModal from "../LoginFormModal";
import SignupFormModal from "../SignupFormModal";
import OpenModalButton from "../OpenModalButton";
import { useDispatch } from "react-redux";

function Navigation({ isLoaded }) {
  const sessionUser = useSelector((state) => state.session.user);
  const dispatch = useDispatch();

  return (
    <div>Navigation</div>
  );
}

export default Navigation;
