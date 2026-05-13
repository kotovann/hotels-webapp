import { Link } from 'react-router-dom';
import usePageMeta from '../hooks/usePageMeta';

function RegisterPage() {
  usePageMeta(
    'HotelsWeb — регистрация пользователя',
    'Страница регистрации пользователя в веб-приложении HotelsWeb для дальнейшего оформления и просмотра бронирований.'
  );
  return (
    <main className="max-w-md mx-auto px-4 py-14">
      <h1 className="text-3xl font-bold">Регистрация</h1>
      <form className="bg-white rounded-2xl border p-6 mt-6 shadow-sm grid gap-4">
        <input className="border rounded-xl px-4 py-3" placeholder="Имя" />
        <input className="border rounded-xl px-4 py-3" placeholder="Фамилия" />
        <input className="border rounded-xl px-4 py-3" type="email" placeholder="Email" />
        <input className="border rounded-xl px-4 py-3" type="password" placeholder="Пароль" />
        <button type="button" className="bg-blue-600 text-white rounded-xl px-5 py-3 font-semibold">
          Создать аккаунт
        </button>
        <p className="text-sm text-slate-600">
          Уже есть аккаунт? <Link to="/login" className="text-blue-600">Войти</Link>
        </p>
      </form>
    </main>
  );
}

export default RegisterPage;
