import { Link } from 'react-router-dom';

function Header() {
  return (
    <header className="bg-white border-b border-slate-200">
      <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        <Link to="/" className="text-2xl font-bold text-slate-900" aria-label="Перейти на главную страницу HotelsWeb">
          HotelsWeb
        </Link>

        <nav className="flex gap-5 text-sm font-medium text-slate-700" aria-label="Основная навигация">
          <Link to="/catalog" className="hover:text-blue-600">Каталог</Link>
          <Link to="/profile" className="hover:text-blue-600">Личный кабинет</Link>
          <Link to="/login" className="hover:text-blue-600">Войти</Link>
        </nav>
      </div>
    </header>
  );
}

export default Header;
