import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { hotels } from '../data/hotels';

function HomePage() {
  const navigate = useNavigate();
  const [city, setCity] = useState('');

  const handleSearch = (event) => {
    event.preventDefault();
    navigate(`/catalog?city=${encodeURIComponent(city)}`);
  };

  return (
    <main>
      <section className="bg-slate-900 text-white">
        <div className="max-w-6xl mx-auto px-4 py-20">
          <h1 className="text-4xl md:text-5xl font-bold max-w-3xl">
            Бронирование гостиниц в удобном веб-приложении
          </h1>
          <p className="mt-5 text-lg text-slate-200 max-w-2xl">
            Найдите подходящую гостиницу, выберите номер и оформите бронирование за несколько шагов.
          </p>

          <form onSubmit={handleSearch} className="mt-10 bg-white text-slate-900 rounded-2xl p-4 grid md:grid-cols-5 gap-3 shadow-lg">
            <input
              className="border rounded-xl px-4 py-3 md:col-span-2"
              placeholder="Город"
              value={city}
              onChange={(event) => setCity(event.target.value)}
            />
            <input className="border rounded-xl px-4 py-3" type="date" />
            <input className="border rounded-xl px-4 py-3" type="date" />
            <button className="bg-blue-600 text-white rounded-xl px-5 py-3 font-semibold hover:bg-blue-700">
              Найти
            </button>
          </form>
        </div>
      </section>

      <section className="max-w-6xl mx-auto px-4 py-12">
        <h2 className="text-2xl font-bold">Популярные гостиницы</h2>
        <div className="grid md:grid-cols-3 gap-6 mt-6">
          {hotels.map((hotel) => (
            <article key={hotel.id} className="bg-white rounded-2xl overflow-hidden shadow-sm border">
              <img src={hotel.image} alt={hotel.name} className="h-48 w-full object-cover" />
              <div className="p-5">
                <h3 className="text-xl font-semibold">{hotel.name}</h3>
                <p className="text-slate-500 mt-1">{hotel.city}</p>
                <p className="mt-3 font-semibold">от {hotel.priceFrom} ₽ / ночь</p>
              </div>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}

export default HomePage;
