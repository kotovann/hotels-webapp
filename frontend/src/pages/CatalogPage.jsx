import { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { hotels } from '../data/hotels';
import usePageMeta from '../hooks/usePageMeta';

const ratingOptions = [
  { label: 'Любой', value: '0' },
  { label: '4.0+', value: '4.0' },
  { label: '4.5+', value: '4.5' },
  { label: '4.8+', value: '4.8' },
];

function CatalogPage() {
  usePageMeta(
    'HotelsWeb — каталог гостиниц',
    'Каталог гостиниц HotelsWeb с карточками отелей, фильтрацией по цене и рейтингу, а также переходом к подробной информации.'
  );

  const [searchParams] = useSearchParams();
  const city = searchParams.get('city') || '';

  const [maxPrice, setMaxPrice] = useState('');
  const [minRating, setMinRating] = useState('0');

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
    <main className="max-w-6xl mx-auto px-4 py-8 md:py-10">
      <h1 className="text-3xl font-bold">Каталог гостиниц</h1>
      <p className="text-slate-600 mt-2">
        Выберите гостиницу из доступных вариантов и перейдите к просмотру номеров.
      </p>

      {city && (
        <p className="text-slate-600 mt-3">
          Показаны результаты по городу: <span className="font-semibold">{city}</span>
        </p>
      )}

      <div className="grid lg:grid-cols-[260px_1fr] gap-6 lg:gap-8 mt-8">
        <aside
          className="bg-white rounded-2xl p-5 border shadow-sm h-fit"
          aria-label="Фильтры каталога гостиниц"
        >
          <h2 className="font-semibold text-lg">Фильтры</h2>

          <label className="block mt-4">
            <span className="text-sm text-slate-600">Цена до</span>
            <input
              className="w-full border rounded-xl px-3 py-2 mt-1"
              type="number"
              min="0"
              placeholder="10000"
              value={maxPrice}
              onChange={(event) => setMaxPrice(event.target.value)}
            />
          </label>

          <fieldset className="mt-4">
            <legend className="text-sm text-slate-600">Рейтинг</legend>
            <div className="grid grid-cols-2 gap-2 mt-2">
              {ratingOptions.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  className={`rounded-xl px-3 py-2 text-sm font-semibold border ${
                    minRating === option.value
                      ? 'bg-blue-600 text-white border-blue-600'
                      : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
                  }`}
                  onClick={() => setMinRating(option.value)}
                  aria-pressed={minRating === option.value}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </fieldset>

          <button
            type="button"
            className="w-full mt-5 bg-slate-900 text-white rounded-xl py-2 font-semibold hover:bg-slate-800"
            onClick={() => {
              setMaxPrice('');
              setMinRating('0');
            }}
          >
            Сбросить фильтры
          </button>
        </aside>

        <section className="space-y-5" aria-labelledby="catalog-results-title">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
            <h2 id="catalog-results-title" className="text-xl font-bold">
              Найденные гостиницы
            </h2>
            <p className="text-slate-500">
              Количество вариантов: {filteredHotels.length}
            </p>
          </div>

          {filteredHotels.length === 0 && (
            <div className="bg-white rounded-2xl border p-6 text-slate-600">
              По выбранным параметрам гостиницы не найдены. Попробуйте изменить фильтры.
            </div>
          )}

          {filteredHotels.map((hotel) => (
            <article
              key={hotel.id}
              className="bg-white rounded-2xl overflow-hidden border shadow-sm grid lg:grid-cols-[260px_1fr]"
            >
              <img
                src={hotel.image}
                alt={`Фотография гостиницы ${hotel.name}`}
                className="h-56 sm:h-64 lg:h-full w-full object-cover"
              />

              <div className="p-5 md:p-6">
                <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
                  <div>
                    <h3 className="text-2xl font-bold">{hotel.name}</h3>
                    <p className="text-slate-500 mt-1">{hotel.city}</p>
                  </div>
                  <span className="font-semibold text-blue-600 bg-blue-50 rounded-full px-3 py-1 w-fit">
                    ★ {hotel.rating}
                  </span>
                </div>

                <p className="text-slate-600 mt-4">{hotel.description}</p>

                <div className="flex flex-wrap gap-2 mt-4" aria-label={`Удобства гостиницы ${hotel.name}`}>
                  {hotel.amenities.map((item) => (
                    <span key={item} className="text-sm bg-slate-100 rounded-full px-3 py-1">
                      {item}
                    </span>
                  ))}
                </div>

                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mt-6">
                  <p className="font-bold">от {hotel.priceFrom} ₽ / ночь</p>
                  <Link
                    to={`/hotels/${hotel.id}`}
                    className="bg-blue-600 text-white rounded-xl px-5 py-3 font-semibold hover:bg-blue-700 text-center"
                    aria-label={`Подробнее о гостинице ${hotel.name}`}
                  >
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
