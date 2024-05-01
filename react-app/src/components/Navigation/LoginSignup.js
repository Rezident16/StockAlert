import OpenModalButton from "../OpenModalButton";
import LoginFormModal from "../LoginFormModal";
import { useHistory } from "react-router-dom";


function LoginSignup({closeMenu}) {
  const history = useHistory()
  const redirect = () => {
    history.push('/signup')
    closeMenu()
  }
  return (
    <div className="login_signup_buttons">
          <OpenModalButton
            className={"navigation_buttons"}
            buttonText="Log In"
            onItemClick={closeMenu}
            modalComponent={<LoginFormModal />}
          />
        </div>
  );
}

export default LoginSignup;
