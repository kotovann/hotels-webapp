import { Link } from 'react-router-dom';
import usePageMeta from '../hooks/usePageMeta';

function LoginPage() {
  usePageMeta(
    'HotelsWeb — вход в личный кабинет',
    'Страница входа пользователя в личный кабинет веб-приложения HotelsWeb.'
  );
  return (
    <main className="max-w-md mx-auto px-4 py-14">
      <h1 className="text-3xl font-bold">Вход</h1>
      <form className="bg-white rounded-2xl border p-6 mt-6 shadow-sm grid gap-4">
        <input className="border rounded-xl px-4 py-3" type="email" placeholder="Email" />
        <input className="border rounded-xl px-4 py-3" type="password" placeholder="Пароль" />
        <button type="button" className="bg-blue-600 text-white rounded-xl px-5 py-3 font-semibold">
          Войти
        </button>
        <p className="text-sm text-slate-600">
          Нет аккаунта? <Link to="/register" className="text-blue-600">Зарегистрироваться</Link>
        </p>
      </form>
    </main>
  );
}

export default LoginPage;
