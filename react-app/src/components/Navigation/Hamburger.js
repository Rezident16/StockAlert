import OpenModalDiv from "./DivModal";
import React, { useState, useEffect, useRef } from "react";
import { useDispatch } from "react-redux";
import { logout } from "../../store/session";
import { useHistory } from "react-router-dom";

function UserHamburger({ userClass, user }) {
  const dispatch = useDispatch();
  const [showMenu, setShowMenu] = useState(false);
  const ulRef = useRef();
  const history = useHistory();

  const openMenu = async () => {
    if (showMenu) return;
    setShowMenu(true);
  };

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

  const handleLogout = (e) => {
    e.preventDefault();
    dispatch(logout());
    closeMenu();
    history.push("/");
  };

  const closeMenu = () => setShowMenu(false);
  const ulClassName = "profile-dropdown" + (showMenu ? "" : " hidden");

  return (
    <div className={userClass}>
      <button onClick={openMenu} id="hamburger">
        <i
          class="fa fa-bars"
          aria-hidden="true"
          style={{ fontSize: "30px", color: "black" }}
        />
      </button>
      <ul className={ulClassName} ref={ulRef}>
        <div>
          <li>{user?.username}</li>
          <li>
            {user?.first_name} {user?.last_name}
          </li>
          <li></li>
            <div >
              <li>
                My Profile
              </li>
            </div>
          <li >
            <div onClick={handleLogout}>
              Log Out
            </div>
          </li>
        </div>
      </ul>
    </div>
  );
}

export default UserHamburger;
