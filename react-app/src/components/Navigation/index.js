import React, { useEffect } from "react";
import { NavLink } from "react-router-dom";
import { useSelector } from "react-redux";
import ProfileButton from "./ProfileButton";
import "./Navigation.css";
import LoginFormModal from "../LoginFormModal";
import SignupFormModal from "../SignupFormModal";
import OpenModalButton from "../OpenModalButton";
import { useDispatch } from "react-redux";
import logo from './5002841.png';

function Navigation({ isLoaded }) {
  const sessionUser = useSelector((state) => state.session.user);
  const dispatch = useDispatch();
  

  return (
    <ul className="navigation">
      <li className="left_nav">
        {sessionUser ? (
          <NavLink className="left_nav" exact to="/stocks">
            <img
              className="logo"
              src={logo}
            />
            <div className="logo_text_parent">
              StockAlert
              </div>
          </NavLink>
        ) : (
          <NavLink className="left_nav" exact to="/stocks">
            <img
              className="logo"
              src={logo}
            />
            <div className="logo_text_parent">
              
            </div>
          </NavLink>
        )}
      </li>
      {isLoaded && (
        <li>
          <ProfileButton user={sessionUser} />
        </li>
      )}
    </ul>
  );
}

export default Navigation;
