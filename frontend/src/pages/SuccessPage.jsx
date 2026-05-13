import { Link } from 'react-router-dom';
import usePageMeta from '../hooks/usePageMeta';

function SuccessPage() {
  usePageMeta(
    'HotelsWeb — бронирование оформлено',
    'Страница успешного оформления бронирования в веб-приложении HotelsWeb.'
  );
  return (
    <main className="max-w-3xl mx-auto px-4 py-20 text-center">
      <div className="bg-white rounded-3xl p-10 border shadow-sm">
        <h1 className="text-3xl font-bold">Бронирование успешно оформлено</h1>
        <p className="text-slate-600 mt-4">
          Информация о бронировании сохранена. Данные можно посмотреть в личном кабинете.
        </p>
        <Link to="/profile" className="inline-block mt-8 bg-blue-600 text-white rounded-xl px-6 py-3 font-semibold">
          Перейти в личный кабинет
        </Link>
      </div>
    </main>
  );
}

export default SuccessPage;
