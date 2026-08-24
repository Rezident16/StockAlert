import { NavLink } from "react-router-dom";
import { useSelector } from "react-redux";
import ProfileButton from "./ProfileButton";
import "./Navigation.css";
import logo from "./5002841.png";

function Navigation({ isLoaded }) {
  const sessionUser = useSelector((state) => state.session.user);

  return (
    <ul className="m-0 flex list-none items-center justify-between gap-5 border-b border-gray-300 bg-white px-4 py-3 shadow-sm sm:px-6">
      <li>
        <NavLink className="flex items-center gap-2 text-2xl text-black no-underline" exact to="/stocks">
          <img className="h-8 sm:h-10" src={logo} alt="StockAlert logo" />
          {sessionUser && (
            <span className="hidden text-lg font-semibold sm:inline sm:text-xl">
              StockAlert
            </span>
          )}
        </NavLink>
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
