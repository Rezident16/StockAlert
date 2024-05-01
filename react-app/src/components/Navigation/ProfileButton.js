import React, { useState, useEffect, useRef } from "react";
import { useSelector } from "react-redux";
import OpenModalButton from "../OpenModalButton";
import LoginSignup from "./LoginSignup";
import UserHamburger from "./Hamburger";

function ProfileButton({ user }) {
  const [showMenu, setShowMenu] = useState(false);
  const [isUser, setIsUser] = useState(false);
  const ulRef = useRef();

  useEffect(() => {
    if (!showMenu) return;

    const closeMenu = (e) => {
      if (!ulRef.current.contains(e.target)) {
        setShowMenu(false);
      }
    };

    document.addEventListener("click", closeMenu);

    return () => document.removeEventListener("click", closeMenu);
  }, [showMenu]);

  const closeMenu = () => setShowMenu(false);
  return (
    <div id="nav-buttons">

      {!user ? (
        <LoginSignup closeMenu={closeMenu} />
        ): (
          <UserHamburger user={user} />
      )}
    </div>
  );
}

export default ProfileButton;
