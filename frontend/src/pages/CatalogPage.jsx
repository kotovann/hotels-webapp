import { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { hotels } from '../data/hotels';
import usePageMeta from '../hooks/usePageMeta';

function CatalogPage() {
  usePageMeta(
    'HotelsWeb — каталог гостиниц',
    'Каталог гостиниц HotelsWeb с карточками отелей, фильтрацией по цене и рейтингу, а также переходом к подробной информации.'
  );
  const [searchParams] = useSearchParams();
  const city = searchParams.get('city') || '';

  const [maxPrice, setMaxPrice] = useState('');
  const [minRating, setMinRating] = useState('4.0');

  const filteredHotels = hotels.filter((hotel) => {
    const matchesCity = city
      ? hotel.city.toLowerCase().includes(city.toLowerCase())
      : true;

    const matchesPrice = maxPrice
      ? hotel.priceFrom <= Number(maxPrice)
      : true;

    const matchesRating = hotel.rating >= Number(minRating);

    return matchesCity && matchesPrice && matchesRating;
  });

  return (
    <main className="max-w-6xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold">Каталог гостиниц</h1>
      <p className="text-slate-600 mt-2">
        Выберите гостиницу из доступных вариантов и перейдите к просмотру номеров.
      </p>

      <div className="grid md:grid-cols-[260px_1fr] gap-8 mt-8">
        <aside className="bg-white rounded-2xl p-5 border shadow-sm h-fit">
          <h2 className="font-semibold text-lg">Фильтры</h2>

          <label className="block mt-4 text-sm text-slate-600">Цена до</label>
          <input
            className="w-full border rounded-xl px-3 py-2 mt-1"
            placeholder="10000"
            value={maxPrice}
            onChange={(event) => setMaxPrice(event.target.value)}
          />

          <label className="block mt-4 text-sm text-slate-600">Рейтинг от</label>
          <select
            className="w-full border rounded-xl px-3 py-2 mt-1"
            value={minRating}
            onChange={(event) => setMinRating(event.target.value)}
          >
            <option value="4.0">4.0</option>
            <option value="4.5">4.5</option>
            <option value="4.8">4.8</option>
          </select>

          <button
            type="button"
            className="w-full mt-5 bg-slate-900 text-white rounded-xl py-2"
            onClick={() => {
              setMaxPrice('');
              setMinRating('4.0');
            }}
          >
            Сбросить
          </button>
        </aside>

        <section className="space-y-5">
          {filteredHotels.length === 0 && (
            <div className="bg-white rounded-2xl border p-6 text-slate-600">
              По выбранным параметрам гостиницы не найдены.
            </div>
          )}

          {filteredHotels.map((hotel) => (
            <article key={hotel.id} className="bg-white rounded-2xl overflow-hidden border shadow-sm grid md:grid-cols-[260px_1fr]">
              <img src={hotel.image} alt={hotel.name} className="h-60 md:h-full w-full object-cover" />
              <div className="p-6">
                <div className="flex justify-between gap-4">
                  <div>
                    <h2 className="text-2xl font-bold">{hotel.name}</h2>
                    <p className="text-slate-500 mt-1">{hotel.city}</p>
                  </div>
                  <span className="font-semibold text-blue-600">★ {hotel.rating}</span>
                </div>
                <p className="text-slate-600 mt-4">{hotel.description}</p>
                <div className="flex flex-wrap gap-2 mt-4">
                  {hotel.amenities.map((item) => (
                    <span key={item} className="text-sm bg-slate-100 rounded-full px-3 py-1">{item}</span>
                  ))}
                </div>
                <div className="flex items-center justify-between mt-6">
                  <p className="font-bold">от {hotel.priceFrom} ₽ / ночь</p>
                  <Link to={`/hotels/${hotel.id}`} className="bg-blue-600 text-white rounded-xl px-5 py-3 font-semibold hover:bg-blue-700">
                    Подробнее
                  </Link>
                </div>
              </div>
            </article>
          ))}
        </section>
      </div>
    </main>
  );
}

export default CatalogPage;
