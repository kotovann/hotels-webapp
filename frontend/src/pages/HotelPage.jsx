import { Link, useParams } from 'react-router-dom';
import { hotels } from '../data/hotels';

function HotelPage() {
  const { id } = useParams();
  const hotel = hotels.find((item) => item.id === Number(id));

  if (!hotel) {
    return <main className="max-w-6xl mx-auto px-4 py-10">Гостиница не найдена</main>;
  }

  return (
    <main className="max-w-6xl mx-auto px-4 py-10">
      <img src={hotel.image} alt={hotel.name} className="w-full h-96 object-cover rounded-3xl" />

      <div className="mt-8 grid md:grid-cols-[1fr_320px] gap-8">
        <section>
          <h1 className="text-4xl font-bold">{hotel.name}</h1>
          <p className="text-slate-500 mt-2">{hotel.city} · ★ {hotel.rating}</p>
          <p className="text-slate-700 mt-5 leading-7">{hotel.description}</p>

          <h2 className="text-2xl font-bold mt-8">Удобства</h2>
          <div className="flex flex-wrap gap-2 mt-4">
            {hotel.amenities.map((item) => (
              <span key={item} className="bg-slate-100 rounded-full px-4 py-2">{item}</span>
            ))}
          </div>

          <h2 className="text-2xl font-bold mt-8">Доступные номера</h2>
          <div className="space-y-4 mt-4">
            {hotel.rooms.map((room) => (
              <div key={room.id} className="bg-white border rounded-2xl p-5 flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold">{room.title}</h3>
                  <p className="text-slate-500">До {room.capacity} гостей</p>
                </div>
                <div className="text-right">
                  <p className="font-bold">{room.price} ₽ / ночь</p>
                  <Link to={`/booking/${hotel.id}/${room.id}`} className="inline-block mt-3 bg-blue-600 text-white rounded-xl px-4 py-2">
                    Забронировать
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </section>

        <aside className="bg-white rounded-2xl border p-6 h-fit shadow-sm">
          <h2 className="text-xl font-bold">Краткая информация</h2>
          <p className="mt-4 text-slate-600">Стоимость от</p>
          <p className="text-2xl font-bold">{hotel.priceFrom} ₽ / ночь</p>
          <p className="mt-4 text-slate-600">Рейтинг: ★ {hotel.rating}</p>
        </aside>
      </div>
    </main>
  );
}

export default HotelPage;
