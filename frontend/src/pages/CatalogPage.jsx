import { Link, useSearchParams } from 'react-router-dom';
import { hotels } from '../data/hotels';

function CatalogPage() {
  const [searchParams] = useSearchParams();
  const city = searchParams.get('city') || '';

  const filteredHotels = city
    ? hotels.filter((hotel) => hotel.city.toLowerCase().includes(city.toLowerCase()))
    : hotels;

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
          <input className="w-full border rounded-xl px-3 py-2 mt-1" placeholder="10000" />

          <label className="block mt-4 text-sm text-slate-600">Рейтинг от</label>
          <select className="w-full border rounded-xl px-3 py-2 mt-1">
            <option>4.0</option>
            <option>4.5</option>
            <option>4.8</option>
          </select>

          <button className="w-full mt-5 bg-slate-900 text-white rounded-xl py-2">
            Применить
          </button>
        </aside>

        <section className="space-y-5">
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
