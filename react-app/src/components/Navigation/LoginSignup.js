import OpenModalButton from "../OpenModalButton";
import LoginFormModal from "../LoginFormModal";
import Signup_main from "../SignupFormModal";
import { useHistory } from "react-router-dom";
import SignupFormModal from "../SignupFormModal/manual";


function LoginSignup({closeMenu}) {
  const history = useHistory()
  const redirect = () => {
    history.push('/signup')
    closeMenu()
  }
  return (
    <div className="login_signup_buttons">
LoginSignup
        </div>
  );
}

export default LoginSignup;
