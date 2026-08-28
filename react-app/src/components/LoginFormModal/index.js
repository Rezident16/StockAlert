import { useState } from "react";
import { demoLogin } from "../../store/session";
import { useDispatch } from "react-redux";
import google from "./google.png";
import { API_BASE_URL } from "../../config";
import { useModal } from "../../context/Modal";

function LoginFormModal() {
  const dispatch = useDispatch();
  const { closeModal } = useModal();
  const [errors, setErrors] = useState([]);

  const handleDemoLogin = async () => {
    const data = await dispatch(demoLogin());
    if (data) {
      setErrors(data);
    } else {
      closeModal();
    }
  };

  return (
    <div className="fixed left-1/2 top-1/2 w-[90vw] max-w-sm -translate-x-1/2 -translate-y-1/2 rounded-xl bg-brand p-5 text-white shadow-lg sm:p-6">
      <h2 className="mb-5 text-center text-2xl font-semibold">Log In</h2>
      <a
        href={`${API_BASE_URL}/api/auth/oauth_login`}
        className="flex h-12 w-full items-center justify-center rounded-md"
      >
        <img src={google} alt="Log in with Google" className="h-full w-full object-contain" />
      </a>
      {process.env.NODE_ENV !== "production" && (
        <>
          <button
            type="button"
            onClick={handleDemoLogin}
            className="mt-4 h-10 w-full rounded-md border border-white bg-transparent text-sm text-white transition-colors hover:bg-white/10"
          >
            Continue as Demo
          </button>
          {errors.length > 0 && (
            <ul className="mt-2.5 list-none p-0 text-center text-sm text-red-300">
              {errors.map((error, idx) => (
                <li key={idx}>{error}</li>
              ))}
            </ul>
          )}
        </>
      )}
    </div>
  );
}

export default LoginFormModal;
