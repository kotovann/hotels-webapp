import { useNavigate, useParams } from 'react-router-dom';
import { hotels } from '../data/hotels';

function BookingPage() {
  const navigate = useNavigate();
  const { hotelId, roomId } = useParams();

  const hotel = hotels.find((item) => item.id === Number(hotelId));
  const room = hotel?.rooms.find((item) => item.id === Number(roomId));

  const handleSubmit = (event) => {
    event.preventDefault();
    navigate('/success');
  };

  if (!hotel || !room) {
    return <main className="max-w-6xl mx-auto px-4 py-10">Данные бронирования не найдены</main>;
  }

  return (
    <main className="max-w-4xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold">Оформление бронирования</h1>

      <div className="bg-white rounded-2xl border p-6 mt-6 shadow-sm">
        <h2 className="text-xl font-bold">{hotel.name}</h2>
        <p className="text-slate-600 mt-1">{room.title}</p>
        <p className="font-bold mt-3">{room.price} ₽ / ночь</p>
      </div>

      <form onSubmit={handleSubmit} className="bg-white rounded-2xl border p-6 mt-6 shadow-sm grid gap-4">
        <input className="border rounded-xl px-4 py-3" placeholder="Имя" required />
        <input className="border rounded-xl px-4 py-3" placeholder="Фамилия" required />
        <input className="border rounded-xl px-4 py-3" type="email" placeholder="Email" required />
        <input className="border rounded-xl px-4 py-3" type="tel" placeholder="Телефон" required />

        <div className="grid md:grid-cols-2 gap-4">
          <input className="border rounded-xl px-4 py-3" type="date" required />
          <input className="border rounded-xl px-4 py-3" type="date" required />
        </div>

        <button className="bg-blue-600 text-white rounded-xl px-5 py-3 font-semibold hover:bg-blue-700">
          Подтвердить бронирование
        </button>
      </form>
    </main>
  );
}

export default BookingPage;
